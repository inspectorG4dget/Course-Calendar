'''
Created on Jan 20, 2011

@author: ashwin
'''

import networkx as nx, matplotlib.pyplot as plt
import Course
from Scrape import *
from copy import deepcopy as clone

G = nx.DiGraph()
nodeLabels = {}
edgeLabels = {}
nodeID = 0
ID = {",":[], "/":[]}	# CourseCode : NodeID
label = {}	# NodeID : CourseCode

def mapMaker(courses, filepath):
	
	f = open(filepath, 'w')
	f.write("digraph g4dget {\n")
	global nodeID, ID, label
	
	for course in courses:

		if course.code not in ID:
			ID[course.code] = nodeID
			label[nodeID] = course.code
			f.write('%d [ label="%s" ] ;\n' %(nodeID, course.code))
			nodeID += 1
			
		p, c, e = course.prerequisites, course.corequisites, course.exclusions
		
		courseCodes, ands, ors = traverse(c)
		i=0
		for i in range(len(courseCodes)):
			if courseCodes[i] not in ID:
				ID[courseCodes[i]] = i
				label[i] = courseCodes[i]
		for i in range(i+1, i+1+ands):
			ID[","].append(i)
			label[i] = ','
		for i in range(i+1, i+1+ors):
			ID["/"].append(i)
			label[i] = '/'
		courseCodes, ands, ors = traverse(e)
		i=0
		
		for i in range(len(courseCodes)):
			if courseCodes[i] not in ID:
				ID[courseCodes[i]] = i
				label[i] = courseCodes[i]
		for i in range(i+1, i+1+ands):
			ID[","].append(i)
			label[i] = ','
		for i in range(i+1, i+1+ors):
			ID["/"].append(i)
			label[i] = '/'
		
		courseCodes, ands, ors = traverse(p)
		i=0
		for i in range(len(courseCodes)):
			if courseCodes[i] not in ID:
				ID[courseCodes[i]] = i
				label[i] = courseCodes[i]
		for i in range(i+1, i+1+ands):
			ID[","].append(i)
			label[i] = ','
		for i in range(i+1, i+1+ors):
			ID["/"].append(i)
			label[i] = '/'
#		print "*"*20, "ID", "*"*20
#		for i in ID: print i, ID[i]
#		print "*"*20, "label", "*"*20
#		for i in label: print i, label[i]
		print 'writing', course.code
		if p:
			if p.key in ',/':
				f.write('%d -> %d [ label="PREREQ" ] ;\n' %(ID[course.code], ID[p.key][0]))
			else:
				f.write('%d -> %d [ label="PREREQ" ] ;\n' %(ID[course.code], ID[p.key]))
		writeOut(p, "PREREQ", f, ID, label)
		if c:
			if c.key in ',/':
				f.write('%d -> %d [ label="COREQ" ] ;\n' %(ID[course.code], ID[c.key][0]))
			else:
				f.write('%d -> %d [ label="COREQ" ] ;\n' %(ID[course.code], ID[p.key]))
		writeOut(c, "COREQ", f, ID, label)
		if e:
			if e.key in ',/':
				f.write('%d -> %d [ label="EXCL" ] ;\n' %(ID[course.code], ID[e.key][0]))
			else:
				f.write('%d -> %d [ label="EXCL" ] ;\n' %(ID[course.code], ID[e.key]))
		writeOut(e, "EXCL", f, ID, label)
	
	f.write("}")
	f.close()
		
def writeOut(root, relation, f, ID, label):
	if not root:
		return
	if not root.left and not root.right:
		id = ID[root.key]
		f.write('%d [ label="%s" ] ;\n' %(id, root.key))
		return id
	else:
		L = writeOut(root.left, relation, f, ID, label)
		R = writeOut(root.right, relation, f, ID, label)
		id = ID[root.key]
		if root.key in ',/':
			id = id.pop(0)
		f.write('%d [ label="%s" ] ;\n' %(id, label[id]))
		f.write('%d -> %d [ label="%s" ] ;\n' %(id, L, relation))
		f.write('%d -> %d [ label="%s" ] ;\n' %(id, R, relation))
		return id
	
def traverse(root, courses=[], ands=0, ors=0):
#	print "*"*40
#	print root
	global ID, label, nodeID

	if not root:
		return courses, ands, ors
	elif not root.left and not root.right:
		courses.append(root.key)
		if root.key not in ID:
			if root.key not in ',/':
				ID[root.key] = nodeID
			else:
				ID[root.key].append(nodeID)
			label[nodeID] = root.key
			nodeID += 1
		return courses, ands, ors
	elif root.key not in [',', '/']:
		courses.append(root.key)
		courses, ands, ors = traverse(root.left, courses, ands, ors)
		return traverse(root.right, courses, ands, ors)
	elif root.key == ',':
		ands += 1
		courses, ands, ors = traverse(root.left, courses, ands, ors)
		return traverse(root.right, courses, ands, ors)
		
	elif root.key == '/':
		ors += 1
		courses, ands, ors = traverse(root.left, courses, ands, ors)
		return traverse(root.right, courses, ands, ors)
	
if __name__ == "__main__":
	print 'starting'
#	c1 = Course.Course("CSC399 ROP")
#	c2 = Course.Course("CSC108 Intro")
#	c3 = Course.Course("CSC398 Topics")
#	
#	c1.addExclusions("CSC399H5")
#	c1.addPrerequisites("CSC399H5/(CSC108H5,CSC398H5)")
	
#	courses, ands, ors = traverse(parse("CSC369H5/CSC373H5,CSC398H5,(CSC258H5/(CSC207H5,CSC263H5),CSC290H5)"))
#	mapMaker([c1,c2, c3], 'run1.dot')

	dpages = getDisciplinePages().values()
#	for dpage in dpages:
	dpage = getDisciplinePages()["Anthropology"] #dpages["Antropology"]
	print 'processing', dpage
	courses = getCourses(dpage)
	mapMaker(courses, dpage.rstrip("/").split('/')[-1]+".dot")
	
	
	print 'done'