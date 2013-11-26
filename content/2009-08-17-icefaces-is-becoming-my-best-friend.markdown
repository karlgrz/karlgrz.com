author: karlgrz 
comments: true
date: 2009-08-17 21:07:00
slug: icefaces-is-becoming-my-best-friend
title: ICEFaces is becoming my best friend...
category: Coding
tags: ICEFaces, JavaEE, JSF

Last week was a greatly productive week, in my opinion. I continued developing a new internal web application for our clients (a glorified query tool for analyzing their data warehouse). I originally wrote this application using a different set of components, and I was, to put it lightly, "un-impressed" with the reliability of the suite.  
  
So I decided to re-write the application using ICEFaces.  
  
And I couldn't be happier. ICEFaces appears to be a much more mature, reliable framework than unreliable component suite that actually cost money for a license.   
  
All the functionality I required was ready to go out of the box with ICEFaces (popup dialogs, data tables, panel series repeaters, transition effects ala jQuery). And since ICEFaces supports AJAX calls in all their components I get a front end that is much more responsive and less headache inducing (full page refreshes give me seizures sometimes...).   
  
My only gripe seems to be the fact that the component suite appears to render it's styles on application generation. I.e. the component suite itself creates the default style sheets used by all the components, which makes referencing a custom style sheet a pain (at least in the short trial and error I tried last week). Perhaps this will be easier as I continue using the framework more in the coming months. Thus far, I am very impressed with the suite of components, and will probably be reaching for those .jar files in many a project to come.
