author: karlgrz 
comments: true
date: 2013-11-30 01:29:22
slug: enabling-wifi-in-raspbian
title: Enabling Wifi in Raspbian
category: Coding
tags: raspberry-pi, raspbian, linux

I've started playing around with a [Raspberry Pi](http://www.raspberrypi.org/) recently. It's pretty slick, but there are a few gotchas I've run into, particularly regarding wifi.

I'm using a [Model B Raspberry Pi](http://www.adafruit.com/products/998?gclid=COG4qNeBjLsCFccRMwodtxcAUQ) which came with a USB wifi dongle, since my TV and router are not in the same room.

With [raspbmc](http://www.raspbmc.com/about/), it asks for your ssid and passphrase, but with an image like [raspian](http://www.raspbian.org/), you have to configure the settings yourself. It's not too bad, but the documentation I searched for was not very helpful or clear.

This worked for me. Here's is what my /etc/network/interfaces looks like:

```
auto lo

iface lo inet loopback
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet dhcp
wpa-ssid "YourSSIDGoesInHere"
wpa-psk "YourWifiPassphraseGoesInHere"
```

After that, run this to reboot the pi:

```
sudo reboot
```

Once it starts back up you should see a message displaying your pi's new IP address handed out from your router displayed during boot.
