'''
'@author James Whitcroft
'@update 1:18 PM 11/25/2016
'''
import os
import re
import sys
import sqlite3
import datetime
import time

def grabUsers2(launch,root):
	try:
		l=[]
		os.chdir(root)
		os.system('dir '+str(root)+'Users > '+str(launch+'\\ResidualWeb')+'\\userDump.txt')
		os.chdir(launch+'\\ResidualWeb')
		fh=open('userDump.txt','r')
		for line in fh:
			if len(line.split())>0:
				if not 'Volume' in line:
					if not '.' in line:
						if not 'Public' in line:
							if not 'bytes' in line:
								if not 'Directory' in line:
									l.append(line.split()[4])
	except:
		return []
	return l

'''
returns a list of active users
caller must check if null before accessing 
@input launch the directory program is launched from
@input root the target drive
'''
def grabUsers(launch,root):
	try:
		potentials=[]
		actives=[]
		os.chdir(root)
		os.system('net user > '+str(launch+'\\ResidualWeb')+'\\userDump.txt')
		fh=open('userDump.txt','r')
		for line in fh:
			if not '---' in line:
				if not 'User accounts' in line:
					if not 'command completed' in line:
						l=line.split()
						potentials.extend(l)
		#active?
		os.chdir(launch)
		for user in potentials:
			os.system('net user '+str(user)+' > activeUsersCheck.txt')
			fhtwo=open('activeUsersCheck.txt', 'r')
			for line in fhtwo:
				if 'Account active' in line:
					h=line.split()
					#print(h)
					if (h[2]=='Yes') or (h[2]=='yes'):
						actives.append(user.lower())
		fh.close()
		fhtwo.close()
		return actives
	except:
		print('Something went wrong::Exiting')
		input()
		sys.exit(-1)
		
'''
Validate a windows user exists by locating user profile
'''	
def checkUserExist(root, user):
	if os.path.exists(str(root)+'Users\\'+str(user)):
		return True
	return False

'''
Read fire fox sqlite database, in case chrome isnt installed
@input launch the directory program is launched from
@input root the target drive
@input user, the user to look for
'''
def readFirefoxHistory(launch, root, user):
	l=[]
	path=[]
	cachelist=[]
	forms=[]
	os.chdir(root)
	os.system('dir /s places.sqlite > '+str(launch+'\\ResidualWeb')+'\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
				if 'Firefox' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line):
						if root in line:
							l=line.split()		#path at l[2]

	fh.close()
	if not len(l)>0:
		return([],[])
	path.append(str(l[2])+'/places.sqlite')
	path.append(str(l[2])+'/formhistory.sqlite')
	if len(path)>0:
		conn=sqlite3.connect(path[0])
		cc=conn.cursor()
		#urls
		for entry in cc.execute('SELECT datetime(moz_historyvisits.visit_date/1000000, "unixepoch", "localtime"), moz_places.url,'
								'datetime(moz_places.last_visit_date/1000000, "unixepoch", "localtime"), moz_places.visit_count '
								'FROM moz_places, moz_historyvisits WHERE moz_places.id = moz_historyvisits.place_id'):
			#print(entry)
			cachelist.append(entry)
			
		
		conn=sqlite3.connect(path[1])
		cc=conn.cursor()
		#user input into forms
		for entry in cc.execute('SELECT datetime((firstUsed/1000000), "unixepoch","localtime"), value,'
								'datetime((lastUsed/1000000), "unixepoch","localtime"),'
								' timesUsed, fieldName FROM moz_formhistory'):
			#print(entry)
			forms.append(entry)
		
		
	return(forms, cachelist)

'''
Read chrome sqlite database, in case firefox isnt installed
@input launch the directory program is launched from
@input root the target drive
@input user, the user to look for
'''	
def readChromeHistory(launch, root, user):
	l=[]
	path=[]
	cachelist=[]
	downs=[]
	forms=[]
	os.chdir(root)
	os.system('dir /s History > '+str(launch+'\\ResidualWeb')+'\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
				if 'Chrome' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line): 
						if root in line:
							l=line.split()		#path at l[2]+l[3]
	
	fh.close()
	if not len(l)>0:
		return([],[])
	os.chdir(str(l[2])+' '+str(l[3]))
	os.system('copy History '+str(launch)+'\\ResidualWeb >>NULL')
	os.system('copy Cookies '+str(launch)+'\\Cookies >>NULL')
	#print(str(l[2])+' '+str(l[3])+'\\History '+str(launch)+'\\ResidualWeb')
	path.append(str(launch)+'\\ResidualWeb\\History')
	path.append(str(launch)+'\\ResidualWeb\\Cookies')
	#path.append(str(l[2])+' '+str(l[3])+'\\History')
	if len(path)>0:
		con=sqlite3.connect(path[0])
		c=con.cursor()
		#downloads
		for entry in c.execute('select datetime((downloads.start_time/1000000-11644473600), "unixepoch"),'
									'current_path, total_bytes, tab_url FROM downloads'):
			#print(entry)
			if not entry==None:
				downs.append(entry)
		#urls
		for entry in c.execute('select datetime((visits.visit_time/1000000-11644473600), "unixepoch"), urls.url,'
										' datetime((urls.last_visit_time/1000000-11644473600), "unixepoch"), '
										'urls.visit_count FROM urls, visits where urls.id = visits.url'):
			#print(entry)
			if not entry==None:
				cachelist.append(entry)
		#form input
		for entry in c.execute('select lower_term from keyword_search_terms'):
			if not entry==None:
				suffix=['?']
				f=suffix+list(entry)
				f.append(1)
				f.append('Chrome')
				forms.append(tuple(f))
				f=[]

	else:	
		return (downs,cachelist,forms)
	return (downs,cachelist,forms)


def cookieDump(launch,root,user):
	l=[]
	path=[]
	os.chdir(root)
	os.system('dir /s Cookies > '+str(launch+'\\ResidualWeb')+'\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	cook=open('ResidualCookies'+str(user)+'.txt','a')
	for line in fh:
		if 'Directory of' in line:
				if 'Chrome' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line): 
						if root in line:
							l=line.split()		#path at l[2]+l[3]
	
	fh.close()
	if not len(l)>0:
		return([],[])
	os.chdir(str(l[2])+' '+str(l[3]))
	#print(str(l[2])+' '+str(l[3]))
	os.system('copy Cookies '+str(launch)+'\\ResidualWeb\\Cookies >>NULL')
	path.append(str(launch)+'\\ResidualWeb\\Cookies')
	if len(path)>0:
		con=sqlite3.connect(path[0])
		c=con.cursor()
		#cookies
		for entry in c.execute('select * from cookies'):
			#print(entry)
			if not entry==None:
				cook.write('\n::Dump:: '+str(entry))
		con.close()
	#moz
	l=[]
	path=[]
	os.chdir(root)
	os.system('dir /s cookies.sqlite > '+str(launch+'\\ResidualWeb')+'\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
				if 'Firefox' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line):
						if root in line:
							l=line.split()		#path at l[2]

	fh.close()
	if not len(l)>0:
		return([],[])
	path.append(str(l[2])+'\\cookies.sqlite')
	if len(path)>0:
		conn=sqlite3.connect(path[0])
		cc=conn.cursor()
		#cookies
		for entry in cc.execute('select * from moz_cookies'):
			#print(entry)
			cook.write('\n::Dump:: '+str(entry))
	
	conn.close()
	return
'''
find drives on running box
@return a  list of drives found on box running program
'''
def findDrives():
	return re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)

'''
removes the clutter from launch drive
@input launch, the drive that the program is running on
'''	
def cleanUp(launch):
	os.chdir(launch+'\\ResidualWeb')
	if os.path.exists('cache2Finder.txt'):
		os.remove('cache2Finder.txt')
	if os.path.exists('activeUsersCheck.txt'):
		os.remove('activeUsersCheck.txt')
	if os.path.exists('userDump.txt'):
		os.remove('userDump.txt')
	if os.path.exists('History'):
		os.remove('History')
	if os.path.exists('downFinder.txt'):
		os.remove('downFinder.txt')
	if os.path.exists('Cookies'):
		os.remove('Cookies')
'''
writes html to a file and leaves it on launch drive
for future analysis
@input launch, the drive that the program was launched from
@input user, the user who was processed
'''
def htmlCreater(launch, user):
	os.chdir(launch+'\\ResidualWeb')
	if os.path.exists('residualRender'+str(user)+'.html'):
		os.remove('residualRender'+str(user)+'.html')
	fh=open('residualRender'+str(user)+'.html','w')
	fh.write('<!DOCTYPE html>\n'+
		'<html>\n'+
		'<head>\n'+
		'<meta charset="utf-8">\n'+
		'<style>\n'+

		'.node {\n'+
		'  cursor: pointer;\n'+
		'}\n'+

		'.node circle {\n'+
		'  fill: #fff;\n'+
		'  stroke: green;\n'+
		'  stroke-width: 1.5px;\n'+
		'}\n'+

		'.node text {\n'+
		'  font: 10px sans-serif;\n'+
		'}\n'+

		'.link {\n'+
		'  fill: none;\n'+
		'  stroke: #ccc;\n'+
		'  stroke-width: 1.5px;\n'+
		'}\n'+

		'</style>\n'+
		'</head>\n'+
		'<body>\n'+
		'<script src="https://d3js.org/d3.v2.min.js"></script>\n'+
		'<script>\n'+

		'var margin = {top: 20, right: 120, bottom: 20, left: 120},\n'+
		'	width = 960 - margin.right - margin.left,\n'+
		'	height = 800 - margin.top - margin.bottom;\n'+

		'var i = 0,\n'+
		'	duration = 750,\n'+
		'	root;\n'+

		'var tree = d3.layout.tree()\n'+
		'	.size([height*3, width*2]);\n'+

		'var diagonal = d3.svg.diagonal()\n'+
		'	.projection(function(d) { return [d.y, d.x]; });\n'+

		'var svg = d3.select("body").append("svg")\n'+
		'	.attr("width", width*3 + margin.right + margin.left)\n'+
		'	.attr("height", height*3 + margin.top + margin.bottom)\n'+
		'	.append("g")\n'+
		'		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");\n'+

		'd3.json("ResidualRender'+user+'.json", function(Dates) {\n'+

		'  root = Dates;\n'+
		'  root.x0 = height / 2;\n'+
		'  root.y0 = 0;\n'+

		'  function collapse(d) {\n'+
		'	if (d.children) {\n'+
		'	  d._children = d.children;\n'+
		'	  d._children.forEach(collapse);\n'+
		'	  d.children = null;\n'+
		'	}\n'+
		'  }\n'+

		'  root.children.forEach(collapse);\n'+
		'  update(root);\n'+
		'});\n'+

		'd3.select(self.frameElement).style("height", "800px");\n'+

		'function update(source) {\n'+

		'  var nodes = tree.nodes(root).reverse(),\n'+
		'	  links = tree.links(nodes);\n'+

		'  nodes.forEach(function(d) { d.y = d.depth * 380; });\n'+

		'  var node = svg.selectAll("g.node")\n'+
		'	  .data(nodes, function(d) { return d.id || (d.id = ++i); });\n'+

		'  var nodeEnter = node.enter().append("g")\n'+
		'	  .attr("class", "node")\n'+
		'	  .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })\n'+
		'	  .on("click", click);\n'+

		'  nodeEnter.append("circle")\n'+
		'	  .attr("r", 1e-6)\n'+
		'	  .style("fill", function(d) { return d._children ? "blue" : "#fff"; });\n'+

		'  nodeEnter.append("text")\n'+
		'	  .attr("x", function(d) { return d.children || d._children ? -10 : 10; })\n'+
		'	  .attr("y", function(d) { return d.children || d._children ? -15 : 0; })\n'+
		'	  .attr("dy", ".35em")\n'+
		'	  .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })\n'+
		'	  .text(function(d) { return d.name; })\n'+
		'	  .style("fill-opacity", 1e-6);\n'+

		'  var nodeUpdate = node.transition()\n'+
		'	  .duration(duration)\n'+
		'	  .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });\n'+

		'  nodeUpdate.select("circle")\n'+
		'	  .attr("r", 6.5)\n'+
		'	  .style("fill", function(d) { return d._children ? "blue" : "#fff"; });\n'+

		'  nodeUpdate.select("text")\n'+
		'	  .style("fill-opacity", 1);\n'+

		'  var nodeExit = node.exit().transition()\n'+
		'	  .duration(duration)\n'+
		'	  .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })\n'+
		'	  .remove();\n'+

		'  nodeExit.select("circle")\n'+
		'	  .attr("r", 1e-6);\n'+

		'  nodeExit.select("text")\n'+
		'	  .style("fill-opacity", 1e-6);\n'+

		'  var link = svg.selectAll("path.link")\n'+
		'	  .data(links, function(d) { return d.target.id; });\n'+

		'  link.enter().insert("path", "g")\n'+
		'	  .attr("class", "link")\n'+
		'	  .attr("d", function(d) {\n'+
		'		var o = {x: source.x0, y: source.y0};\n'+
		'		return diagonal({source: o, target: o});\n'+
		'	  });\n'+

		'  link.transition()\n'+
		'	  .duration(duration)\n'+
		'	  .attr("d", diagonal);\n'+

		'  link.exit().transition()\n'+
		'	  .duration(duration)\n'+
		'	  .attr("d", function(d) {\n'+
		'		var o = {x: source.x, y: source.y};\n'+
		'		return diagonal({source: o, target: o});\n'+
		'	  })\n'+
		'	  .remove();\n'+

		'  nodes.forEach(function(d) {\n'+
		'	d.x0 = d.x;\n'+
		'	d.y0 = d.y;\n'+
		'  });\n'+
		'}\n'+

		'function click(d) {\n'+
		'  if (d.children) {\n'+
		'	d._children = d.children;\n'+
		'	d.children = null;\n'+
		'  } else {\n'+
		'	d.children = d._children;\n'+
		'	d._children = null;\n'+
		'  }\n'+
		'  update(d);\n'+
		'}\n'+

		'</script>\n'+
		'</body>\n'+
		'</html>\n')
	fh.close()


'''
formats database queries in dictionaries with date-row format
@input coupleOfTuples tuple formatted ((moz downloads),(moz urls),(chrome downloads),(chrome urls),(form input))
@input list, list of indexes for set values in coupleOfTuples
'''
def dictMaker(coupleOfTuples,list):
	ret={}
	adders=[]
	for x in list:
		if len(coupleOfTuples[x])>0:
			for y in range(0,len(coupleOfTuples[x])):
				if len(coupleOfTuples[x][y])>0:
					if not coupleOfTuples[x][y][0].split()[0] in ret.keys():
						ret[coupleOfTuples[x][y][0].split()[0]]=[coupleOfTuples[x][y]]
					else:
						for tup in ret[coupleOfTuples[x][y][0].split()[0]]:
							if not coupleOfTuples[x][y][1] in tup:
								adders.append(coupleOfTuples[x][y])
								break
						ret[coupleOfTuples[x][y][0].split()[0]]=ret[coupleOfTuples[x][y][0].split()[0]]+adders
						adders=[]
	return ret

'''
produces json file in location of residualRender.py with filename residualRender<user>.json
@input launch, the launch location of the program
@input coupleOfTuples tuple formatted ((moz downloads),(moz urls),(chrome downloads),(chrome urls),(form input))
@input user, the user being processed
'''
def jsonCode(launch, coupleOfTuples, user):
	downs=dictMaker(coupleOfTuples,[0,2])
	hist=dictMaker(coupleOfTuples,[1,3])
	form=dictMaker(coupleOfTuples,[4])
	
	os.chdir(launch+'\\ResidualWeb')
	if os.path.exists('residualRender'+user+'.json'):
		os.remove('residualRender'+user+'.json')
	fh=open('residualRender'+user+'.json','a')
	count3=1
	fh.write('{"name":"Records Found", "children": [')
	for leaf in ['Downloads','History','Form Input']:
		count1=1
		count2=1
		fh.write('{"name":"'+leaf+'","children":[')
		
		if leaf=='Downloads':
			for date in sorted(downs.keys()):
				fh.write('{"name":"'+date+'","children":[')
				for url in downs[date]:
					fh.write('{"name":"'+url[1].replace('\\','/')+'","children" : [')
					for meta in range(2,len(url)):
						if meta==len(url)-1:
							fh.write('{"name":"Target Path: '+str(url[meta]).replace('\\','/')+'"}')
						else:
							fh.write('{"name":"Total Bytes: '+str(url[meta])+'"},')
					if count1==len(downs[date]):
						fh.write(']}')
						count1=1
					else:
						fh.write(']},')
						count1=count1+1
				if count2==len(downs.keys()):
					fh.write(']}')
					count2=1
				else:
					fh.write(']},')
					count2=count2+1

			if count3==2:
				fh.write(']}')
			else:
				fh.write(']},')
				count3=count3+1
				
		if leaf=='History':
			for date in sorted(hist.keys()):
				fh.write('{"name":"'+date+'","children":[')
				for url in hist[date]:
					fh.write('{"name":"'+url[1].replace('\\','/')+'","children":[')
					for meta in range(2,len(url)):
						if meta==len(url)-1:
							fh.write('{"name":"Visit Count: '+str(url[meta]).replace('\\','/')+'"}')
						else:
							fh.write('{"name":"Last Visited: '+str(url[meta]).replace('\\','/')+'"},')
					if count1==len(hist[date]):
						fh.write(']}')
						count1=1
					else:
						fh.write(']},')
						count1=count1+1
				if count2==len(hist.keys()):
					fh.write(']}')
					count2=1
				else:
					fh.write(']},')
					count2=count2+1
			if count3==3:
				fh.write(']}')
			else:
				fh.write(']},')
				count3=count3+1
				
				
				
		if leaf=='Form Input':
			for date in sorted(form.keys()):
				fh.write('{"name":"'+date+'","children":[')
				for url in form[date]:
					fh.write('{"name":"'+url[1].replace('\\','/')+'","children":[')
					for meta in range(2,len(url)):
						if meta==len(url)-1:
							fh.write('{"name":"Input Field: '+str(url[meta]).replace('\\','/')+'"}')
						elif meta==len(url)-2:
							fh.write('{"name":"Input Count: '+str(url[meta]).replace('\\','/')+'"},')
						else:
							fh.write('{"name":"Last Used: '+str(url[meta]).replace('\\','/')+'"},')
					if count1==len(form[date]):
						fh.write(']}')
						count1=1
					else:
						fh.write(']},')
						count1=count1+1
				if count2==len(form.keys()):
					fh.write(']}')
					count2=1
				else:
					fh.write(']},')
					count2=count2+1

			if count3==3:
				fh.write(']}')
			else:
				fh.write(']},')
				count3=count3+1
				
				
	fh.write(']}')

'''
searches keyword provided by user, prints to screen and exits
@input launch, the launch location of program
@input root, the target drive
@input user, the user being processed
@input key, the keyword to search for
@input log file handle
'''
def searchER(launch,root,user,key,log):
	st=time.time()
	log.write('\n::Term search start:: '+str(datetime.datetime.now()))
	l=[]
	path=[]
	cachelist=[]
	downs=[]
	os.chdir(root)
	os.system('dir /s History > '+str(launch)+'\\ResidualWeb\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
				if 'Chrome' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line): 
						if root in line:
							l=line.split()		#path at l[2]+l[3]
	
	fh.close()
	if len(l)>0:
		path.append(str(l[2])+' '+str(l[3])+'\\History')
		if len(path)>0:
			con=sqlite3.connect(path[0])
			c=con.cursor()
		i=1
		print('\nFrom Chrome::\n')
		log.write('\nFrom Chrome::\n')
		try:
			for entry in c.execute('select count(url) from urls where url like "%'+key+'%"'):
				log.write('The keyword ::'+str(key)+':: has been found ::'+str(entry[0])+':: time(s)\n')
				print('The keyword ::'+str(key)+':: has been found ::'+str(entry[0])+':: time(s)\n')
			for entry in c.execute('select url from urls where url like "%'+key+'%"'):
				print(str(i)+':: '+entry[0]+'\n')
				log.write(str(i)+':: '+entry[0]+'\n')
				i=i+1
		except:
			print('\nFrom Chrome::\n')
			log.write('\nFrom Chrome::\n')
			print('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
			log.write('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
		
	else:
		print('\nFrom Chrome::\n')
		log.write('\nFrom Chrome::\n')
		print('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
		log.write('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
	
	print('\n\n')
	l=[]
	path=[]
	cachelist=[]
	forms=[]
	os.chdir(root)
	os.system('dir /s places.sqlite > '+str(launch)+'\\ResidualWeb\\cache2Finder.txt')
	os.chdir(launch+'\\ResidualWeb')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
				if 'Firefox' in line:
					if (user.lower() in line) or (user.upper() in line) or (user.capitalize() in line):
						if root in line:
							l=line.split()		#path at l[2]

	fh.close()
	if len(l)>0:
		path.append(str(l[2])+'\\places.sqlite')
		if len(path)>0:
			i=1
			conn=sqlite3.connect(path[0])
			cc=conn.cursor()
			print('From Firefox::\n')
			log.write('From Firefox::\n')
			try:
				for entry in cc.execute('select count(url) from moz_places where url like "%'+key+'%"'):
					print('The keyword ::'+str(key)+':: has been found ::'+str(entry[0])+':: time(s)\n')
					log.write('The keyword ::'+str(key)+':: has been found ::'+str(entry[0])+':: time(s)\n')
				for entry in cc.execute('select url from moz_places where url like "%'+str(key)+'%"'):
					print(str(i)+':: '+entry[0]+'\n')
					log.write(str(i)+':: '+entry[0]+'\n')
					i=i+1
			except:
				print('From Firefox::\n')
				log.write('From Firefox::\n')
				print('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
				log.write('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')

		
	else:
		print('From Firefox::\n')
		log.write('From Firefox::\n')
		print('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')
		log.write('The keyword ::'+str(key)+':: has been found ::0:: time(s)\n')

	log.write('::Time Elapsed:: '+str(time.time()-st)+' seconds')
	return

'''
main function allows user to select drive and validates user provided
'''
def main():
	launch=os.getcwd()
	if not os.path.exists(launch+'\\ResidualWeb'):
		os.mkdir(launch+'\\ResidualWeb')
	log=open(launch+'\\ResidualWeb\\ResidualLog.txt','a')
	log.write('\n\n::BEGIN TEST::\n\n::Start time:: '+str(datetime.datetime.now()))
	log.write('\n\n::Launched from:: '+str(launch))
	start=time.time()
	drives=findDrives()
	i=1
	ilist=[]
	print('\nTarget Drive Options...\n----------')
	for d in drives:
		print('| '+str(i)+' | '+d.replace('\\','')+' |')
		print('----------')
		ilist.append(str(i))
		i+=1
	ui=input('\nDrive selection # : ')
	if not ui in ilist:
		print('Invalid option')
		input()
		os.system('cls')
		main()
	root=drives[int(ui)-1]
	log.write('\n\n::Drive selection:: '+str(root))
	try:
		os.chdir(root)
	except:
		log.write('\nSomething went wrong:: Exiting\n')
		print('Something went wrong:: Exiting')
		input('Press Enter')
		log.close()
		sys.exit(-1)
	#options=grabUsers(launch,root)
	options=grabUsers2(launch,root)
	print('\n---------\nPotential Users\n---------')
	for o in options:
		print('| '+str(o)+' |')
	print('---------')
	usr=input('\nUser name: ')
	if len(usr)<1:
		os.system('cls')
		main()
	if not checkUserExist(root,usr):
		print('User ::'+str(usr)+':: Does Not Exist')
		input()
		os.system('cls')
		main()
	log.write('\n\n::User selected:: '+str(usr))
	looper(launch,root,usr,log)
	log.write('\n\n::Time Elapsed:: '+str(time.time()-start)+' seconds\n\n::END TEST::\n')
	log.close()
	sys.exit()
	
	
'''
does the work
'''
def looper(launch,root,usr,log):
	print('\n-------------------\n| 1 | Term Search |'
			'\n-------------------\n| 2 | Full Search |'
			'\n-------------------\n| 3 | Cookie Dump |'
			'\n-------------------\n| 4 | Exit        |'
			'\n-------------------')
	ui=input('\n# : ')
	if ui=='1':
		ui=input('\nTerm to search: ')
		if len(ui)<1:
			os.system('cls')
			looper(launch,root,usr,log)
		log.write('\n\n::Term Search:: '+str(ui))
		searchER(launch,root,usr,ui,log)
		cleanUp(launch)
		print('\nType q or quit to Quit')
		q=input('\nHit Enter to continue\n::')
		if q in ('q','Q','quit','Quit'):
			log.write('\n\n::User Quit:: '+str(datetime.datetime.now())+'\n')
			log.close()
			sys.exit(1)
		else:
			os.system('cls')
			looper(launch,root,usr,log)
		
	elif ui=='2':
		try:
			log.write('\n\n::Attempting Full Search::'+str(datetime.datetime.now()))
			print('\n\n::Attempting Full Search::')
			testTime=time.time()
			for u in usr.split():
				fire=readFirefoxHistory(launch, root, u)
				chrome=readChromeHistory(launch, root, u)
				htmlCreater(launch, u)
				if (len(chrome[0])+len(chrome[1])+len(chrome[2])>0) and (len(fire[0])+len(fire[1])>0):
					jsonCode(launch, ((),fire[1],chrome[0],chrome[1],fire[0]+chrome[2]),u)
				elif (len(chrome[0])+len(chrome[1])+len(chrome[2])>0):
					jsonCode(launch, ((),(),chrome[0],chrome[1],chrome[2]),u)
				elif (len(fire[0])+len(fire[1])>0):
					jsonCode(launch, ((),fire[1],(),(),fire[0]),u)
				else:
					jsonCode(launch,((),(),(),(),()),u)
		except:
			print('Something went wrong::Exiting...')
			log.write('\n\nSomething went wrong::Exiting...\n')
			input()
			log.write('\n\n::End:: '+str(datetime.datetime.now())+'\n')
			log.close()
			cleanUp(launch)
			sys.exit(-1)
		cleanUp(launch)
		print('::Done::')
		log.write('\n\n::Time Elapsed:: '+str(time.time()-testTime)+' seconds\n\n::Done::')
		input()
		os.system('cls')
		looper(launch,root,usr,log)
		return
	elif ui=='3':
		st=datetime.datetime.now()
		testTime=time.time()
		log.write('\n\n::Cookie Dump:: '+str(st))
		cookieDump(launch,root,usr)
		log.write('\n\n::Time Elapsed:: '+str(time.time()-testTime)+' seconds')
		print('::Done::')
		input()
		os.system('cls')
		looper(launch,root,usr,log)
		return
	elif ui=='4':
		log.write('\n\n::User Quit:: '+str(datetime.datetime.now())+'\n')
		log.close()
		cleanUp(launch)
		sys.exit(-1)
		return
	else:
		os.system('cls')
		print('Invalid option')
		looper(launch,root,usr, log)
	
	
#running on windows?
if sys.platform.startswith('win'):
	main()
else:
	print('Invalid platform; try Windows')
	sys.exit(-1)
