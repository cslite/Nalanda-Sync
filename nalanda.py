import requests
import json
from bs4 import BeautifulSoup
import os
from mimetypes import guess_extension
import re
from config import *


'''
to make the string a valid filename
'''
def clean_string(s):
	s = str(s).strip().replace(' ', '_')
	return re.sub(r'(?u)[^-\w.&()]', '_', s)
'''
to remove slashes from the string
'''
def rm_slash(s):
	s = s.replace('/','_')
	s = s.replace('\\','_')
	return s

'''
login to the nalanda system and return the obtained cookies
'''
def login(user, pwd):
	global plogin_url
	global base_url
	cookiejar = {}
	r = requests.get(base_url+plogin_url)
	cookiejar = dict(r.cookies)
	r = requests.post(base_url+plogin_url,data={'username':user,'password':pwd},allow_redirects=False)
	# print(r.text)
	cookiejar = dict(r.cookies)
	print(cookiejar)
	return cookiejar

'''
get a list of courses along with their links
'''
def get_courses(cookies):
	global base_url
	global pdash_url
	r = requests.get(base_url+pdash_url,cookies=cookies)
	soup = BeautifulSoup(r.text,'lxml')
	soup_list = soup.find_all('div',{'class':'column c1'})
	courses = {}
	for soup in soup_list:
		soup = soup.find('a')
		# print(soup.getText())
		# print(soup['href'])
		courses[rm_slash(soup.getText())] = soup['href']
	return courses

'''
get list of files for a given course
'''
def get_file_list(course_url,cookies):
	r = requests.get(course_url,cookies=cookies)
	soup = BeautifulSoup(r.text,'lxml')
	soup_list = soup.find_all('div',{'class':'activityinstance'})
	files = {}
	for soup in soup_list:
		soup = soup.find('a')
		link = soup['href']
		if 'resource' in link:
			files[link.split('=')[-1]] = soup.getText()
	return files

'''
download resource with given resource_id to donwload_path
'''
def get_resource(resource_id,download_path,cookies):
	global base_url
	global presource_url
	resource_url = base_url+presource_url+resource_id
	r = requests.get(resource_url,cookies=cookies,allow_redirects=True)
	extn = guess_extension(r.headers['content-type'])
	# print(extn)
	with open(download_path+extn,'wb') as f:
		f.write(r.content)

def sync_all_files():
	global user
	global pwd
	cookies = login(user,pwd)
	courses = get_courses(cookies)
	if not os.path.isdir(base_path):
		os.mkdir(base_path)
	for c in courses:
		cpath = os.path.join(base_path,c)
		if not os.path.isdir(cpath):
			os.mkdir(cpath)
		cfile_list = get_file_list(courses[c],cookies)
		for cfile in cfile_list:
			cfile_path = os.path.join(cpath,clean_string(cfile_list[cfile]))
			get_resource(cfile,cfile_path,cookies)
			print('Downloaded %s from %s...'%(cfile_list[cfile],c))



# login(user,pwd)

# get_courses(c)

# get_resource('6509','test',c)

sync_all_files()
