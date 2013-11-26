author: karlgrz 
comments: true
date: 2009-09-17 21:45:00
slug: stream-an-excel-workbook-to-a-client
title: Stream an Excel workbook to a client
category: Coding
tags: ICEFaces, JavaEE, JSF, Servlet

A short while ago I came to a realization that the [ice:dataExporter](http://www.icefaces.org/docs/v1_8_0/tld/ice/dataExporter.html) component that I was using to export table data from my [ICEFaces](http://www.icefaces.org) application was not behaving exactly how I liked it. I noticed that when I would refresh the table (which worked great on the UI) and then re-export the file, I would get the SAME data in my output workbook. After some [Googling](http://www.google.com/search?source=ig&hl=en&rlz=&=&q=Export+excel+from+JSF&aq=f&oq=&aqi=) and [stackoverflowing](http://stackoverflow.com/search?q=Export+excel+jsf), I came up with a solution that appears to be working great for my needs. I'd like to refactor this at a later date to be more generic than this implementation, but the concept works beautifully for my particular situation.  
  
Let's start with a simple interface for our data model. We'll call it "Customer". Here's what the interface looks like:  

``` java    
package com.test;

public interface Customer
{
    public String getName();
    public String getAddress();
    public String getEmail();       
}
```
 
OK, so a couple of properties, no big deal. Just an example.  
  
We also have a managed bean that will hold a List of these Customer objects that we want to display in a table. Here's the Customer bean:  

``` java    
package com.test;

import java.util.List;
import java.util.ArrayList;

public class Bean
{
    private List<Customer> customerList;
    
    public List<Customer> getCustomerList()
    { 
        return customerList;
    }

    public void setCustomerList(List<Customer> customerList) 
    {
        this.customerList = customerList;
    }

    public Bean()
    {
        // Initialize our customerList. 
        // We're only going to make 2 Customer
        // objects and add them to our list, 
        // but you could be calling
        // a web service or querying a database 
        // for your data.
        defineCustomerList();
    }

    private List<Customer> defineCustomerList()
    {
        this.customerList = new ArrayList<Customer>();
        customerList.add(new OnlineCustomer("Karl", "123 Main St.", "kg@go.com"));
        customerList.add(new OnlineCustomer("Paul", "321 Abbey Rd.", "pg@go.com"));
    }
}
```

Again, really simple implementation just for this example. Note: OnlineCustomer is just a basic object that implements the Customer interface I spoke of earlier. I have omitted it's class structure for brevity.  
  
We need to reference the managed bean in our faces-config.xml file for our application to be able to use and reference it. Here's the entries for that in our faces-config.xml:  

``` xml    
<?xml version="1.0" encoding="UTF-8"?> 
<faces-config
    xmlns="http://java.sun.com/xml/ns/javaee"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-facesconfig_1_2.xsd"
    version="1.2">
   <managed-bean>
      <managed-bean-name>Bean</managed-bean-name>
      <managed-bean-class>com.test.Bean</managed-bean-class>
      <managed-bean-scope>session</managed-bean-scope>
   </managed-bean>  
</faces-config>
```

So we're going to have a simple .jspx that has an [ice:dataTable](http://facestutorials.icefaces.org/tutorial/dataTable-tutorial.html) component, and a button to export the table to an Excel file. Here's the markup:  

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
                <title>Excel Output Example</title>
                <link
                    rel="stylesheet"
                    type="text/css"
                    href="../xmlhttp/css/rime/rime.css"
                />
            </head>
            <body>
                <ice:form
                    partialSubmit="true"
                    rendered="true" >   
                    <ice:dataTable id="customerTable"      
                                      value="#{Bean.customerList}"
                                      rows="20"
                                      var="customer">
                        <ice:column>
                            <f:facet name="header">
                                <ice:outputText id="column1" value="Name"/>
                            </f:facet>
                            <ice:outputText id="name" value="#{customer.name}" />                                    
                        </ice:column>
                        <ice:column>
                            <f:facet name="header">
                                <ice:outputText id="column2" value="Address"/>
                            </f:facet>
                            <ice:outputText id="address" value="#{customer.address}" />                             
                        </ice:column>
                        <ice:column>
                            <f:facet name="header">
                                <ice:outputText id="column3" value="E-Mail"/>
                            </f:facet>
                            <ice:outputText id="email" value="#{customer.email}" />
                        </ice:column>
                    </ice:dataTable>      
                    <ice:outputLink value="./export" >
                        <h:outputText value="Export To Excel" />
                    </ice:outputLink>                                            
            </body>
        </html>
    </jsp:root>
```

So we have a button that is just an output link to the URL /export which we are going to configure to control our Excel output. How, you ask? We're going to write a Servlet that will handle requests to that URL and will stream an Excel workbook to the client, with the familiar "Open/Save As" dialog box your users are comfortable with.  
  
To accomplish this we need to tell our application what to do when it navigates to the URL /export. We don't want another page, since we don't want to give the user any choices, just export every customer that is currently in the List. The way we are writing this Excel class, it will output ANY class that implements the Customer interface (Note: as I mentioned above I want to refactor this later to be a bit more generic, but for this example it works fine.)  
  
OK, so first step let's write our ExportToExcel servlet. For this servlet we are going to use the [Apache POI library](http://poi.apache.org/) for writing our Excel workbook. Note that ICEFaces uses a different library ([jxl](http://jexcelapi.sourceforge.net/)) which would work fine as a substitute for POI. However, I am more comfortable with POI, hence that's why I am using it here). Here's what our servlet looks like:  

    
``` java    
package com.test;

import java.io.*;
import java.util.List;

import javax.servlet.*;
import javax.servlet.http.*;

import org.apache.poi.hssf.usermodel.HSSFRichTextString;
import org.apache.poi.hssf.usermodel.HSSFRow;
import org.apache.poi.hssf.usermodel.HSSFSheet;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;

public class ExportToExcel extends HttpServlet 
{
    private static final long serialVersionUID = 2595261807932102942L;

    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
    {
        doPost(req, resp);
    }

    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
    {
        // Get the current session for our ICEFaces application.
        // This gives us access to the session scoped managed beans
        HttpSession session = req.getSession(false);
        if (session != null)
        {
           // Retrieve the current, data-filled customerList 
           // collection from our session.
           // This will drive the data of our Excel workbook.
           List<Customer> customers = 
               ((Bean)req.getSession().getAttribute("Bean"))
                .getCustomerList(); 
           
           // In order to get the browser-native dialog box 
           // ("Open / Save As") we need to set these values
           // in the response object that this servlet will 
           // send back to the client.
           resp.setContentType("application/vnd.ms-excel");  
           resp.setHeader(
               "Content-disposition", "attachment;filename=Customers.xls");            
             
           // Our Excel workbook instance we are going to 
           // manipulate and fill with our Customer data.
           HSSFWorkbook wb = new HSSFWorkbook();  
           HSSFSheet sheet = wb.createSheet("Customers");  
           
           // Instance for a Excel worksheet row.
           HSSFRow row;  
           
           // rowNum will be used to specify which 
           // row number we are going to be manipulating
           // within the worksheet.
           int rowNum = 0;
           
           // Create a new row that represents a row in the worksheet.
           row = sheet.createRow((short)rowNum);  
           
           // Here we're just creating our header row.
           // createCell(#) allows us to reference specific 
           // cells within our worksheet.
           row.createCell((short)0)
              .setCellValue(new HSSFRichTextString("Name"));  
           row.createCell((short)1)
              .setCellValue(new HSSFRichTextString("Address"));
           row.createCell((short)2)
              .setCellValue(new HSSFRichTextString("Email"));
           
           // Increment our row to start writing out customer data 
           // from our List<Customer> collection.
           rowNum++;
           
           // Iterate over our List<Customer> to 
           // write all the data out.
           for(Customer customer:customers)
           {           
               // Create a new row that represents a row in the worksheet.
               row = sheet.createRow((short)rowNum);               
               
               // Write out the data for each Customer object.
               row.createCell((short)0)
                  .setCellValue(new HSSFRichTextString(estimate.getName()));  
               row.createCell((short)1)
                   .setCellValue(new HSSFRichTextString(estimate.getAddress()));
               row.createCell((short)2)
                  .setCellValue(new HSSFRichTextString(estimate.getEmail()));
               
               // Increment our row to start continue writing customer data 
               // from our List<Customer> collection.
               rowNum++;
           }
           
           try 
           {  
                // Create an output stream to stream data to the client.
                ServletOutputStream out = resp.getOutputStream();  
                
                // POI has a write() method on a HSSFWorkbook object 
                // that takes a ServletOutputStream as a parameter
                // and streams the contents to the client.
                wb.write(out);  
                
                out.flush();  
                out.close();  
           } 
           catch (IOException e) 
           {   
                // Print any errors to stdout
                e.printStackTrace();  
           }           
        }
    }
}
```

We call the doPost() method from our doGet() because we want the excel to be output regardless of how this page is navigated to ([commandButton](http://www.icefaces.org/docs/latest/tld/ice/commandButton.html) and [commandLink](http://www.icefaces.org/docs/v1_8_0/tld/ice/commandLink.html) use different submit methods to HTTP). Now we run the same logic regardless of how the URL is reached. Good.  
  
The last piece is to tell our application what code to run when we navigate to /export. This is done using a servlet definition and servlet URL mapping in web.xml. We will be adding the following entries:  
 
``` xml    
    <servlet>
        <servlet-name>exportServlet</servlet-name>
        <servlet-class>com.test.ExportToExcel</servlet-class>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>exportServlet</servlet-name>
        <url-pattern>/export</url-pattern>
    </servlet-mapping>
```
  
This tells my application to listen for all GET/POST requests at the URL /export, and to use the exportServlet (com.test.ExportToExcel) to process these requests.  
  
This implementation works great for streaming data from a List to an excel worksheet. I've tested this with as much as ~1,500 objects with 12 properties and found performance to be quite snappy, even with many users. Obviously this is very concrete code and should be refactored to allow for a more dynamic approach, but for this example I think it's perfect.  
  
Thoughts? Anyone have a (much) better way to implement this?
