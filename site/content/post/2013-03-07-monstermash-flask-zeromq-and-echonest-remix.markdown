+++
author = "karlgrz"
comments = true
date = "2013-03-07T14:55:27"
slug = "monstermash-flask-zeromq-and-echonest-remix"
title = "MonsterMash: Flask, ZeroMQ, and EchoNest Remix"
category = ["Coding"]
tags = ["2013", "distributed", "dreamhost", "ec2", "echonest", "python", "remix", "zeromq"]
+++

Off and on for the past couple of months I've been working on a side project using [flask](http://flask.pocoo.org/), [zeromq](http://www.zeromq.org/), and the [remix api](http://echonest.github.com/remix/) by [echo nest](http://the.echonest.com/).

If you take a look online, there are a lot of excellent guides to introduce you to [flask](http://flask.pocoo.org/), but not many that dive into something more complex or closer to something that an engineer in more distributed services would need to put together. I've seen some great guides on _organizing_ larger applications, but not so much commentary about how the experience was. This is what I want to offer to you here, just some thoughts about working with this framework for a client/server project.

## MonsterMash

I am a musician, so music is a big part of my life. I've always been fascinated with [echo nest](http://the.echonest.com) and all the cool stuff they do with big music data, so I thought I would give some of their tools a spin. What better way to do that then to create a little web app to mash songs up?

[![MonsterMash logo](/images/2013-03-07-monstermash-flask-zeromq-and-echonest-remix/monster.jpg)](http://monstermash.karlgrz.com)

All the code is hosted on github here: [https://github.com/karlgrz/monstermash](https://github.com/karlgrz/monstermash)

My little site, [MonsterMash](http://monstermash.karlgrz.com), uses an example from the [echo nest](http://the.echonest.com) [remix api](http://echonest.github.com/remix/), [afromb.py](https://github.com/echonest/remix/blob/master/examples/afromb/afromb.py) written by [Ben Lacker](https://github.com/blacker). This set of code basically takes song A and applies segments of song B that are somewhat beat-matched to A. It does some volume enveloping calculations to even out the levels between both tracks, too, so one isn't extremely overpowering.

If you're not familiar with the [remix api](http://echonest.github.com/remix/) from [echo nest](http://the.echonest.com), I encourage you to check out their tools [here](http://developer.echonest.com/).

## Dreamhost

I have a shared hosting account with [Dreamhost](http://www.dreamhost.com) that hosts this blog (and a variety of other nonsense, as well). I wanted to get [flask](http://flask.pocoo.org/) up and running on on [Dreamhost](http://www.dreamhost.com) since, well, I'm cheap and didn't want to spend any more money than I had to.

This proved to be a fun challenge that wasn't very difficult to overcome. [Dreamhost](http://www.dreamhost.com) doesn't really give you root access to anything, since it's shared hosting. This is understandable, but it makes installing python and linux packages kind of annoying. Also, you're normally forced to use whatever version of python is installed on the server that your account is hosted on. Weak.

Fortunately, [virtualenv](http://www.virtualenv.org) allows me to easily manage a self contained python environment in my local user directory. I won't go into all the details here, use the resources out there for virtualenv if you have trouble. I found [this guide](http://wiki.dreamhost.com/Flask) to be helpful in getting started. Basically, you need to configure the subdomain that you'll be using for the site to use passenger for python apps and to point to the correct virtualenv path. If you take a look at [my passenger_wsgi.py](https://github.com/karlgrz/monstermash/blob/master/passenger_wsgi.py) file you'll get the idea. This has to live at the root of the subdomain to work properly.

[![Passenger Checkbox in Dreamhost](/images/2013-03-07-monstermash-flask-zeromq-and-echonest-remix/02_passenger_checkbox_on_dreamhost.png)](/images/2013-03-07-monstermash-flask-zeromq-and-echonest-remix/02_passenger_checkbox_on_dreamhost.png)

[Dreamhost](http://www.dreamhost.com) seems to be doing more than an adequete job of handling requests, but I don't think anything I've done on there has been very high traffic. I'm sure if anything high traffic was hosted there it would probably need to be moved to a self hosted solution somewhere, but that is just speculation.

## EC2

I chose [Amazon EC2 free tier](http://aws.amazon.com/free/) for the server since it's, well, free. The t1.micro instance I'm using is not recommended for anything other than this: a demonstration of technology. The instances are NOT tuned for anything production ready that requires any kind of processor power. That being said, for the purposes I was going for this worked out nicely. Free is good!

Basically, the song processing takes (a lot) longer than it would if I actually spent some money for a decent spec'd instance with some computing power for crunching the remix (c1.medium would be sufficient, I think). I'm ok with that. You should be too ;-)

## Flask

I'm not going to chronicle the many steps and setups I went through to get [flask](http://flask.pocoo.org/) up and running. I used the following guides along my journey, I think they have done a great job explaining the basics:

- [Flask large apps how-to](https://github.com/mitsuhiko/flask/wiki/Large-app-how-to) and [flask patterns](http://flask.pocoo.org/docs/patterns/packages/) by [@mitsuhiko](http://twitter.com/mitsuhiko), the flask creator
- [Fantastic multi-post tutorial on getting started with flask](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by [@miguelgrinberg](http://twitter.com/miguelgrinberg)
- [Fbone, a flask large application template](https://github.com/imwilsonxu/fbone) by [@imwilsonxu](http://twitter.com/imwilsonxu)

Overall, I really enjoyed working with [flask](http://flask.pocoo.org/). To an me, it just feels like how I expect a web framework to work. You get all the routing power you would expect from a web framework with VERY little ceremony. It stays out of your way so you can just write your code and get on with your day. There were very few points in time when I was actually setting up routes or other flask-specific tasks that I had to look for a great deal of information to get moving forward.

For example, a basic "about" view that returns just a static html template can look like this:

``` python
@app.route('/about')
def about():
	return render_template('about.html')
```

Take a look at [my views.py](https://github.com/karlgrz/monstermash/blob/master/monstermash/views.py) for the brunt of the [flask](http://flask.pocoo.org/) code.

I am enamored with [SQLAlchemy](http://www.sqlalchemy.org/), the python ORM. It's quite literally the best ORM I've ever used (for better or worse...that's up for debate as well). I love that queries are as simple as this:

``` python
user = db_session.query(User).filter(User.username==username).first()
```

I have not had a chance to load test this app very well yet, so I don't have any data related to how efficient [SQLAlchemy](http://www.sqlalchemy.org/) is being with it's query generation to the server.

I also really like working with [Jinja2](http://jinja.pocoo.org/docs/) templates. They feel very natural to me, and there weren't any situations that I was left wondering how to implement something. Out of the box, they just work.

[Flask](http://flask.pocoo.org/) also feels a lot less taxing to configure and set up than [django](https://www.djangoproject.com/) did. Now, I must caveat this statement with a few facts. My first (and only experience) with django was a couple years ago. I was not nearly as comfortable with python as I am now, and I'm certain the framework has developed more since I last looked. I will definitely be taking another look at it in the not so distant future.

## What I don't really like about what I did with flask

I might like the framework a lot, but there are things that in particular I did on this project that I'd like to improve on in the future.

- In order to separate the views from the init module you need to have circular imports, which does _**NOT**_ feel good to me. The creator explains it in the links above and that it isn't a big deal, but it really doesn't feel right and I wish there was a better way to do it.
- __init__ is pretty freaking large in order to share dependencies (which I believe [Blueprints](http://flask.pocoo.org/docs/blueprints/) would help with). I'm sure there are more refactorings I can do on that to compartmentalize it better (the links above went a little more in depth with the organization, especially Fbone...something to keep in mind in the future.)
- I would like to further refactor the views into better organized classes, but for demonstration purposes I think this is ok. I'd also like to implement [Blueprints](http://flask.pocoo.org/docs/blueprints/), but I'll save that for later. These are both just shortcomings of my own time, as they are certainly possible, I just didn't go the extra step for this demonstration.

We've started using [flask](http://flask.pocoo.org/) for a small monitoring web app in production for [work](http://www.mediafly.com) and it has worked out quite well. We had a few hiccups with server configuration and had to start using [gunicorn](http://gunicorn.org/) to ensure performance, but it was a pretty smooth deployment all around I think.

Also, obviously there's no tests. I'm really not as comfortable with [pyunit](http://pyunit.sourceforge.net/) as I am with [NUnit](http://www.nunit.org/) and I didn't want to delay the work on this side project to learn pyunit. This is on my radar in the short future, and hopefully I can get some TDD practice with pyunit soon.

## ZeroMQ

Again, I'm not going to give an introduction or setup tutorial on [zeromq](http://www.zeromq.org/). There are plenty of guides online, and they do a wonderful job of that.

I'm very used to working with [RabbitMQ](http://www.rabbitmq.com) in production for work. [zeromq](http://www.zeromq.org/) is definitely not RabbitMQ, and that's ok and expected.

What I like about [zeromq](http://www.zeromq.org/) is that, to me, it seems geared towards simple messaging needs that do not require redundancy and durability and clustering and replication and bla bla bla...it's simple when you need simple.

And that's pretty refreshing. RabbitMQ is by no means a piece of bloatware, in my opinion, but it can be a bit daunting to get set up and going. The biggest problem I had with zeromq ended up being fine in the end (I was worried about building the software on Dreamhost, but it worked out just fine). I love that I can send a message like this:

``` python
import json
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect('remoteserver:5000')
socket.send_json(json.dumps([{'id':id, 'key': key}]))
```

And process a message like this:

``` python
import json
import zmq

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect('127.0.0.1:5000')
message = socket.recv_json()
obj = json.loads(message)[0]
```

I really did not have much in the way of a bad time with [zeromq](http://www.zeromq.org/). Not much bad I can say about it. I used the PUSH/PULL methodology of distributing jobs kicked off by the web front end to the workers on my backend server. It got the job done pretty easily and quickly. I will definitely be looking to zmq in the future for quick and dirty projects that I need to get up and going quickly

That being said, it's kind of difficult for me to trust [zeromq](http://www.zeromq.org/) in a large scale production app. They provide a lot of good examples and presentations on redundancy and clustering and all the features I would expect from a durable queueing implementation, but it just feels really lightweight to the point that I don't trust it. And that's really the only evidence I have against it. I'd love to implement a really high traffic service with it to get some numbers and see some real world usage, but I guess I'm a little afraid to use anything other than RabbitMQ for that sort of thing. One of these days perhaps I will just have to make a leap and give it a shot, because the ease of use and visibility that it allows are really refreshing.

Check this out if you're interested in a more in depth read about [zeromq and messaging ideology](http://zguide.zeromq.org/page:all) in general.

## Remix

[Remix](http://echonest.github.com/remix/) is an SDK for interacting with [echo nest's](http://the.echonest.com) hive mind, which allows you to programmatically "chop up" a given song into individual bars, beats, and tatums and "remix" them any way you like.

As a musician and an engineer, this technology has fascinated me for a long time. It blows my mind where we've come in terms of computing to allow things like this to be possible.

I messed around with trying to detect segments (i.e. verse, chorus, bridge, etc.) of both songs and using those for the mashes, but it proved to be a bit flaky with my weak first attempt. I think I will work on that in the not-so-distant future because the technology fascinates me, but the main purpose of this project was flask and zeromq and I just wanted to get it out there. Remix hacking will come later :-)

In the meantime, I thought I would share one of the more exceptional remixes I encountered in my testing of MonsterMash: [Nine Inch Nails Closer](http://www.youtube.com/watch?v=PTFwQP86BRs) and [Johnny Cash covering NIN's Hurt](http://www.youtube.com/watch?v=SmVAWKfJ4Go)

- [Closer as seed song](https://www.dropbox.com/s/ydu09uqi4frlgvw/CloserHurt.mp3?dl=1)
- [Hurt as seed song](https://www.dropbox.com/s/jazuht7ekdd4oy2/HurtCloser.mp3?dl=1)

Just hearing how these turned out made this whole thing worth while. It blows my mind that python code (or any code) can do these types of things now. We've come a long way, but we still have a long way to go. I'm excited for what's coming next!

Please feel free to create your own mash ups on [MonsterMash](http://monstermash.karlgrz.com) and [let me know](http://twitter.com/karl_grz) what you come up with!

## Conclusion

I had a lot of fun learning these new technologies. It doesn't hurt that I am using [flask](http://flask.pocoo.org/) in production, so I benefit from having some experience with something that I will definitely be using more and more in my work.

I've still got a lot to learn about all of this stuff.

I really enjoyed a lot of everything I used on this project. In my experience that doesn't happen very often. I hope the luck keeps going!
