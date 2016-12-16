Read me for **Residual Web** \- a browser history forensics tool

**This tool is intended for _Windows_ operating systems only. Any attempted use outside of _Windows_ will surely result in errors. _Requires python 3 or greater_.**

##Purpose

#####This tool will allow you to retreive cache history from firefox and/or chrome browser(s) on a Windows box. Data is sorted by date and displayed in an html document.


##Features

- Scrape
  * Browser cache
  * Form history
  * Downloads
- Term search
  * Search urls for terms
- Present
  * [ _d3.js_ ] (https://www.d3js.org) visualization
  * Quick access to important data


##Usage

- python path\_to\_file\\ResidualWeb.py
- input integer corresponding to the drive you would like to search
- enter the name of the user you would like to search
  * a list of possible users will be presented
  * if no user is input a search will be done for all presented users
- 1 : term search
  * search for term in urls
- 2 : full search
  * generate html display of analysis
- all documentation is located in ResidualRender folder created by program
- all actions are recorded to ResidualLog.txt

######For best results, run as admin
