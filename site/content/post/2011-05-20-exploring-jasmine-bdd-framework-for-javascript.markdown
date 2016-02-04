+++
author = "karlgrz"
comments = true
date = "2011-05-20T21:37:00"
slug = "exploring-jasmine-bdd-framework-for-javascript"
title = "Exploring Jasmine BDD Framework for Javascript"
categories = ["Coding"]
tags = ["bdd", "jasmine", "javascript"]
+++

It has been AGES since I've put anything down on paper. I remember when I was at least writing something here (...anything) that my communication skills only improved. I can tell in the past year my skills have deteriorated a bit as I have not been required to write as much. This must be remedied, and I've found a great candidate that I think both is personally applicable and hopefully will benefit someone out there as well. There will hopefully be a seperate string of posts outlining my new experiences and journeys in the start-up world, but that can wait for the time being.

And let's get at it!

I recently have been doing a lot of Javascript development at work. After speaking with some coworkers and developer friends of mine, there seems to be a an impetus to better organize Javascript source files. I know from my experience that I've been in situations, both professionally and in my own side-projects, where my JS files just grow and grow like a wildebeast. Other times, I have a difficult time validating that my logic has been correctly implemented. On the server side it's usually a lot easier to validate behavior, either through proper testing or looking at values in a database or many other means. With Javascript, usually you have to fire up the browser and physically navigate through your page in order to visually validate the behavior you are expecting.

This technique stinks. I know I always forget to check something or leave something off or, worse, introduce regression bugs into my scripts. Bad, Karl.

Jasmine ([http://pivotal.github.com/jasmine](http://pivotal.github.com/jasmine)) appears to at least help facilitate BDD when writing Javascript. I've played around with it a little bit and have found it to be quite nice for designing Javascript, and hopefully will give me newfound confidence in the scripts I write.

Judge for yourself, though. I am but one developer who has had a decent introductory experience. Try the tool out for yourself and see if it helps your workflow.

For discussion sake I created a very simple spec. Let's say we want to have an image editor, with very simple requirements.

ImageEditor
-----------
- Should be able to open an image from URL
- When an image is opened, Should show controls for editing the image
- When an image is opened, Should be able to close the image
- When no image is opened, throw an exception if try to close

So, super simple spec, but a spec nonetheless. We're given four requirements to implement in our Javascript code.

To start, I'm going to download the latest standalone release of jasmine (as of May 20th, 2011, that was 1.0.2) here ([http://pivotal.github.com/jasmine/download.html](http://pivotal.github.com/jasmine/download.html)). If you have a Ruby project you will be working with there is a Jasmine Gem, but to keep things language agnostic I'm not going to make any assumptions.

The zip comes with some example specs and .js files, which I basically followed along with in this post. Nothing fancy, just a "Hello, world", which is basically what I'm showing you here.

First thing to take a look at is spec/SpecRunner.html.

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/1.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/1.PNG)

When you first load the page, it runs your tests and shows you the results, either green if they all pass or red for any failures. Standard test fare. You can click "Show passed" checkbox to drill down into each individual test.

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/2.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/2.PNG)

Nice and clean.

Ok, so let's start coding some Javascript!

Our first spec is "Should be able to open an image from URL". So let's write an ImageSpec.js spec first:

**_ImageSpec.js_**

``` javascript
describe("Image", function() {
	var image;

	beforeEach(function() {
		image = new Image();
	});

	it("should be able to set an image url", function() {
		var url = "http://www.google.com/images/logo_sm.gif";
		image.load(url);
		expect(image.url).toEqual(url);
	});
});
```

Notice the language that Jasmine uses. The **describe** function is used to encapsulate a suite of tests. The **it** function specifies your test. This makes your test code read VERY similarly to your spec.

We're going to add a reference to SpecRunner.html for our new ImageSpec.js file. It looks like this:

**_SpecRunner.html_**
``` html
<html>
    <head>
        <title>Jasmine Test Runner</title>
        <link rel="stylesheet" type="text/css" href="lib/jasmine-1.0.2/jasmine.css">
        <script type="text/javascript" src="lib/jasmine-1.0.2/jasmine.js"></script>
        <script type="text/javascript" src="lib/jasmine-1.0.2/jasmine-html.js"></script>
        <!-- include source files here... -->
        <!-- include spec files here... -->
        <script type="text/javascript" src="spec/SpecHelper.js"></script>
        <script type="text/javascript" src="spec/ImageSpec.js"></script>
    </head>
    <body>
        <script type="text/javascript">
            jasmine.getEnv().addReporter(new jasmine.TrivialReporter());
            jasmine.getEnv().execute();
        </script>
    </body>
</html>
```

Running this spec we should see 1 failure:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/3.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/3.PNG)

Which we do. Ok, now let's write the code to make this pass.

**_Image.js_**
``` javascript
function Image() {
}

Image.prototype.load = function(url) {
	this.url = url;
}
```

Ok, now we have to add the following line to our SpecRunner.html in order to load our script:

**_SpecRunner.html_**
``` html
<script type="text/javascript" src="src/Image.js"></script>
```

And this is where my first gripe with Jasmine comes in: in a large project, I can have MANY Javascript files. This means I'm going to be editing this SpecRunner.html file A LOT while I'm developing. Weak. Apparently, the Ruby Gem eliminates this problem, and I'm willing to bet there are plugins out there that will alleviate this pain on agnostic projects. For the time being though it's just something to keep in mind that I thought was annoying.

After we run our test now we should see green:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/4.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/4.PNG)

And it passes. Alright, let's move onto the ImageEditor.

Our next spec states: When an image is opened, should show controls for editing the image.

Ok, let's write a test.

**_ImageEditorSpec.js_**
``` javascript
describe("ImageEditor", function() {
	var imageEditor;
	var image;

	beforeEach(function() {
		imageEditor = new ImageEditor();
		image = new Image();
	});

	it("should be able to open an image from URL", function() {
		imageEditor.open(image);
		expect(imageEditor.currentImage).toEqual(image);
	});
});
```

Now we need to add the following line to our SpecRunner.html (somewhat annoyed with that yet? You might be...):

**_SpecRunner.html_**
``` html
    <script type="text/javascript" src="spec/ImageEditorSpec.js"></script>
```

Run the tests, and should have a failure:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/5.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/5.PNG)

Ok, let's pass this test.

**_ImageEditor.js_**
``` javascript
function ImageEditor() {
}

ImageEditor.prototype.open = function(image) {
	this.currentImage = image;
}
```

Now we run the test:

Still fails. D'oh! We forgot to add the ImageEditor.js file to our SpecRunner.html file! Are you really annoyed with that yet? (I know I am...)

**_SpecRunner.html_**
``` html
<script type="text/javascript" src="src/ImageEditor.js"></script>
```

Ok, now let's run the test:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/6.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/6.PNG)

Green. Passed.

Ok, so we've opened the image. But there's still part of the spec that isn't implemented: should show controls for editing the image.

Ok, let's use Jasmine's spyOn function to monitor when functions are called.

Here's our test:

**_ImageEditorSpec.js_**
``` javascript
it("should show controls when an image is opened", function() {
	spyOn(imageEditor, 'showControls');

	imageEditor.open(image);

	expect(imageEditor.showControls).toHaveBeenCalledWith(true);
});
```

To me, I relate this to something similar to a Stub in Rhino.Mocks. I just want to make sure my function gets called when the image is opened. This will of course fail until we implement.

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/7.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/7.PNG)

So let's implement this behavior:

**_ImageEditor.js**_
``` javascript
ImageEditor.prototype.open = function(image) {
	this.currentImage = image;
	this.showControls(true);
}

ImageEditor.prototype.showControls = function(showControls) {
	this.isShowControls = showControls;
}
```

As you can see, the open function now calls showControls, which our test will check for. In true BDD I should write a test for showControls as well, but for the sake of this blog post I will omit that. Now we run our tests and:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/8.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/8.PNG)

Tada, green.

Ok, for our last spec, let's use Jasmine's expect function to test if an exception is thrown:

- When no image is opened, throw an exception if try to close

Here's our test, where we are explicitly checking for an exception:

**_ImageEditorSpec.js_**
``` javascript
describe("#close", function() {
    it("should throw an exception if image editor already closed", function() {
	expect(function() {
		imageEditor.close();
	}).toThrow("image editor already closed");
    });
});
```

I love the way this reads. It's pure Javascript, but to me it's extremely straightforward and doesn't require much in the way of picking up and going.

Running the tests should show a failure:

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/9.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/9.PNG)

Which it does fail. Let's write the code to make it pass:

**_ImageEditor.js_**
``` javascript
ImageEditor.prototype.close = function() {
    if(!this.currentImage) {
        throw new Error('image editor already closed');
    }

    this.currentImage = null;
    this.showControls(false);
}
```

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/10.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/10.PNG)

Pass. As you can see in my code, there are a couple more functions that should be tested. Here is the spec I used for testing those:

**_ImageEditorSpec.js_**
``` javascript
    describe("when an image is open", function() {
        beforeEach(function() {
            imageEditor.open(image);
        });

        it("should show the editing controls", function() {
            expect(imageEditor.isShowControls).toBeTruthy();
        });

        it("should be able to close the image", function() {
            imageEditor.close();
            expect(imageEditor.currentImage).toEqual(null);
        });

        it("should hide controls when an image is closed", function() {
            spyOn(imageEditor, 'showControls');

            imageEditor.close();

            expect(imageEditor.showControls).toHaveBeenCalledWith(false);
        });
    });
```

And these all pass...

[![](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/11.PNG)](/images/2011-05-20-exploring-jasmine-bdd-framework-for-javascript/11.PNG)

If this framework improves my code even a little I will be thankful. I don't consider myself a Javascript expert by any means, but I think this tool will at least give me the confidence I need to break new ground and learn even more going forward, as well as being a lot more confident with refactorings.

In the future I hope to expand on this post with more advanced testing and implementing JQuery into my tests, as we use that library in production.
