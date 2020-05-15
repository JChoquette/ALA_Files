import sys
import csv
import os
import xml.etree.ElementTree as ET

class NodeContent:
	def __init__(self,col):
		self.col=col
	

class Workflow:
	def __init__(self, name):
		self.name=name


	def crawldata(self,data):
		#The raw data is an array of lines in the cflow file. Crawl through and pick out all the nodes
		content = []
		weekindex=0
		for week in data.iter('week'):
			for node in week.iter('node'):
				nodeContent = NodeContent(node.find('column').text)
				nodeContent.id = node.find('id').text
				nodeContent.context=node.find('lefticon').text
				nodeContent.task=node.find('righticon').text
				nodeContent.week=weekindex
				nodeContent.repeatTo=""
				for link in week.iter('node'):
					if(link.find('linktext')!=None and link.find('linktext').text.toLowerCase().index('repeat')>=0):
						nodeContent.repeatTo = link.find('targetid').text
						break
				content.append(nodeContent)
			weekindex=weekindex+1
		for node in content:
			if(node.repeatTo!=""):
				nodeid = node.repeatTo
				for node2 in content:
					if(nodeid == node2.id):
						node2.repeatFrom=node.id
		self.weeks = weekindex
		self.nodes = content
			
	def makeStudent(self):
		student = []
		for node in self.nodes:
			if(node.col=="OOC" or node.col=="ICS"):
				student.append(node)
		self.studentNodes=student

	def makeContracted(self):
		contracted = []
		for node in self.studentNodes:
			if(len(contracted)>0):
				if(contracted[-1].col==node.col and contracted[-1].week==node.week):continue
			contracted.append(node)
		self.studentNodesContracted=contracted

	def makeStrings(self):
		studentString=""
		studentStringTask=""
		studentStringContext=""
		studentStringContracted=""
		firstOOCTask=""
		firstICSTask=""
		
		for i in range(len(self.studentNodesContracted)):
			node = self.studentNodesContracted[i]
			if(firstICSTask=="" and node.col=="ICS"):firstICSTask+=node.task
			if(firstOOCTask=="" and node.col=="OOC"):firstOOCTask+=node.task
			if(i>=1):
				if(node.week!=self.studentNodesContracted[i-1].week):studentStringContracted+="/"
				else: studentStringContracted+="-"
			studentStringContracted+=node.col

		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			prefix = ""
			if(i>=1):
				if(node.week!=self.studentNodes[i-1].week):prefix="/"
				elif(node.col!=self.studentNodes[i-1].col):prefix="-"
				else: prefix=","
				
			studentString+=prefix+node.context+" "+node.task+" "+node.col
			studentStringTask+=prefix + node.task
			studentStringContext+=prefix + node.context
		self.studentString=studentString
		self.studentStringTask=studentStringTask
		self.studentStringContext=studentStringContext
		self.studentStringContracted=studentStringContracted
		self.firstOOCTask=firstOOCTask
		self.firstICSTask=firstICSTask
		

workflows = []
for file in os.listdir("."):
	if(file.endswith(".CFlow")):
		print(file)
		rawdata = ET.parse(file).getroot()
		wf = Workflow(file[:file.index(".CFlow")])
		wf.crawldata(rawdata);
		
		workflows.append(wf)


for wf in workflows:
	wf.makeStudent()
	wf.makeContracted()
	wf.makeStrings()

outstring="Name,Parts,In/Out Pattern,Full Pattern,Tasks,Context,First Out of Class Task,First In-Class Task\n"
for wf in workflows:
	outstring+=wf.name+","+str(wf.weeks)+",\""+wf.studentStringContracted+ "\",\""+wf.studentString+ "\",\""+wf.studentStringTask\
		+"\",\""+wf.studentStringContext+"\",\""+wf.firstOOCTask+"\",\""+wf.firstICSTask+"\"\n"

outfile = open("ALA_data.csv",'w')
outfile.write(outstring)
outfile.close()

