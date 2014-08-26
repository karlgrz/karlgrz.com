author: karlgrz
comments: true
date: 2013-09-18 17:53
slug: stub-remote-api-calls-locally-with-nginx
title: Stub Remote API Calls Locally with Nginx
category: Coding
tags: nginx, 2013, distributed, api, stub

One of the things that makes distributed systems development somewhat of a challenge is interacting with all the remote APIs that your system requires to function properly.  

I find this a challenge when developing on the train (as I spend over 2 hours a day on one). 4G LTE is great and all, but there are dead zones and dropouts that make some API calls annoyingly long to respond.  

Lately I've been messing around with stubbing out the remote calls locally using nginx, so I thought I would share how I do it.  

It's quite simple, really, and seems to help me rapidly iterate over my own logic without needing to make expensive remote calls. Most recently, I've been interacting with some remote APIs using 3 legged oAuth authentication, which if you have any experience with that you can understand the frustration.  

Start by installing nginx (I'm assuming Ubuntu here, so substitute for your particular distribution):

```
sudo apt-get install nginx
```

Basic install. Nothing fancy. Now, let's say we want to stub out a call to remoteapi.yourdomain.com/first_stub_action?param=something. We need to use a different host in our dev environment, so a pattern I usually use is to replace .com with .dev and just redirect that URL in my hosts file.

Let's start by making /var/www if it doesn't exist (*note*: you don't need to use this, but it's pretty common for serving files, so I'll stick with that). We also want a folder for our stubbed endpoint, so let's create that in one shot:

```
mkdir -p /var/www/remoteapi.yourdomain.dev
```

That folder could be *whatever you want* as long as that's what you specify as the root in our nginx config (coming up shortly).  

Now, what should this call return? I like json, so let's use that. We're going to create a file (can also be whatever you want), I like the naming convention of calling it the action you are stubbing. For this call I'll use first_stub_action.json:

```
touch /var/www/remoteapi.yourdomain.dev/first_stub_action.json
```

Then let's paste the following into that file (using the editor of your choice or cat or whatever...doesn't matter):
*(note: this is simplified for the example)*

```
{
    "status": "ok",
    "value": "testValue"
}
```

Ok, now let's edit /etc/nginx/sites-available/default with the meat of what makes this work:

```
server {
    listen 80; 
    server_name remoteapi.yourdomain.dev;
    access_log   /var/log/nginx/remoteapi.yourdomain.dev_access_log;
    error_log   /var/log/nginx/remoteapi.yourdomain.dev_error_log;

    location / { 
        root /var/www/remoteapi.yourdomain.dev/;
        try_files $uri /first_stub_action.json;
    }   
}
```

The key's here lie in the location. **try_files** tries to resolve a url (denoted by $uri) and will continue trying files down the line until it either finds something that is valid or returns the last endpoint. You can even add a =404 at the end of the list to return a 404 if you want to (which is nice for testing errors). But in our case, we want to *always* return the first_stub_action.json file.  

Basically, *any* request made to remoteapi.yourdomain.dev with this configuration will return the contents of /var/www/remoteapi.yourdomain.dev/first_stub_action.json. Success!  

This is ready to go, we just need to restart nginx and add an entry into our hosts file for this .dev subdomain.

Add the following line to /etc/hosts:

```
127.0.0.1    remoteapi.yourdomain.dev
```

Then restart nginx:

```
sudo service nginx restart
```

If you navigate to remoteapi.yourdomain.dev/first_stub_action?param=something in your browser, you should see the contents of first_stub_action.json returned. Success!

But wait...what if we have OTHER URLs that we need to stub from the *same* subdomain? Right now, the way this is configured, EVERY call to remoteapi.yourdomain.dev will return the same result. It's nice if you only are stubbing one call, but what about multiple actions?  

That's easy, just add different locations and files for the different calls.

```
touch /var/www/remoteapi.yourdomain.dev/second_stub_action.json
```

And copy whatever you want to be returned into that file:

```
{
    "status": "ok",
    "value": "somethingElse"
}
```

And now our site config looks like this:

```
server {
    listen 80; 
    server_name remoteapi.yourdomain.dev;
    access_log   /var/log/nginx/remoteapi.yourdomain.dev_access_log;
    error_log   /var/log/nginx/remoteapi.yourdomain.dev_error_log;

    location / { 
        root /var/www/remoteapi.yourdomain.dev/;        
    }   

    location /first_stub_action {
        try_files $uri /first_stub_action.json;
    }

    location /second_stub_action {
        try_files $uri /second_stub_action.json;
    }
}
```

Now, when we go to remoteapi.yourdomain.dev/first_stub_action?param=something we get the contents of first_stub_action.json:

[![first_stub_action_screenshot](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/first_stub_action_screenshot.PNG)](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/first_stub_action_screenshot.PNG)

and when we go to remoteapi.yourdomain.dev/second_stub_action?param2=somethingElse, we get the contents of second_stub_action.json:

[![second_stub_action_screenshot](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/second_stub_action_screenshot.PNG)](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/second_stub_action_screenshot.PNG)

Success! A by product of this configuration is you will also get a 404 returned for any endpoint that has not been specified, which can be good or bad depending on your goals:

[![404_missing_action_screenshot](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/404_missing_action_screenshot.PNG)](/images/2013-09-18-stub-remote-api-calls-locally-with-nginx/404_missing_action_screenshot.PNG)

I hope this helps you as much as it has helped me in quickly stubbing out remote api calls, without a lot of ceremony and nonsense, so I can get on with actually writing the code that I'm interested in writing.
