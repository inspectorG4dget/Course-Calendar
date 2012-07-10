'''
Created on Jan 20, 2011

@author: ashwin

 Licensed to Ashwin Panchapakesan under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 Ashwin licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''

#from Course import *
import Course, urllib2, re, json
from BeautifulSoup import BeautifulSoup as BS
from os import system as cmd

class Node:
	def __init__(self, k=None, L=None, R=None):
		self.key = k
		self.left = L
		self.right = R
		
	def __str__(self):
		return "%s\n\tL:%s\n\tR:%s" %(self.key, self.left, self.right)
	
def AND(L):
	n = L[0]
	for i in L[1:]:
		n = Node(',', n, i)
	
	return n

def OR(L):
	n = L[0]
#	print n
#	print "+"*40
	for i in L[1:]:
		n = Node('/', n, i)
#		print i
#		print "+"*40
#	print n.key
#	print n.left.key, n.left.left, n.left.right
#	print n.right.key, n.right.left, n.right.right
	return n

delimToFunc = { '/' : OR,
				',' : AND
				}
	
def getDisciplinePages():
	""" Return a dict {DisciplineName:URL} of URLs, each one corresponding to one Discipline """
	
	answer = {}
	cmd("cd /home/ashwin/workspace/CourseCalendar/scrapy/regcal/regcal/spiders/")
	cmd("scrapy crawl regcal --set FEED_URI=items.json --set FEED_FORMAT=json")
	
	f = open("/home/ashwin/workspace/CourseCalendar/scrapy/regcal/regcal/spiders/items.json")
	j = ' '.join([line.strip() for line in f])
	f.close()
	son = json.loads(j)
	L = [dict((str(k), [str(i) for i in d[k]]) for k in d) for d in son]
	
	for d in L:
		answer[d['discipline'][0]] = "http://www.utm.utoronto.ca/regcal/%s" %d['link'][0].replace("WEBDEP", "WEBLISTCOURSES")

	return answer

def getCourses(URL):
	""" Given a discpline's URL return a list of course objects - each referring to a course in the discipline """
	
	courses = []
		
	html = ''.join(urllib2.urlopen(URL)).replace("<br/<", "<br>/<")
	soup = BS(html)
	
	div = soup.body.div
	
	course = div.p.nextSibling.nextSibling.nextSibling
	for _ in range(html.count('<p class="titlestyle">')):
		courseStr = str(course)
		keys = ['<.*?>', '\n+', ' +']
		values = ['', ' ', ' ']
		for i in range(len(keys)):
			courseStr = re.sub(keys[i], values[i], courseStr)
		
		exclusions = []
		prereqs = []
		coreqs = []
		
		try:
			prop = course.nextSibling.nextSibling.span.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling
		except:
			pass
		
		i = 0
		while i<3:
			try:
				if "Exclusion" in re.sub("<.*?>", "", str(prop)).strip().replace(":", ""):
					toAdd = re.sub("<.*?>", "", str(prop.nextSibling)).strip()
					if toAdd not in exclusions:
						exclusions.append(str(toAdd))
				elif "Prerequisite" in re.sub("<.*?>", "", str(prop)).strip().replace(":", ""):
					toAdd = re.sub("<.*?>", "", str(prop.nextSibling)).strip()
					if toAdd not in prereqs:
						prereqs.append(str(toAdd))
				elif "Corequisite" in re.sub("<.*?>", "", str(prop)).strip().replace(":", ""):
					toAdd = re.sub("<.*?>", "", str(prop.nextSibling)).strip()
					if toAdd not in exclusions:
						coreqs.append(str(toAdd))
					
				prop = prop.nextSibling.nextSibling.nextSibling.nextSibling
				i += 1
			except:
				i = 3
		
		ended = False
		while str(prop).find('<p class="titlestyle">') < 0 and not ended:
			try:
				prop = prop.nextSibling
				if prop == None:
					ended = True
			except:
				ended = True
		
		c = Course.Course(courseStr)
		c.addExclusions(''.join(exclusions))
		c.addPrerequisites(''.join(prereqs))
		c.addCorequisites(''.join(coreqs))
#		c.description = course.nextSibling.nextSibling.text
		courses.append(c)
		
		course = prop
		
	return courses
	
def normalize(courses):
	courses = courses.replace(' ', '')
	courses = re.sub('[a-zA-z]{3}\(', '(', courses)
	
	last = ''
	courseCodes = courses.replace(';', ' ').replace(',', ' ').replace('(', ' ').replace(')', ' ').replace('/', ' ').split()
	splits = re.sub('[a-zA-z]{3}[0-9]{3}[HY][135]', '', courses)
	splits = re.sub('[0-9]{3}[HY][135]', '', splits)
	splits = re.sub('[a-zA-z]{3}', '', splits)
	
	for i in range(len(courseCodes)):
		if courseCodes[i][:3].isalpha():
			last = courseCodes[i][:3]
		else:
			courseCodes[i] = last + courseCodes[i]
		
		try:
			courseCodes[i] += splits[i]
			if 	(splits[i] in ',;/' and splits[i+1] == '(') or \
				(splits[i] == ")" and splits[i+1] in ';,/'):
				courseCodes[i] += splits[i+1]
				splits = splits[1:]
		except:
			pass
	return ''.join(courseCodes)

def parse(courses):
#	print courses
	courses = courses.replace(" ", "")
	
	if not courses:
		return None
	
	if courses.isalnum():	# only one course
		return Node(courses)
	else:
		if HOMO(courses, ','):
			return AND([parse(i) for i in courses.split(',')])
		elif HOMO(courses, '/'):
#			print courses.split('/')
			return OR([parse(i) for i in courses.split('/')])
		else:	# there are ()s
			if courses[0] == "(":
#				print "YAY"
				i = PDA_Find(courses)
				if i+1>len(courses)-1:
#					print "HAH"
#					print courses[1:-1]
					return parse(courses[1:-1])
				elif courses[i+1] == '/':
					return OR([parse(courses[:i+1]), parse(courses[i+2:])])
				elif courses[i+1] == ',':
					return AND([parse(courses[:i+1]), parse(courses[i+2:])])
				
			else:
				a,o = cache_find(courses, ','), cache_find(courses, '/')
#				if a<0: x = o+1
#				elif o<0: o = a+1
				
				if a<o>0<a:# and a<o:
					return AND([parse(courses[:a]), parse(courses[a+1:])])
				elif o<a>0<o:	# o<a
#					print "HAHA"
#					print courses
					c = courses.find(',')
					if ("(" in courses[o:c]):
						if courses[o:c].count("(") == courses[o:c].count(")"):
							e = PDA_Find(courses[courses.find("(") :]) + len(courses[: courses.find("(")])
#							print "e, len(courses)-1:", e, len(courses)-1
							if e == len(courses)-1:
								return OR([parse(courses[:o]), parse(courses[o+1:])])
							else:
	#							print "courses:", courses, courses[e], courses[e+1]
	#							print "courses[:e+1]:", courses[:e+1]
								if courses[e+1] == ',':
									return AND([parse(courses[:e+1]), parse(courses[e+1:])])
								elif courses[e+1] == '/':
									return OR([parse(courses[:e+1]), parse(courses[e+1:])])
						else:
							e = PDA_Find(courses[courses.find("(") :]) + len(courses[: courses.find("(")])
							if e == len(courses)-1:
								return OR([parse(courses[:o]), parse(courses[o+1:])])
							else:
	#							print "courses:", courses, courses[e], courses[e+1]
	#							print "courses[:e+1]:", courses[:e+1]
								if courses[e+1] == ',':
									return AND([parse(courses[:e+1]), parse(courses[e+2:])])
								elif courses[e+1] == '/':
									return OR([parse(courses[:e+1]), parse(courses[e+2:])])
					elif "(" not in courses[o:c]:
						return AND([parse(courses[:a]), parse(courses[a+1:])])
					else:
#						return AND([parse(courses[:a]), parse(courses[a+1:])])
						e = PDA_Find(courses[courses.find("(") :]) + len(courses[: courses.find("(")])
#						print "e, len(courses)-1:", e, len(courses)-1
						if e == len(courses)-1:
							return OR([parse(courses[:o]), parse(courses[o+1:])])
						else:
#							print "courses:", courses, courses[e], courses[e+1]
#							print "courses[:e+1]:", courses[:e+1]
#							print "HOHOE"
							return AND([parse(courses[:e+1]), parse(courses[e+2:])])
				elif a>o:
					return AND([parse(courses[:a]), parse(courses[a+1:])])
				elif o>a:
					return OR([parse(courses[:o]), parse(courses[o+1:])])
			
def HOMO(s, c):
	copy = re.sub("[A-Za-z0-9 ]", "", s)
	copy = re.sub(c, "", copy)
	return not copy

def PDA_Find(s):
#	print "s:", s
	open, close, i = 0,0,1
	
	if s[0] != "(":
		return False
	else:
		open += 1
		while close<open:
			char = s[i]
			if char == "(":
				open += 1
			elif char == ")":
				close += 1
			i += 1
		return i-1
	
def cache_find(s, c):
	return s.find(c)
	
if __name__ == "__main__":
	print 'starting'
#	print parse("CSC369H5")
#	print parse("CSC369H5/(CSC100H5,CSC101H5)/CSC102H5")
#	print parse("CSC100H5/CSC369H5,(CSC369H5,CSC373H5)")
#	print parse("CSC207H5,(CSC369H5/CSC373H5),CSC398H5")
#	print parse("CSC369H5/CSC373H5,CSC398H5,(CSC258H5/(CSC207H5,CSC263H5),CSC290H5)")
#	print normalize("CSC369H5/373H5,CSC398H5, (CSC258H5/STA(207H5,263H5),CSC290H5)")
#	print extract("CSC207H5, 209H5; CGPA 2.0; CSC290H5/MAT300H5/301H5")
	
#	dpages = ["http://www.utm.utoronto.ca/regcal/"+i for i in getDisciplinePages()]
	dpages = getDisciplinePages()
	anthroURL = dpages["Computer Science"]
	courses = getCourses(anthroURL)
	for course in courses:
		print "*"*40
		print course.code
		print course.exclusions
		print course.prerequisites
		print course.corequisites

	print 'done'