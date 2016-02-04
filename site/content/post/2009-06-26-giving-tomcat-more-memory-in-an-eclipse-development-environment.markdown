+++
author = "karlgrz"
comments = true
date = "2009-06-26T15:45:00"
slug = "giving-tomcat-more-memory-in-an-eclipse-development-environment"
title = "Giving Tomcat More Memory in an Eclipse Development Environment"
categories = ["Coding"]
tags = ["eclipse", "memory", "tomcat"]
+++

Sometimes when running tomcat inside eclipse there are processes that throw OutOfMemory errors (creating an extremely large Excel file, for instance) that are not thrown on our production servers.

By default, Eclipse runs tomcat with 64MB of maximum memory, even if you set up Eclipse to use more memory by editing the eclipse.ini file (I have mine set to 1024, and tomcat still runs at 64MB).

Eclipse makes it really easy to pass command line arguments to your Tomcat instance every time it is started. I found this out after spending about 30 minutes testing different configurations in the catalina.bat file. To increase your Eclipse environment's Tomcat memory allocation:

- Go to Window -> Preferences -> Java -> Installed JRE's -> and click "Edit" after highlighting your JRE.
- Add the following line to the "Default VM Arguments" text box:

```
-Xms1024m -Xmx1024m
```

This starts up Tomcat each time with a 1024MB Heap, which we are also setting as the maximum heap size. Please note that you can set -Xms (starting) to a smaller value, and have the JVM increase the size as it needs it. However, this operation is expensive and will affect performance accordingly. Just keep that in mind.
