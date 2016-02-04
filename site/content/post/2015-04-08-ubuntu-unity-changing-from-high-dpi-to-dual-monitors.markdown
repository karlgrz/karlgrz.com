+++
author = "karlgrz"
comments = true
date = "2015-04-08T17:30:00"
slug = "ubuntu-unity-changing-from-high-dpi-to-dual-monitors"
title = "Ubuntu Unity: Changing from High DPI to Dual Monitors"
categories = ["Coding"]
tags = ["2015", "bash", "ubuntu", "unity", "high-dpi"]
+++

I've been running Ubuntu Desktop on my desktop machine at home for a few years now (I put together a great system in January 2014). Just recently, in November 2014, I switched my work laptop from a retina MacBook Pro to a Dell XPS 15 (High DPI w/ touchscreen: [amazon.com](http://www.amazon.com/Dell-XPS-15-Touchscreen-Performance/dp/B00N3FPZ5E/) ) running Ubuntu Desktop 14.04. For some reason, I prefer Linux to OS X, I guess I'm weird, heh.

The screen on this model is a 3200x1800 touchscreen, and text looks just as good (if not better) than the retina MacBook does at max DPI.

The problem is: it's Linux, so...high DPI is not exactly a well supported feature throughout the ecosystem.

At the time I received the Dell, it was pointless trying to run day to day work activities in high DPI. Everything looked all jacked up, whether it was browsing the web in Chrome or Firefox, editing text with Sublime Text, chatting in HipChat, querying postgresql with PgAdmin, or looking at source trees in TortoiseHG, amongst other things. Odd stuff like this was commonplace:

<blockquote class="instagram-media" data-instgrm-version="4" style=" background:#FFF; border:0; border-radius:3px; box-shadow:0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,0.15); margin: 1px; max-width:658px; padding:0; width:99.375%; width:-webkit-calc(100% - 2px); width:calc(100% - 2px);"><div style="padding:8px;"> <div style=" background:#F8F8F8; line-height:0; margin-top:40px; padding:50% 0; text-align:center; width:100%;"> <div style=" background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAsCAMAAAApWqozAAAAGFBMVEUiIiI9PT0eHh4gIB4hIBkcHBwcHBwcHBydr+JQAAAACHRSTlMABA4YHyQsM5jtaMwAAADfSURBVDjL7ZVBEgMhCAQBAf//42xcNbpAqakcM0ftUmFAAIBE81IqBJdS3lS6zs3bIpB9WED3YYXFPmHRfT8sgyrCP1x8uEUxLMzNWElFOYCV6mHWWwMzdPEKHlhLw7NWJqkHc4uIZphavDzA2JPzUDsBZziNae2S6owH8xPmX8G7zzgKEOPUoYHvGz1TBCxMkd3kwNVbU0gKHkx+iZILf77IofhrY1nYFnB/lQPb79drWOyJVa/DAvg9B/rLB4cC+Nqgdz/TvBbBnr6GBReqn/nRmDgaQEej7WhonozjF+Y2I/fZou/qAAAAAElFTkSuQmCC); display:block; height:44px; margin:0 auto -44px; position:relative; top:-22px; width:44px;"></div></div><p style=" color:#c9c8cd; font-family:Arial,sans-serif; font-size:14px; line-height:17px; margin-bottom:0; margin-top:8px; overflow:hidden; padding:8px 0 7px; text-align:center; text-overflow:ellipsis; white-space:nowrap;"><a href="https://instagram.com/p/wbc1Vph3le/" style=" color:#c9c8cd; font-family:Arial,sans-serif; font-size:14px; font-style:normal; font-weight:normal; line-height:17px; text-decoration:none;" target="_top">A photo posted by Karl Grzeszczak (@karlgrz)</a> on <time style=" font-family:Arial,sans-serif; font-size:14px; line-height:17px;" datetime="2014-12-10T14:05:23+00:00">Dec 10, 2014 at 6:05am PST</time></p></div></blockquote>
<script async defer src="//platform.instagram.com/en_US/embeds.js"></script>

I tried all kinds of hacks and settings to get things working nicely, but alas, it was frustrating, and it was just easier to run in 1920x1080. It still looked ok, but it wasn't __as good__ as it could be.

This pissed me off, obviously ;-)

Last week, I saw an update for Chromium. Every time I see an update for Chromium, I try it on high DPI. Lo and behold, they finally have scaling working properly! Huzzah! This is what it looks like now:

![Present day Chromium](/images/2015-04-08-ubuntu-unity-changing-from-high-dpi-to-dual-monitors/Chromium_HighDPI.png)

So I put in a bit more work, and I'm happy to say my entire workflow can be sustained in high DPI, with a few caveats that I can put up with.

- HipChat still looks a little weird (shrug)
- PgAdmin looks really weird. Query output windows are really smooshed in grid view.
- TortoiseHg is hilarious:

![Thanks, QT](/images/2015-04-08-ubuntu-unity-changing-from-high-dpi-to-dual-monitors/TortoiseHG_HighDPI.png)

- VirtualBox guests have no respect for scaling factor. This is fine, because I don't do much work in Windows anymore, so I just need to run an IIS server for MVC 5 apps until vNext is fully supported on Linux.
- Dual monitors are still jacked up because you can't set monitor independent text scaling factors (I think this is supported in 14.10 or 15.04 but I can wait for that).

So this is great when I'm just using the laptop, but what about when I go to the office and use my second monitor?

Like I said, I'm on 14.04, so this might be better (or hopefully unnecessary) in 14.10 or 15.04 (PLEASE let me know in the comments if it's the case!), but I just whipped up a couple very simple scripts to run when I switch between the two.

SetupForHighDPI.sh
``` bash
#!/bin/bash

dconf write /com/ubuntu/user-interface/scale-factor "{'DP1': 8, 'eDP1': 16}"
gsettings set org.gnome.desktop.interface text-scaling-factor '1.25'
```

SetupForDualMonitors.sh
``` bash
#!/bin/bash

dconf write /com/ubuntu/user-interface/scale-factor "{'DP1': 8, 'eDP1': 8}"
gsettings set org.gnome.desktop.interface text-scaling-factor '1.0'
```

What these scripts do, basically, is just automate setting the Text Scaling Factor from Unity Tweak Tool and the Scaling Factor from Settings -> Displays menu. You'll need to find the settings for your specific system, these posts helped me out:

[http://askubuntu.com/questions/454279/change-default-system-font-using-terminal-only-in-14-04](http://askubuntu.com/questions/454279/change-default-system-font-using-terminal-only-in-14-04)

[http://askubuntu.com/questions/510457/how-do-i-get-the-value-of-display-scale-for-menu-and-title-bars-from-the-c/510476#510476](http://askubuntu.com/questions/510457/how-do-i-get-the-value-of-display-scale-for-menu-and-title-bars-from-the-c/510476#510476)

It's annoying to have to run a script each time I switch from just the laptop to using my external monitor at work. It's all worth for those beautiful looking, high DPI fonts though!

Hopefully soon I won't need any of this and high DPI in Unity will Just Work™. A lot of people tell me to switch to GNOME or KDE or xfce. I've used all those, and while they are great in their own right, I've come to like Unity. It should work well here, too. It seems like all the problematic apps are using QT. Could be a coincidence.