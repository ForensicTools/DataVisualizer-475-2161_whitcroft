'''
'@author James Whitcroft
'@update 4:32 PM 10/28/2016
'''
import os, re, binascii, math

'''
returns a list of active users
caller must check if null before accessing 
'''
def grabUsers():
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

def checkMozilla(user):
	path=[]
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
				if user.lower() in line.lower():
					l=line.split()		#path at l[2]
	fh.close()
	#establish file name, size, and date information
	path.append(str(l[2])+'\\entries\\')
	for i in ['c','a','w']:
		os.system('dir "'+str(l[2])+'/entries" /o:s /t:'+str(i)+' > cache2Dump.txt')
		myHelper(cacheDict, 'Mozilla')
	return (path, cacheDict)

'''
chrome default cache search
@return dict mapping file names to file data
	formatted [size,(create, time),(access, time),(write, time)]
'''
def checkChrome():
	path=[]
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
	path.append(str(l[2])+' '+str(l[3])+'/Cache')
	#establish file name, size, and date information
	for i in ['c','a','w']:
		os.system('dir "'+str(l[2])+' '+str(l[3])+'/Cache" /o:s /t:'+str(i)+' > cache2Dump.txt')
		myHelper(cacheDict, 'Chrome')
	return (path, cacheDict)

'''	
helps to parse chrome and firefox cache data
by validating lines read from a file
@input cacheDict a dictonary mapping file names to data
@input browser a string representing the browser 'mozilla' or 'chrome'
'''
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
collects downloads from users download folder
@input users a list of users to search downloads
'''
def getDowns(users):
	found=[]
	userDowns={}
	os.chdir('/')
	os.system('dir /s Downloads > %HOMEPATH%\\desktop\\downFinder.txt')
	os.chdir(os.environ['HOMEPATH']+'\\desktop')
	fh=open('downFinder.txt','r')
	for line in fh:
		for user in users:
			if user.lower() in line.lower():
				l=line.split()
				found.append(l[2]+'\\Downloads')
				userDowns[user]={}
	fh.close()
	os.chdir('/')
	for dir in found:
		for x in ['c','a','w']:
			os.system('dir /t:'+str(x)+' '+'"'+str(dir)+'"'+' >%HOMEPATH%\\DESKTOP\\downFinder.txt' )
			os.chdir(os.environ['HOMEPATH']+'\\desktop')
			fh=open('downFinder.txt','r')
			for line in fh:
				if 'File Not Found' in line:
					break
				if not '<DIR>' in line:
					if not 'bytes' in line:
						if not 'Volume' in line:
							if not 'Directory' in line:
								l=line.split()
								#THIS IS WRONG, POPULATES BOTH USERS WITH SAME DATA
								for user in users:
									if len(l)>=3:
										if l[4] in userDowns[user]:
											userDowns[user][l[4]].append((l[0],l[1]+' '+l[2]))
										else:
											userDowns[user][l[4]]=[l[3],(l[0],l[1]+' '+l[2])]
	return userDowns

'''
parses cache2 files individually
@input filename, the path to the cache2 file, one at a time
'''
def readCacheFile(filename):
	fh=open(filename,'rb')
	size=fh.seek(0,2)
	#mozilla chunk size 262144
	#2 hash bytes per chunk
	chunkHash=math.ceil(size/262144)*(2)
	fh.seek(-4,2)
	loc=binascii.hexlify(fh.read(4))
	fh.seek(int(loc,16)+(4+chunkHash))
	#version
	version=binascii.hexlify(fh.read(4))
	#fetch count
	fetchCount=binascii.hexlify(fh.read(4))
	#last fetched date
	fetchDate=binascii.hexlify(fh.read(4))
	#last modified date
	modDate=binascii.hexlify(fh.read(4))
	#frequency
	freq=binascii.hexlify(fh.read(4))
	#expiration date
	expires=binascii.hexlify(fh.read(4))
	#key length
	keyLen=binascii.hexlify(fh.read(4))
	#uri
	uri=str(binascii.hexlify(fh.read(int(keyLen,16))))
	i=binascii.hexlify(fh.read(1))
	if str(i)=="b''":
		 pass
	else:
		l=[str(i)]
		while not int(i,16)==0:
			#uri=str(int(uri,16))+str(int(i,16))
			l.append(str(i))
			i=binascii.hexlify(fh.read(1))
			if str(i)=="b''":
				break
		for g in l:
			uri=uri+g
		#dirty clean up of str uri
		#trim byte flag
		uri=uri.replace('b','')
		#trim quotes
		uri=uri.replace("'",'')
		#entries are formatted :http:
		#3a==':'
		uri=uri[uri.find('3a')+2:]
		#print(version)
		#print(fetchCount)
		#print(fetchDate)
		#print(modDate)
		#print(freq)
		#print(expires)
		#print(keyLen)
		#print(uri[10:])
		'''
		NOT SURE WHY THIS HAPPENS YET, POSSIBLY DUE TO MY TRIMMING
		NEEDS TO BE TESTED
		'''
		if len(uri)%2==0:
			print(binascii.unhexlify(uri))
		else:
			print(uri)

def readCacheFile2(filename):
	#binascii.hexlify(struct.pack('>h', int))
	return
			
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
	if os.path.exists('downFinder.txt'):
		os.remove('downFinder.txt')
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
	#manually insert user for testing
	f=checkMozilla('James')
	for k in f[1].keys():
		print(str(k)+'\n'+str(f[1][k])+'\n')
	h=checkChrome()
	for v in h[1].keys():
		print(str(v)+'\n'+str(h[1][v])+'\n')
	
	#manually insert user(s) for testing
	g=getDowns(['jesus','james'])
	for v in g.keys():
		print('1:'+str(v)+'\n'+str(g[v])+'\n')
	for cacheEntry in f[1].keys():
		readCacheFile(f[0][0]+cacheEntry)
	#remove all those files I created, sorry...)	
	cleanUp()
	
main()
