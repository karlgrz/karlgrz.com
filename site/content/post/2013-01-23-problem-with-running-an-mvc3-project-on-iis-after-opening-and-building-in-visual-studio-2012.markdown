+++
author = "karlgrz"
comments = true
date = "2013-01-23T01:44:06"
slug = "problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012"
title = "Problem With Running an MVC3 Project on IIS After Opening and Building in Visual Studio 2012"
categories = ["Coding"]
tags = [".net", "2013", "c#", "iis", "mvc3", "visual studio 2012", "Web"]
+++

I was having trouble running a .NET 4.0, MVC3 web application locally on IIS after building in VS2012. The unit tests would pass, all projects would build successfully, and it would even run from Cassini, but something was just not working properly on IIS. This project SPECIFICALLY references MVC3 assemblies that are included in a packages folder in the project, so I didn't think it was MVC, but all signs were pointing to that. I uninstalled MVC4, tried changing the references, but everything was still failing.

So today I started going a little slower and found the culprit.

When you open a VS2010 solution in VS2012, you are greeted with a little HTML report of things that it decided to change for you so your project / solution would play nicely in both environments. For the most part, this all seems to work quite nicely.

[![01](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/01-1024x177.png)](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/01-1024x177.png)

I noticed that:

- open MVC3 project in 2012
- converts solution and projects
- save all
- project is now .NET Framework 2.0 for some reason (not explicitly set before?)
- if change in (web project) -> Properties -> Application -> Target Framework dropdown, then VS2012 mucks up my web.config pretty good, and it's hard to see what breaks (I was just getting 500's and it wasn't clear why)

[![02](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/02.png)](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/02.png)

[![03](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/03-1024x448.png)](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/03-1024x448.png)

The big thing that jumped out at me today was that web.config was changing along with the .csproj file after I changed the framework.

[![04](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/04.png)](/images/2013-01-23-problem-with-running-an-mvc3-project-on-iis-after-opening-and-building-in-visual-studio-2012/04.png)

This set off alarms in my brain, mostly "Why isn't TargetFrameworkVersion already there?"

So I reverted everything and instead of letting VS2012 change the framework, I just opened the .csproj in Sublime Text 2 (or any text editor) and added this:

``` xml
<TargetFrameworkVersion>v4.0</TargetFrameworkVersion>
```

After saving the .csproj file, re-opening the solution and letting VS2012 perform it's conversion, and building, the site runs again as expected from IIS. I lost WAY too much time to that nonsense. Hopefully nobody else has to.
