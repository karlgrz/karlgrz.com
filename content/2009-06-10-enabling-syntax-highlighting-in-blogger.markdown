author: karlgrz 
comments: true
date: 2009-06-10 03:16:00
slug: enabling-syntax-highlighting-in-blogger
title: Enabling Syntax Highlighting in Blogger
category: Coding
tags: blogger, syntaxhighlighting

This evening I wanted to put a little effort into enabling syntax highlighting for code in my posts here on Blogger. The process started innocently enough, but there were a few trip ups along the way, so I decided to share them here.  
  
I chose to use [syntaxhighlighter](http://code.google.com/p/syntaxhighlighter/), which is hosted on Google Code. It is an all JavaScript solution to syntax highlighting that seems to play nicely with Blogger.  
  
We will link to the svn trunk for the necessary JavaScript & CSS files. This eliminates the need to host these files from a seperate source, which is incredibly convenient if you do not have a host set up for your blog.  
  
First things first, head over to the "Layout" tab from the Blogger dashboard. This will bring you to a screen with with a graphical representation of your blog. Click on "Edit HTML".  
  
From this page click inside the "Edit Template" text box with all the HTML. Locate the <head> tag, and copy the following lines immediately after it:  

``` html   
<link href='http://syntaxhighlighter.googlecode.com/svn/trunk/Styles/SyntaxHighlighter.css' rel='stylesheet' type='text/css'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shCore.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushJava.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushJScript.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushCss.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushSql.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushCSharp.js'/>
<script language='javascript' src='http://syntaxhighlighter.googlecode.com/svn/trunk/Scripts/shBrushXml.js'/>
```

This enables the following:  

- CSS styling for the code [(SyntaxHighlighter.css)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Styles/SyntaxHighlighter.css)
- Core JavaScript libraries for rendering [(shCore.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shCore.js)
- Java syntax highlighting support [(shBrushJava.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushJava.js)
- JavaScript syntax highlighting support [(shBrushJScript.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushJScript.js)
- CSS syntax highlighting support [(shBrushCss.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushCss.js)
- SQL syntax highlighting support [(shBrushSql.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushSql.js)
- C# syntax highlighting support [(shBrushCSharp.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushCSharp.js)
- XML and HTML syntax highlighting support [(shBrushXml.js)](http://code.google.com/p/syntaxhighlighter/source/browse/trunk/Scripts/shBrushXml.js)
  
NOTE: You don't **need** to import the same syntax support I did. These are simply the languages that I will most likely be posting about on my blog, so I have enabled them off the bat. Import what you need. For the most up to date listing of supported language parsers, see the [Script](http://code.google.com/p/syntaxhighlighter/source/browse/#svn/trunk/Scripts) directory from the current svn trunk of [syntaxhighlighter](http://code.google.com/p/syntaxhighlighter/).  
  
Next, locate the </body> tag, and paste the following code immediately before it:  

``` html 
<script language='javascript'>
    dp.SyntaxHighlighter.BloggerMode();  
    dp.SyntaxHighlighter.HighlightAll('code');
</script>  
```

Now, if you are using some versions of Firefox (3.0.10 I know for certain has the issue, I've heard 3.0.5 also has the problem, but your mileage may vary) you won't see any highlighting even when the HTML is formatted correctly. This is due to a problem parsing the .css files since I am using the ones stored directly at Google Code (and not on my own host). A simple fix is to remove the Strict DOCTYPE tag at the top of the HTML template. I found this fixed the problem immediately.  
  
Click "Save Template" next, and you're all done!   
  
In order to activate syntax highlighting, use the following HTML in your next post:  
  
``` html    
    
<pre name="code" class"xml">
    ...content goes here...
    ...remember to find/replace all instances of...
    ...< with &lt; and > with &gt;
    ...(regardless of language) prior to publishing...
</pre>

```

That's it!  
  
Here's some other examples:  

``` html    
// Java
public static void main(String args[])
{
    System.out.println("Hello World!");
}

-- SQL
SELECT
    Id,
    COUNT(Value) As Total
FROM
    Test
WHERE
    Id <> 0
GROUP BY
    Id
ORDER BY
    Id ASC

// C#
class Test
{
   public int Value {get; set;}
}

/* CSS */
p.first{ color: blue; }
```

I hope this saves somebody a little bit of headache.

UPDATE: This site now uses Markdown, but I wanted to keep these notes around for others who might need it.
