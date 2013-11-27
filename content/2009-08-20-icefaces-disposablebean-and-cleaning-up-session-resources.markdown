author: karlgrz 
comments: true
date: 2009-08-20 18:42:00
slug: icefaces-disposablebean-and-cleaning-up-session-resources
title: ICEFaces DisposableBean and Cleaning Up Session Resources
category: Coding
tags: ICEFaces, JavaEE, javascript, JSF, Session-Management

Here's the scenario:  
  
Your user has this web application that runs a data process. Say, power through a 2GB file and run some processing on each record. Fairly straightforward back end logic, maybe aggregate a column on the file and write the total to a SQL database somewhere. Whatever.  
  
Let's say this process takes upwards of 45 minutes - 1 hour to complete, depending on the input file. In order to assure that the process finishes to completion we want to set our session timeout to be something longer than that. Let's say 2 hours, to ensure we can get through a really large file, if need be.  
  
OK, great. Where's the problem?  
  
Let's say they only want to run a very tiny file, like 10 MB, and this only takes 5 minutes to run. Why do I need to wait for 2 hours to invalidate that session if the user is done and back to surfin' the net after 5 minutes?!  
  
I wanted to have a mechanism in place for cleanup code to executed in the following two cases:  
  
1. The user's session expires naturally.  
2. The user closes their internet browser.  
  
The first one is somewhat trivial, in that JSF manages a lot of that bean clean up for us. The second one, however, proved to be quite the task in nailing down so it worked to my satisfaction. After a morning or so of research, however, I have an implementation that I like and seems to be working.  
  
Here's what I did:  
  
I'm using JSF 1.2, ICEFaces 1.8, and Tomcat 6.0. Since ICEFaces 1.7, they have included an interface with their framework called DisposableBean. What this interfaces does is define one method (dispose()) that gets called when the session is invalidated, either naturally or by application code.   
  
So let's say I have a simple session-scoped managed bean as such:  

``` java    
package com.beans;

public class Bean
{
    public Bean()
    {
        defineDescriptorList();
    }   
    
    private List<String> descriptorList;

    public List<String> getDescriptorList()
    {
        return descriptorList;
    }

    public void setDescriptorList(List<String> descriptorList)
    {
        this.descriptorList = descriptorList;
    }

    private String selectedDescriptor;

    public String getSelectedDescriptor()
    {
        return selectedDescriptor;
    }

    public void setSelectedDescriptor(String selectedDescriptor)
    {
        this.selectedDescriptor = selectedDescriptor;
    }

    private void defineDescriptorList()
    {
        descriptorList = ServiceToSetupDescriptorList(); // Return a List<String> of pertinent descriptors
    }

    public String executeProcess()
    {
        ServiceToProcessLongDataFile(getSelectedDescriptor()); // Run our data process using selectedDescriptor
        return null;
    }
}
```

In my faces-config.xml, I have the following entry to configure the JSF framework to manage this bean instance:  
  

``` xml
    
<managed-bean>
  <managed-bean-name>Bean</managed-bean-name>
  <managed-bean-class>com.beans.Bean</managed-bean-class>
  <managed-bean-scope>session</managed-bean-scope>
</managed-bean>

```
  
  
OK, so upon the first reference to Bean on the .jspx page, JSF will instantiate an instance of the Bean class using the no-argument constructor I have defined. The call to defineDescriptorList() will set up my descriptorList collection with values from a service (could be database, file, whatever...irrelevant to this conversation).  
  
OK, now, let's say that on my page I just want to fire off a huge data processing event using a parameter chosen from our descriptorList collection. This is a basic example, so I'm just storing the selected value into a string variable and using that in my bean to fire off the process. To do this I will use a selectOneMenu component. Here's my markup:  
  

``` html
<jsp:root
    jsfc="f:view"
    xmlns:jsp="http://java.sun.com/JSP/Page"
    xmlns:f="http://java.sun.com/jsf/core"
    xmlns:h="http://java.sun.com/jsf/html"
    xmlns:ice="http://www.icesoft.com/icefaces/component"
    xmlns:ui="http://java.sun.com/jsf/facelets"
    xmlns:c="http://java.sun.com/jstl/core"
    xmlns:fn="http://java.sun.com/jsp/jstl/functions"
>
    <ice:outputDeclaration
        doctypeRoot="html"
        doctypePublic="-//W3C//DTD XHTML 1.0 Transitional//EN"
        doctypeSystem="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    />
    <html>
        <head>
            <title>Descriptor Lookup Tool</title>
            <link
                rel="stylesheet"
                type="text/css"
                href="/xmlhttp/css/rime/rime.css"
            />
        </head>
        <body>
             <!-- content -->
            <h1>Descriptor Lookup Tool</h1>
            <br />
            <ice:form
                partialSubmit="true"
                rendered="true" >   
                <p>
                    <ice:panelGroup>       
                        <ice:panelGrid columns="2">
                            <ice:outputText style="font-weight: bold;" value="Descriptors" />                                                                            
                            <ice:selectOneMenu id="ddlDescriptor" partialSubmit="true" value="#{Bean.selectedDescriptor}" >                        
                                <f:selectItems id="ddlItems" value="#{Bean.descriptorList}"/>
                            </ice:selectOneMenu>
                        </ice:panelGrid>
                    </ice:panelGroup>
                </p>                        
                <p>                                                      
                    <ice:panelGrid columns="1">  
                        <ice:commandLink value="Process Data File" 
                                         action="#{Bean.executeProcess}" />
                    </ice:panelGrid>
                </p>                                                
                <p>
                    <ice:panelGrid columns="2">                            
                        <ice:messages id="errMsgs" errorClass="error" infoClass="ss_text" style="font-size:14px;" layout="table"/>
                        <ice:outputText id="txtErrors" style="font-size:14px;" value="" />                        
                    </ice:panelGrid>
                </p>                               
            </ice:form>
        </body>
    </html>
</jsp:root>

```
  
  
Great! This gives us our list for what we're trying to accomplish. However, after I run my process, which could take up to 2 hours, and I close my browser window, I'm left with a session object that is going to be laying around for potentially longer (depending on how long the session timeout is set for). When that browser window closes I wanted to run some clean up code. This is where DisposableBean interface comes in. Let's make the following changes to our Bean class:  
  
1. Implement the DisposableBean interface, which includes overriding the dispose() method and adding our logic to cleanup our bean there.  
2. Add a Logout servlet that will call the dispose() method on any or all of the managed beans we want to clean up.  
3. Add some JavaScript to our .jspx page to listen for the browser close event and navigate to the "Logout" URL, which will run our Logout servlet code.  
  
Sounds like a lot of work? It's actually not as bad as you would think, and gives us the power to ensure our resources are cleaned up if the browser is closed.  
  
Let's tackle these one at a time.  
  
First, we implement the DisposableBean interface (which is an ICEFaces interface that is included with the framework as of version 1.7) to our Bean class. Here's what our class will look like after:  

``` java
package com.beans;

import com.icesoft.faces.context.DisposableBean;

public class Bean implements DisposableBean
{
    public Bean()
    {
        defineDescriptorList();
    }   
    
    private List<String> descriptorList;

    public List<String> getDescriptorList()
    {
        return descriptorList;
    }

    public void setDescriptorList(List<String> descriptorList)
    {
        this.descriptorList = descriptorList;
    }

    private String selectedDescriptor;

    public String getSelectedDescriptor()
    {
        return selectedDescriptor;
    }

    public void setSelectedDescriptor(String selectedDescriptor)
    {
        this.selectedDescriptor = selectedDescriptor;
    }

    private void defineDescriptorList()
    {
        descriptorList = ServiceToSetupDescriptorList(); // Return a List<String> of pertinent descriptors
    }

    public String executeProcess()
    {
        ServiceToProcessLongDataFile(getSelectedDescriptor()); // Run our data process using selectedDescriptor
        return null;
    }
    
    public void dispose() throws Exception
    {
        descriptorList.clear();
    }
}
```

As you can see, we're just going to execute the clear() method on our List of descriptors in our little example to prove the concept.  
  
Next we're going to add a servlet that will control how our clean up gets executed. Here's my implementation of the Logout servlet:  

``` java    
package com.beans;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class Logout extends HttpServlet 
{
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
    {
        doPost(req, resp);
    }

    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
    {
        HttpSession session = req.getSession(false);
        if (session != null)
        {            
            try
            {
                Bean bean = (Bean)req.getSession().getAttribute("Bean");
                if(bean != null)
                {
                    bean.dispose();    
                }                                
            }
            catch (Exception e)
            {
                e.printStackTrace();
            }                        
        }
    }
}
```

In order for this code to ever be executed as is, we need to set up an instance of this Servlet in the web.xml, as well as a URL pattern to use. We do this by adding the following to web.xml:  

``` xml    
<servlet-mapping>
    <servlet-name>logoutServlet</servlet-name>
    <url-pattern>/logout</url-pattern>
</servlet-mapping>
<servlet>
    <servlet-name>logoutServlet</servlet-name>
    <servlet-class>com.beans.Logout</servlet-class>
    <load-on-startup>1</load-on-startup>
</servlet>
```

What this does is tells our application to instantiate an instance of the Logout servlet, and listen to any POSTs or GETs to any URL matching /logout. If any request is made to that URL, the Logout servlet will handle it.  
  
The last thing we want to do is add the JavaScript to our .jspx page to navigate to the /logout URL if the user closes the browser. We end up with a .jspx file that looks like so:  
  
UPDATE: This code appears to only work using IE. Since the purpose of this piece of code was to support an IE-only application it works great. However, I would like to extend this to work cross-browser at some point.  

``` html    
<jsp:root
    jsfc="f:view"
    xmlns:jsp="http://java.sun.com/JSP/Page"
    xmlns:f="http://java.sun.com/jsf/core"
    xmlns:h="http://java.sun.com/jsf/html"
    xmlns:ice="http://www.icesoft.com/icefaces/component"
    xmlns:ui="http://java.sun.com/jsf/facelets"
    xmlns:c="http://java.sun.com/jstl/core"
    xmlns:fn="http://java.sun.com/jsp/jstl/functions"
>
    <ice:outputDeclaration
        doctypeRoot="html"
        doctypePublic="-//W3C//DTD XHTML 1.0 Transitional//EN"
        doctypeSystem="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    />
    <html>
        <head>
            <title>Descriptor Lookup Tool</title>
            <link
                rel="stylesheet"
                type="text/css"
                href="/xmlhttp/css/rime/rime.css"
            />
            <!-- This JavaScript code detects the user closing their  -->
            <!-- browser window. It offers the user a choice to exit or cancel and stay on -->
            <!-- the page. If the user clicks "OK" any managed beans that implement -->
            <!-- DisposableBean will have their dispose() method called. -->
            <script type="text/javascript">
               window.onbeforeunload = function (evt) 
                {
                  var message = 'Are you sure you want to leave?';
                  if (typeof evt == 'undefined') 
                  {
                    evt = window.event;
                  }
                  if (evt) 
                  {
                    evt.returnValue = message;
                    window.navigate('./logout');
                  }
                  return message;
                }
            </script>
        </head>
        <body>
             <!-- content -->
            <h1>Descriptor Lookup Tool</h1>
            <br />
            <ice:form
                partialSubmit="true"
                rendered="true" >   
                <p>
                    <ice:panelGroup>       
                        <ice:panelGrid columns="2">
                            <ice:outputText style="font-weight: bold;" value="Descriptors" />                                                                            
                            <ice:selectOneMenu id="ddlDescriptor" partialSubmit="true" value="#{Bean.selectedDescriptor}" >                        
                                <f:selectItems id="ddlItems" value="#{Bean.descriptorList}"/>
                            </ice:selectOneMenu>
                        </ice:panelGrid>
                    </ice:panelGroup>
                </p>    
                <p>                                                      
                    <ice:panelGrid columns="1">  
                        <ice:commandLink value="Process Data File" 
                                         action="#{Bean.executeProcess}" />
                    </ice:panelGrid>
                </p>                                                
                <p>
                    <ice:panelGrid columns="2">                            
                        <ice:messages id="errMsgs" errorClass="error" infoClass="ss_text" style="font-size:14px;" layout="table"/>
                        <ice:outputText id="txtErrors" style="font-size:14px;" value="" />                        
                    </ice:panelGrid>
                </p>                               
            </ice:form>
        </body>
    </html>
</jsp:root>
```

Now, when the user clicks the red "X" to close their browser while our application is running, they will be greeted with a confirmation dialog (OK & Cancel) asking if they are sure they want to leave the application. If they click OK, the application routes to /logout, which runs our code in the Logout servlet, disposing of our Bean instance.   
  
In applications that hold a lot of data in memory for processing between page requests, this appears to be another tool to fight memory leaks. The dispose() method will be called either on browser close or when the session times out naturally, which means we are doing our part to minimize the amount of unnecessary overhead our application is using.  
  
I'm open to suggestions for better methods, but for this specific example it seems to be working great.  
  
UPDATE: I've noticed that once the session expires naturally, ICEFaces calls the bean's dispose() method a second time, even if the user closed their browser to "close" the application. Something to look into...
