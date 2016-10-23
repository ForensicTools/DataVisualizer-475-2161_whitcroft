import os, re

'''
returns a list of active users
caller must check if null before accessing 
'''
def grabUsers():
	os.system('cd %HOMEPATH%')
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
'''

def checkMozilla(u,d):
	os.system('cd /')
	os.system('dir /s entries > %HOMEPATH%\\cache2Finder.txt')
	if len(u)<1:
		input('no user profiles found...exiting')
		exit()
	userDict={}#user=>entries list
	os.system('cd %HOMEPATH%')
	fh=open('cache2Finder.txt','r')
	for line in fh:
		if 'Directory of' in line:
			l=line.split()		#path at l[2]

	
	for driveLetter in d:
		for user in u:
			#st=str(driveLetter)+':\\users\\'+str(user)+'\\appdata\\local\\mozilla\\firefox\\profiles\\fuvg83qk.default'
			#if os.path.exists(')
			break
	fh.close()
	
def dnsCache():
	os.system("cd %HOMEPATH%")
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
	os.system('cd %HOMEPATH%')
	if os.path.exists('HOMEPATH%\\cache2Finder.txt'):
		os.remove('cache2Finder.txt')
	if os.path.exists('HOMEPATH%\\activeUsersCheck.txt'):
		os.remove('activeUsersCheck.txt')
	if os.path.exists('HOMEPATH%\\dns.txt'):
		os.remove('dns.txt')
	if os.path.exists('HOMEPATH%\\userDump.txt'):
		os.remove('userDump.txt')

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
main()
