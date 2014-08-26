author: karlgrz 
comments: true
date: 2013-07-31 03:29:22
slug: one-reason-i-like-linq-in-c
title: One Reason I Like LINQ in C#
category: Coding
tags: .net, 2013, c#, linq

This is one of my favorite things about LINQ in C#. This code:

``` csharp
var nonBlank = false;

foreach (var byteval in arrayOfBytes)
{
    if (byteval <= 0) 
        continue;
    nonBlank = true;
    break;
}
```

Becomes this code:

``` csharp
var nonBlank = arrayOfBytes.Any(byteval => byteval > 0);
```
