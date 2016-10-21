import os, re

'''
returns a list of active users
caller must check if null before accessing 
'''
def grabUsers():
	#os.system('cd %HOMEPATH%')
	potentials=[]
	actives=[]
	os.system('net user > userDump.txt')
	fh=open('userDump.txt','r')
	for line in fh:
		if not '---' in line:
			if not 'User accounts' in line:
				if not 'command completed' in line:
					l=line.split()
					potentials.extend(l)
	#active?
	for user in potentials:
		os.system('net user '+str(user)+' > activeUsersCheck.txt')
		fhtwo=open('activeUsersCheck.txt', 'r')
		for line in fhtwo:
			if 'Account active' in line:
				h=line.split()
				#print(h)
				if (h[2]=='Yes') or (h[2]=='yes'):
					actives.append(user)
	fh.close()
	fhtwo.close()
	return actives

'''
check default cache locations for Mozilla
@input u is a list of active users
@input d is a list of drive letters
cacheDict is a map of cache names 0-n found in mozillas cache2 file
	to a list of cache data formatted as 
		[size, creation date, lact access, last written]
			dates are in tuple form (date, time)
'''
#NEED TO MAKE THIS USABLE FOR MULTIPLE USERS AND DRIVES
#TWO LOOPS WILL SOLVE THIS

def checkMozilla():
	cacheDict={}
	os.chdir('/')
	os.system('dir /s entries > %HOMEPATH%\\desktop\\cache2Finder.txt')
	#if len(u)<1:
	#	input('no user profiles found...exiting')
	#	exit()
	#userDict={}#user=>entries list
	os.chdir(os.environ['HOMEPATH']+'\\desktop')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
			if 'Mozilla' in line:
				l=line.split()		#path at l[2]
	fh.close()
	#establish file name, size, and date information
	for i in ['c','a','w']:
		os.system('dir "'+str(l[2])+'/entries" /o:s /t:'+str(i)+' > cache2Dump.txt')
		myHelper(cacheDict, 'Mozilla')
	return cacheDict

'''
chrome default cache search
@return dict mapping file names to file data
	formatted [size,(create, time),(access, time),(write, time)]
'''
def checkChrome():
	cacheDict={}
	os.chdir('/')
	os.system('dir /s Cache > %HOMEPATH%\\desktop\\cache2Finder.txt')
	#if len(u)<1:
	#	input('no user profiles found...exiting')
	#	exit()
	#userDict={}#user=>entries list
	os.chdir(os.environ['HOMEPATH']+'\\desktop')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
			if 'Chrome' in line:
				l=line.split()		#path at l[2]+l[3]
	fh.close()
	#establish file name, size, and date information
	for i in ['c','a','w']:
		os.system('dir "'+str(l[2])+' '+str(l[3])+'/Cache" /o:s /t:'+str(i)+' > cache2Dump.txt')
		myHelper(cacheDict, 'Chrome')
	return cacheDict
	
def myHelper(cacheDict, browser):
	fh=open('cache2Dump.txt','r')
	for line in fh:
		if not '<DIR>' in line:
			if not 'bytes' in line:
				if not 'Volume' in line:
					if not str(browser) in line:
						cacheLine=line.split()
						#print(cacheLine)
						if len(cacheLine)>=3:
							if not cacheLine[4] in cacheDict.keys():
								cacheDict[cacheLine[4]]=[cacheLine[3],(cacheLine[0], cacheLine[1]+' '+cacheLine[2])]
							else:
								cacheDict[cacheLine[4]].append((cacheLine[0], cacheLine[1]+' '+cacheLine[2]))		
	fh.close()



'''
@input users a list of users to search downloads
'''
def getDownloads(users):
	found=[]
	userDowns={}
	os.chdir('/')
	os.system('dir /s Downloads > %HOMEPATH%\\desktop\\downFinder.txt')
	os.chdir(os.environ['HOMEPATH']+'\\desktop')
	fh=open('downFinder.txt','r')
	for line in fh:
		for user in users:
			if user in line:
				l=line.split()
				found.append(l[2]+'\\Downloads')
				userDowns[user]=[]
	fh.close()
	os.chdir('/')
	for dir in found:
		os.system('dir '+dir+' >%HOMEPATH%\\DESKTOP\\downFinder.txt' )
		os.chdir(os.environ['HOMEPATH']+'\\desktop')
		fh=open('downFinder.txt','r')
		for line in fh:
			if not '<DIR>' in line:
				if not 'bytes' in line:
					if not 'Volume' in line:
						if not 'Directory' in line:
							
#pretty sure this will only read from local box and not external hdd	
def dnsCache():
	os.system("ipconfig /displaydns > dns.txt")

'''
reads data from dns cache
@return k: map{requested url, resolved url}
'''
def readDNS():
	d={}
	a=''
	s=''
	fh=open('dns.txt','r')
	for line in fh:
		if 'Name' in line:
			if 'not' in line:
				pass
			else:
				s=line.split(":")[1].strip()
		if 'AA' in line or 'Host' in line:
			if 'No' in line:
				pass
			else:
				a=line.split(":")[1].strip()
		if not a=='':
			d[s]=a
	fh.close()
	#for k in d.keys():
	#	print("requested=> "+k+"\n")
	#	print("reply=> "+d[k]+'\n')
	return d
	
def findDrives():
	return re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)
		
def cleanUp():
	os.chdir(os.environ['HOMEPATH']+'\\desktop')
	if os.path.exists('cache2Finder.txt'):
		os.remove('cache2Finder.txt')
	if os.path.exists('activeUsersCheck.txt'):
		os.remove('activeUsersCheck.txt')
	if os.path.exists('dns.txt'):
		os.remove('dns.txt')
	if os.path.exists('userDump.txt'):
		os.remove('userDump.txt')
	if os.path.exists('cache2Dump.txt'):
		os.remove('cache2Dump.txt')

def main():
	drives=findDrives()
	i=1
	ilist=[]
	for d in drives:
		print(str(i)+'=> '+d+'\n')
		ilist.append(str(i))
		i+=1
	ui=input('\nDrive selection(s){seperated by spaces}: ')
	if not ui in ilist:
		print('Invalid option')
		main()
	root=drives[int(ui)-1]
	print(root.replace('\\',''))
	os.system(root.replace('\\',''))
	users=grabUsers()
	print(users)
	dnsCache()
	dns=readDNS()
	for k in dns.keys():
		print("requested=> "+k+"\n")
		print("reply=> "+dns.get(k)+'\n')
	f=checkMozilla()
	for k in f.keys():
		print(str(k)+'\n'+str(f[k])+'\n')
	h=checkChrome()
	for v in h.keys():
		print(str(v)+'\n'+str(h[v])+'\n')
	cleanUp()
main()
