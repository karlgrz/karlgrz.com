+++
author = "karlgrz"
comments = true
date = "2012-10-24T23:10:00"
slug = "rabbitmq-highly-available-queues-and-clustering-using-amazon-ec2"
title = "RabbitMQ Highly Available Queues and Clustering Using Amazon EC2"
category = ["Coding"]
tags = ["rabbitmq", "aws", "distributed", "highly available", "clustering"]
+++

Using [RabbitMQ](http://www.rabbitmq.com) on Amazon EC2 is an easy, performant way to operate a service oriented application. It's pretty trivial to set up and once you do, you can usually forget about it and go about your day.

Until Amazon has an EC2 outage. And your bus goes down. And you don't have a plan for getting back up quickly. Fail. Fail. Fail.

Fortunately, since [version 2.6.0](http://lists.rabbitmq.com/pipermail/rabbitmq-discuss/attachments/20110831/36015373/attachment.txt) (I believe...I could be wrong...) RabbitMQ has supported [Highly Available queues](http://www.rabbitmq.com/ha.html) (basically replicating queues across nodes in a cluster) to ensure that you don't need to be choked by a single point of failure in your messaging infrastructure and can still be performant and scalable.

What I want to discuss today is setting up a RabbitMQ [cluster](http://www.rabbitmq.com/clustering.html) with Highly Available queues using Amazon EC2. I'm sure you can use these techniques in a different environment, but I am tailoring all of this to a specific situation since I'm familiar with it and there doesn't seem to be a whole lot of information pertaining to it out there.

Before we begin, I must caveat this post with a few important notes that I think are easy to overlook.

# Hostnames = nodenames

It is **very important** that you understand the importance of the hostname for each of your instances when dealing with RabbitMQ clusters. The way that the clusters identify nodes and communicate with each other on Amazon's (and in general as well) infrastructure is critical. RabbitMQ, by default, will use **rabbit@_hostname_** for the name of the node. It really doesn't matter what you use for the hostname, as long as you can identify it later. For this post, let's assume they will be **ubuntu-** followed by the availability zone they are in. For example, **ubuntu-us-east-1a** or **ubuntu-us-east-1b**.

# Firewall rules

This might be obvious to some, but it is **very important** that each of your RabbitMQ nodes can communicate with one another. I think that if you are using RabbitMQ in the cloud you are aware of this, but just in case please keep it in mind. RabbitMQ communicates, by default, over port 5672. Therefore, it would be wise to assign a security group to each of these instances that allows port 5672, at least to instances within the same security group or another one you have set up. Otherwise debugging an issue will be unnecessarily difficult, and nobody wants to deal with that, right?

_Updated 2012-10-25 04:20:55 UTC:_ Per [Brett's](http://www.blogger.com/profile/01808630043272393203) suggestion in the comments, which I was ignorant of, it is a great idea to open the port that [epmd](http://www.erlang.org/doc/man/epmd.html) (Erlang Port Mapper Daemon)uses, which is the tool that which RabbitMQ relies on to identify nodes in it's cluster. That port is 4369 by default. Once the nodes are identified, by default they communicate through pretty much any available random port. You can add the following to your **rabbitmq.config** to override this behavior, so you only need to open a specific port. Using [Brett's](http://www.blogger.com/profile/01808630043272393203) example of port 65535, the following would be added to **rabbitmq.config**


```
[
{kernel,
[{inet_dist_listen_min, 65535},
{inet_dist_listen_max, 65535}
]
}
]
```

# Booting instance and installing RabbitMQ

To start, I booted up an [Ubuntu Server 12.04](http://www.ubuntu.com/download/server) instance in **us-east-1a** availability zone. Since we are keeping in mind redundancy and geographical outages, we're going to boot each instance in a different zone to better insulate from failure scenarios.

  **_ Please keep in mind I am using ubuntu 12.04, so your results may require a bit of deviating from what I'm doing to work in your particular environment._**


```
cd /etc/apt/sources.list.d
sudo vim apt-rabbitmq.list
deb http://www.rabbitmq.com/debian testing main
sudo apt-get update
sudo apt-get install rabbitmq-server
```

This should install [rabbitmq-server v. 2.8.7-1](http://www.rabbitmq.com/download.html) as of the publishing of this blog. As long as you are using version 2.8.6 or greater you should be ok (they fixed some bugs introduced in v. 2.8.5 having to do with the shutting down of a mirrored queue, which is exactly what we will be focusing on).

# Starting up a cluster

Next, we need to begin creating our cluster of nodes.

```
sudo /etc/init.d/rabbitmq-server stop (since the service gets started up on install
sudo rabbitmq-server -detached
sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl start_app
sudo rabbitmqctl cluster_status (should be one node running and one node in the cluster)
```

cluster_status Output:

```
Cluster status of node 'rabbit@ubuntu-us-east-1a' ...
[{nodes,[{disc,['rabbit@ubuntu-us-east-1a']}]},
 {running_nodes,['rabbit@ubuntu-us-east-1a']}]
...done.
```

Now, we have one node running in a cluster, which right now only has itself in it. Let's add another node to our cluster.

# Spinning up another node

Spin up another instance (PREFERABLY in a completely seperate availability zone, I'm using **us-east-1b**, so this instance's hostname is **ubuntu-us-east-1b**) and run the previous steps up until you start running rabbitmqctl commands. Instead of joining it's own cluster, we want this new instance to join the cluster defined by the previous **ubuntu-us-east-1a** node.

```
sudo rabbitmqctl stop_app
sudo rabbitmqctl reset
sudo rabbitmqctl cluster rabbit@ubuntu-us-east-1a rabbit@ubuntu-us-east-1b <i>(this way is disk based)</i>
```

OR

```
sudo rabbitmqctl cluster rabbit@ubuntu-us-east-1a <i>(this way is memory based)</i>
sudo rabbitmqctl start_app
sudo rabbitmqctl cluster_status
```

Running **sudo rabbitmqctl cluster_status** on either instance should now show them both in the cluster and running, similar to this:

```
Cluster status of node 'rabbit@ubuntu-us-east-1b' ...
[{nodes,[{disc,['rabbit@ubuntu-us-east-1b','rabbit@ubuntu-us-east-1a']}]},
 {running_nodes,['ubuntu-us-east-1b','rabbit@ubuntu-us-east-1a']}]
...done.
```

# Setting up Highly Available queues

Now let's set up an exchange and a highly available queue so we can send messages and ensure they are replicated across all our nodes.

I used [python](http://www.python.org/getit/) and [pika](https://pika.readthedocs.org/en/latest/index.html), but there are NUMEROUS other clients in most languages out there. The actual nitty gritty here is outside the scope of this post, but I'm sure it shouldn't be terribly hard to take these ideas and apply them to the language of you choosing. Run this code on the **ubuntu-us-east-1a** instance.

``` python
#!/usr/bin/env python

from pika.adapters import BlockingConnection
from pika import BasicProperties

connection = BlockingConnection()

channel = connection.channel()

client_params = {"x-ha-policy": "all"}

exchange_name = 'public'
queue_name = 'test_queue'
routing_key = 'test_routing_key'

channel.exchange_declare(exchange=exchange_name, type='topic')

channel.queue_declare(queue=queue_name, durable=True, arguments=client_params )

channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

connection.close()
```

Let's break down what we're doing here:

We're declaring our exchange like normal.

You see our **queue_declare** method has **arguments=client_params**. **"x-ha-policy" : "all"** informs rabbitmq that we want this queue to be highly available and replicated amongst our clustered nodes. This gives us the redundancy we are looking for. (source: http://www.rabbitmq.com/ha.html)

We create a binding like normal, and then we can just publish messages like normal, and rabbitmq will handle all the replication across the cluster nodes for us.

Here's where things get fun, and a little tricky.

# When catastrophe strikes...

The whole idea here is that when one node goes down the entire bus doesn't get taken out with it. You still want your system to function.

So, let's run a test.

With our 2 node cluster, let's send a message to our bus cluster.

``` python
#!/usr/bin/env python

from pika.adapters import BlockingConnection
from pika import BasicProperties

connection = BlockingConnection()

channel = connection.channel()

exchange_name = 'public'
routing_key = 'test_routing_key'

channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body='testing mirroring!', properties=BasicProperties(content_type="text/plain", delivery_mode=1))

print "publish complete"

connection.close()
```

The output from **sudo rabbitmqctl list_queues** on _either node_ should look like this:

```
Listing queues ...
test_queue 1
...done.
```

This shows that exactly one message is in the 'test_queue' queue on both nodes, but we only published it to one node. Our replication works!

Now, kill one of the instances. That's right. Nuke it. It's ok. You can even go into the instance, get the PID for the rabbitmq process, and **sudo kill -9** it if you like, in order to test a more disastrous situation. In fact, let's do that. We're going to **ps aux | grep rabbitmq** to get the PID for our rabbitmq process and then **sudo kill -9** that PID.

## _DISCLAIMER: Please be sure you know what you're doing here. Don't go and **sudo kill -9** all willy-nilly and then come back complaining about your machine being in a funky state. You've been warned, but if you have read this far, I'm not too worried._

If you run **sudo rabbitmqctl cluster_status** from the **ubuntu-us-east-1b** instance should fail since rabbitmq-server is no longer running. This is ok, and a part of our disaster experiment. We'll make it better later, I promise!

But if you go to the **ubuntu-us-east-1a** node and **sudo rabbitmqctl cluster_status**, it is alive and well, and shows that the other node is just not running. Sending a message to this (**ubuntu-us-east-1a**) node that is still running will properly queue the message.

```
Cluster status of node 'rabbit@ubuntu-us-east-1a' ...
[{nodes,[{disc,['rabbit@ubuntu-us-east-1b','rabbit@ubuntu-us-east-1a']}]},
 {running_nodes,['rabbit@ubuntu-us-east-1a']}]
...done.
```

# Disaster recovery

Now, if we were to bring that bad node back into cluster, like so:

```
sudo rabbitmq-server -detached
```

And then run **sudo rabbitmqctl list_queues**, you will see the message has been properly replicated! No data lost!

The takeaway here is that even if there is disastrous network interruption, you can configure your client applications to use the clustered endpoints to ensure that there is a MUCH better chance of them communicating their messages to the broker.

# What happens when the instance completely dies and we need to replace it?

Replacing a degraded instance is a normal operation in the cloud, but when using EC2 there are a couple of things to keep in mind. You need to be able to get the hostname for the killed instance. This is pretty simple, even if the host is long gone and you cannot access the instance metadata anymore. Just go to a healthy node and run **sudo rabbitmqctl cluster_status**. You should be able to deduce node that shows in the cluster but not running, and the hostname should be after the **rabbit@** part of the nodename. If you don't have ANY healthy nodes left, well...in that extreme case, I think you have more problems than I can help with!

# Spin up new instance (remember, different availability zone!)

Let's use **ubuntu-us-east-1c** this time. Remember, since we want to _replace_ the **ubuntu-us-east-1b** node in the cluster, we need to make the new **ubuntu-us-east-1c** node _look like_ the failed instance to RabbitMQ. This is how we do that:

```
sudo echo ubuntu-us-east-1b > /etc/hostname
sudo vim /etc/hosts
- 127.0.0.1 ubuntu-us-east-1b and remove any specific hostname redirects for old host
sudo vim /etc/rc.local
- hostname ubuntu-us-east-1b added before exit 0
# reboot instance
sudo rabbitmqctl cluster rabbit@ubuntu-us-east-1a rabbit@ubuntu-us-east-1b
```

The confusing part for me was associating this old hostname with the new instance. Since the cluster was created with the old name, and the running nodes have the reference to this nodename you can't just add a new node with any nodename. The other nodes will not see the old node in the cluster list will not work correctly. This could have been fixed in a recent build, but from what I understand this procedure is important. _**It's important that the hostname matches EXACTLY. This is because of the way RabbitMQ manages the cluster nodes.**_

As you see from running **sudo rabbitmqctl list_queues** from the new node, the queue data has been properly replicated to the new node!

Now this node will operate just like the old instance. It's a little tricky and awkward, but not terribly bad.

This, of course, can all be scripted up with puppet, chef, or other admin scripts already in your environment.

_Update: 2012-10-25 04:36:30 UTC:_ [Carl](http://www.blogger.com/profile/14828480937686018825) pointed out that RabbitMQ inherantly does not tolerate partitioning across availability zones due to potential cluster corruption from data loss([third paragraph](http://www.rabbitmq.com/clustering.html)). This is a valid point. However, the tradeoffs between getting something operational and implemented as simply as possible and adding complexity later led me to use naive Highly Available queues and clustering only. The documentation mention some plug-ins to enable better replication over WAN, such as [federation](http://www.rabbitmq.com/federation.html). I believe this looks to be a great addition to what I have written about here, and will definitely be looking into this in the very near future.

# Give yourself more than one point of failure

Coming off of the recent spat of EC2 outages, single points of failure are hot on the mind's of admins everywhere. If uptime is an important feature for your app (and isn't one for EVERY app?) this is another tool for the kit that can help prevent down time in case of emergency.
