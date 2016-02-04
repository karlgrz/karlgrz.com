+++
author = "karlgrz"
comments = true
date = "2013-09-24T17:26:00"
slug = "testing-salt-states-rapidly-with-docker"
title = "Testing Salt States Rapidly with Docker"
categories = ["Coding"]
tags = ["salt", "2013", "docker"]
+++

At [Mediafly](http://www.mediafly.com) we have been using [Puppet](https://github.com/puppetlabs/puppet) for a lot of our configuration management. While it does the job, it's a little opinionated and a little more complex than I'd like.

I've been using [Salt](http://github.com/saltstack/salt/) a lot lately outside of work and I love the simplicity. I'll save my opinions for another post, but I guess if I'm writing about it that means I enjoy using it, right?

In conjunction with that, we've also been experimenting a lot with [Docker](http://docker.io). I'm learning that I wish Docker was around a long, long time ago (or that I discovered [LXC](http://lxc.sourceforge.net/) a long time ago).

I just wanted to share how I've been using Docker to rapidly test Salt states (and I presume you could do the same for puppet or [Chef](https://github.com/opscode/chef)).

Before Docker, when I wanted to test a system state (using shell scripts, puppet, or even just manual statements) I would spin up a base [ubuntu server](http://www.ubuntu.com/download/server) image in [AWS](http://aws.amazon.com) and have to wait for it to get going, which takes a long time (~2-3 minutes). Soon I'd grow tired of this and moved on to just using VMs in [VirtualBox](https://www.virtualbox.org/) on my dev machine. While this helped out in the time of spinning up a new instance in a fresh state, it would still take up a lot more time than I'd like (as close to instant as possible).

With Docker, the feedback cycle shortens to near instantaneous. Here's how I do it. Note that I'm not advocating this as the best way by any means, this is just the simple approach that works very well for me.

Let's get a few assumptions out of the way. I will assume that you have Docker running properly in your environment. If you do not, [this](http://www.docker.io/gettingstarted/) is the best way to get started.

Also, if you wish to persist changes to the Docker images you make, you should set up an account [here](http://index.docker.io) so you can push and pull your images easily.

The best way to get Salt onto a fresh machine is with [salt-bootstrap](http://github.com/saltstack/salt-bootstrap). As such, you should clone this repo in your dev environment somewhere that your Docker container can access it (I'll explain later). You'll also need the Salt states you'll be running (if you are just getting started you can clone [this](http://github.com/saltstack/salt-states), which are some very good examples to get started).

Now, let's get started with a fresh ubuntu image. We're going to use 12.04 (at the time of writing) which is the default Docker ubuntu image. First, start the Docker daemon:

```
sudo docker -d
```

Next, let's run the following command, which will attempt to connect to the base ubuntu image from [index.docker.io](http://index.docker.io) - since this is the first time it is running, Docker will download the image to your dev environment:

```
sudo docker run -i -t ubuntu /bin/bash
```

Once this all downloads, you should be at a bash shell prompt, with a vanilla ubuntu 12.04 install, as the root user.

Now, for Salt testing, we want this container to have access to our code in our Salt repository, wherever that may be. To do this, let's create the folder /srv/salt inside our Docker container:

```
mkdir -p /srv/salt
```

Salt by default looks for states inside /srv/salt, so we'll use this for our testing.

Now, we want to *commit* the change we just made, so that the /srv/salt directory persists in our Docker image.

In *another terminal*, run the following command to get the list of running Docker containers:

```
sudo docker ps
```

This will come back with something like this:

```
karl@karl-VirtualBox:~$ sudo docker ps
[sudo] password for karl:
ID                  IMAGE                              COMMAND             CREATED             STATUS              PORTS
93963124836e        ubuntu:latest   /bin/bash           15 seconds ago      Up 15 seconds
```

Now, to commit the changes, run this, replacing the ID you see in your environment:

```
sudo docker commit 93963124836e karlgrz/salt-base
```

Ok, couple things here. *karlgrz/salt-base* is just a name for an image I want to push up to [index.docker.io](index.docker.io) and takes the form of username/image-name. This could be whatever you want if you are not pushing to a repository, I just like to follow that practice. If you did want to push it to [index.docker.io](index.docker.io), you just issue the following command:

```
sudo docker push karlgrz/salt-base
```

Now you have an image that is base ubuntu, plus a folder at /srv/salt. Now, let's make another directory, which is where that salt-bootstrap repo will be mounted, inside our Docker container:

```
mkdir -p /srv/salt-bootstrap
```

Again, commit the change:

```
sudo docker commit 93963124836e karlgrz/salt-base
```

Now we have the following folder structure in our Docker container:

```
- srv
    - salt
    - salt-bootstrap
```

In the shell, hit Ctrl+D to exit and disconnect from the Docker container.

Now we want to mount our Salt states repo and the salt-bootstrap repo INSIDE that Docker container (because we shouldn't need to do any editing of source code inside there, leave that for your comfortable dev environment).

Start the Docker container like this to do that (replacing your local paths as necessary):

```
sudo docker run -i -v /home/karl/workspace/salt-bootstrap:/srv/salt-bootstrap -v /home/karl/workspace/salt-states:/srv/salt -t karlgrz/salt-base /bin/bash
```

Ok, now if you cd in to /srv/salt in our Docker container, you will see all the code from /home/karl/workspace/salt-states, and /srv/salt-bootstrap contains the salt-bootstrap stuff.

That's it! Now run the following command from /srv inside the Docker container:

```
salt-call --local state.highstate
```

And that will run salt locally, using the states in /srv/salt. You can view the output like you would on a normal machine, but now, when you stop and re-start the Docker container, you're at a fresh state. No need to wait for an AWS instance or a VM to spin up. This makes that feedback cycle SO MUCH FASTER!

Obviously, you aren't limited to just Salt or Puppet or Chef testing here. Docker presents new ways to control deployments and infrastructure partitioning that have been eye opening to me, and I think I've only begun to scratch the surface.
