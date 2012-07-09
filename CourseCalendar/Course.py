'''
Created on Jan 20, 2011

@author: ashwin
'''

from Scrape import *

class Course:
	def __init__ (self, courseStr=None):
		self.code = None
		self.title = None
		self.prerequisites = None
		self.corequisites = None
		self.exclusions = None
		
		if courseStr:
			self.code = courseStr.split()[0]
			self.title = ' '.join(courseStr.split()[1:])
			self.prerequisites = None
			self.corequisites = None
			self.exclusions = None
			
	def setCode(self, c):
		""" Set the course code"""
		
		self.code = c
		
	def getCode(self):
		return self.code
	
	def getDesignation(self):
		return self.code[:3]
	
	def getNumber(self):
		return self.code[3:6]
	
	def getCredits(self):
		return 0.5 if self.code[6] == "H" else 1.0
	
	def getCampus(self):
		return self.code[7]
	
	def getSemester(self):
		return self.code[8]
	
	def setTitle(self, t):
		"""Set the course title"""
		
		self.title = t
		
	def getTitle(self):
		return self.title
	
	def addPrerequisites(self, courses):
		""" Add a list of pre-requisites for the course. These pre-requisites are course codes """
		
		self.prerequisites = parse(normalize(courses))
		
	def getPrerequisites(self):
		return self.prerequisites
	
	def addCorequisites(self, courses):
		""" Add a list of co-requisites for the course. These co-requisites are course codes """
		
		self.corequisites = parse(normalize(courses))
		
	def getCorequisites(self):
		return self.corequisites
	
	def addExclusions(self, courses):
		""" Add a list of exclusions for the course. These exclusions are course codes """
		
		self.exclusions = parse(normalize(courses))
		
	def getExclusions(self):
		return self.exclusions
	
	def getType(self):
		return self.type
	
	def setType(self, t):
		"""Set the course type: SCI, HUM or SSc"""
		
		self.type = t
	
	def setDecription(self, d):
		""" Set the course description"""
		
		self.description = d
		
	def getDescription(self):
		return self.description
	
	def getLabel(self):
		return '%s\n%s' %(self.code, self.title)