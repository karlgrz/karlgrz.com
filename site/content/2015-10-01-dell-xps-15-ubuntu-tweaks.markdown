author: karlgrz
comments: true
date: 2015-10-01 19:00:00
slug: dell-xps-15-ubuntu-tweaks
title: Dell XPS 15 Ubuntu Tweaks
category: Coding
tags: 2015, ubuntu, unity, dell, xps15, synaptics, bumblebee, nvidia

Tonight I was chatting with someone interested in buying a [Dell XPS 15](http://www.amazon.com/Dell-XPS-15-Touchscreen-Performance/dp/B00N3FPZ5E/) versus a Macbook Pro. Having used the XPS 15 for almost a year now I had a lot of good things to say about it. There's a few things I had to do in order to get it even closer to the perfect dev machine (still not quite there, but nothing is). I figured I would jot them down in case I forget anything in the future.

[This post](http://karlgrz.com/ubuntu-unity-changing-from-high-dpi-to-dual-monitors/) covers some of what I do to bounce back and forth between HiDPI and 1080p (although in practice I spend a lot more time in 1080p still today).

These notes fix some of the quirks that initially annoyed me about this laptop, and if you're coming from using a Macbook you might find these useful as well.

## Touchpad

The touchpad drivers on this laptop are great, and with these small tweaks it, in my opinion, performs very closely to how the touchpad behaves on a Macbook Pro (which I think is that hardware's best feature).

Initially, the touchpad will have two "soft buttons" in bottom left and right corners. These pissed me off so much I wanted to throw the laptop across the room. But cooler heads prevailed, and I figured out how to just turn them off.

Also, three finger tap to get "middle click" wasn't turned on initially, so this autostart script does those three things.

(note: if you know a better way to do this please leave a comment!)

I added the following to `~/.config/autostart/touchpad.desktop`:

```
[Desktop Entry]
Type=Application
Exec=synclient TapButton3=2 && synclient RightButtonAreaTop=0 && synclient RightButtonAreaLeft=0
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=FixTouchpad
Name=FixTouchpad
Comment[en_US]=Removes the soft mouse buttons and adds three finger middle click on the touchpad
Comment=Removes the soft mouse buttons and adds three finger middle click on the touchpad
```

## NVIDIA Drivers and Bumblebee

If you've ever used linux on a desktop you know all too well the dumptruck of nonsense you have to deal with regarding video card drivers.

The state of that world has gotten a lot better lately, however. Now there is a new ppa that seems to be much, much better supported. Add the ppa like so:

```
sudo apt-add-repository ppa:graphics-drivers/ppa
```

This ppa has drivers for all cards (nvidia, amd, etc) which is really nice.

Then:

```
sudo apt-get update
```

For the XPS 15 model I have (with the NVIDIA GeForce GT 750M) when I first got it back in November 2014 it was a bit of a pain to track down everything. Now you can just:

```
sudo apt-get install nvidia
```

Easy as that. However, if you stop there, the system is going to try to use the nvidia driver all the time, which can be quite a drain on your battery. You only need the nvidia card when you are doing graphics intensive stuff, so why use it all the time?

That's where [bumblebee](https://github.com/Bumblebee-Project/Bumblebee) comes in. It's a nifty little utility that lets you start specific programs (like games) with your nvidia graphics drivers, and let the integrated graphics from intel power the rest of your computing experience. This works really well. It's a bit tricky to set up, but I'll go through the steps I used. [This post](http://askubuntu.com/a/625090/89271) helped me out a lot.

So in my case I installed nvidia-355 (as that is the current version in 15.04). Now I need to install bumblebee:

```
sudo apt-get install bumblebee bumblebee-nvidia primus python-appindicator
```

Next, there is a taskbar indicator that I like to install that makes it really easy to launch games or whatever using your nvidia drivers:

```
git clone https://github.com/Bumblebee-Project/bumblebee-ui.git
cd bumblebee-ui
./INSTALL
```

I also had to install this package on 15.04, might be different on other builds:

```
sudo apt-get install bbswitch-dkms
```

Next, add your user to bumblebee group:

```
sudo adduser $USER bumblebee
```

If you're on 15.04 or later, enable the daemon:

```
sudo systemctl enable bumblebeed
```

Next, add the following two lines to `/etc/modules-load.d/modules.conf`:

```
i915
bbswitch
```

Ok, if you made it this far, you're almost done. The way bumblebee works is by forcing the kernel to blacklist your nvidia drivers at system boot (so they are never loaded and, thus, your desktop is never driven by a power hungry GPU when it doesn't need to be) and only loads them when it is asked.

You need to edit `/etc/modprobe.d/bumblebee.conf` to add the version of the driver you installed to the list (in this case, nvidia-355). So you add this to the end of the file (replace 355 with whatver version number you installed):

```
blacklist nvidia-355
```

There should be many versions in this file.

Last step! You need to edit the version of `/etc/bumblebee/bumblebee.conf` to match your version (I'm not sure this is necessary anymore, but in my case I had to do it, just check it out):

```
Driver=nvidia
```

```
KernelDriver=nvidia-355
```

```
LibraryPath=/usr/lib/nvidia-355:/usr/lib32/nvidia-355
```

```
XorgModulePath=/usr/lib/nvidia-355/xorg,/usr/lib/xorg/modules
```

Reboot and ride away clean.

I am probably missing something in current or different desktop environments (I'm using Unity) but this worked magically well for me for playing games on Steam or on a Windows VM.

## Hybrid Sleep / Suspend

One of my favorite features of the Macbook was just closing the lid at any time and being confident that when I popped open the lid later both the state of my environment and my battery would be preserved.

Initially, at least in November 2014 on ubuntu 14.04, this didn't work that well. Even when you closed the lid, the system wouldn't always go to sleep, instead sometimes it would just lock and stay awake in my bag. When I would take it out in the morning on the train I would have some piddly bit of juice left instead of the 65-70% I had expected from the night before (not to mention my laptop would be burning hot). Yikes.

This little tweak forces the system to always use hibernate to but in a way that is similar to the behavior you get when closing the Macbook lid (and I could be wrong here, just going by what I observed when I had a Macbook).

Add this to `/etc/pm/config.d/00-use-suspend-hybrid`:

```
# WORKAROUND: always set the default hibernate mode first (normal mode)
# (not required if you have the patch mentioned by Rohan below (http://askubuntu.com/a/344879/169))
HIBERNATE_MODE=platform

# Always use hibernate instead of suspend, but with "suspend to both"
if [ "$METHOD" = "suspend" ]; then
  METHOD=hibernate
  HIBERNATE_MODE=suspend
fi

# Make sure to use the kernel's method, in case uswsusp is installed etc.
SLEEP_MODULE=kernel
```

Now, when I close my lid, the laptop properly goes to sleep. Huzzah.

## Only wake from sleep by lid or power button

...only to wake up randomly?! C'mon, Man!

Sometimes I noticed, even after adding that tweak, the laptop would somehow wake itself up in the middle of the night (maybe it's thirsty...).

Anyway, to prevent this is very simple...using [this post](http://www.linuxquestions.org/questions/linux-hardware-18/cannot-wake-from-suspend-with-keyboard-or-mouse-on-dell-xps-17-l702x-940367/) and [this post](https://bugs.launchpad.net/dell-sputnik/+bug/1161962) and doing some experimenting I settled on this and I haven't experienced the wake up nonsense since.

Add this to `/etc/rc.local` before the exit 0 line:

```
## Disable wake up for all except lid and power button
echo EHC1 > /proc/acpi/wakeup
echo EHC2 > /proc/acpi/wakeup
echo XHC > /proc/acpi/wakeup
```

Now, only opening the lid or pressing the power button will wake your laptop.

After all these tweaks, the Dell XPS 15 is probably the best laptop I've used, only because the driver support for linux is better on this than on the Macbook. The Macbook's touchpad is the thing I miss the most, but the XPS 15 gets very close. And I like linux a lot better than OS X, so this one edges it out.

What else am I missing?