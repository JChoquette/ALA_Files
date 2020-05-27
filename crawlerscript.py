import sys
import csv
import os
import xml.etree.ElementTree as ET
import copy

Dict = {"ICS":"I","OOC":"O","ICI":"I","OOCI":"O","solo":"Individual","group":"Group","class":"Class","research":"Gather Information","discuss":"Discuss","problem":"Problem Solve","analyze":"Analyze","peerreview":"Assess/Review Peers","debate":"Debate","play":"Game","create":"Create/Design","practice":"Revise/Improve","evaluate":"Evaluate","reading":"Read","write":"Write","present":"Present","experiment":"Experiment","quiz":"Quiz","curation":"Curation","orchestration":"Orchestration","instrevaluate":"Instr. Eval.","other":"Other","undefined":"None"}



class NodeContent:
	def __init__(self,col):
		self.col=col
		self.repeatTo=None
		self.repeatFrom=None
		self.week=""
		self.task=""
		self.context=""

	def getContents(self,contents):
		if(self.col=="dummyrepeatstart"):return "("
		if(self.col=="dummyrepeatend"):return ")"
		if(self.col=="dummyweek"):return "\n"
		if(contents=="all"):return Dict[self.context] + " " + Dict[self.task] + " " + Dict[self.col]
		if(contents=="column"):return Dict[self.col]
		if(contents=="task"):return Dict[self.task]
		if(contents=="context"):return Dict[self.context]
		if(contents=="nocolumn"):return Dict[self.context] + " " + Dict[self.task]
	

class Workflow:
	def __init__(self, name):
		self.name=name


	def crawldata(self,data):
		#The raw data is an array of lines in the cflow file. Crawl through and pick out all the nodes
		content = []
		fullcontent = []
		weekindex=0
		for week in data.iter('week'):
			for node in week.iter('node'):
				nodeContent = NodeContent(node.find('column').text)
				nodeContent.id = node.find('id').text
				nodeContent.context=node.find('lefticon').text
				nodeContent.task=node.find('righticon').text
				nodeContent.week=weekindex
				for link in node.iter('link'):
					if(link.find('linktext')!=None and link.find('linktext').text.lower().find('repeat')>=0):
						nodeContent.repeatTo = link.find('targetid').text
						break
				content.append(nodeContent)
			weekindex=weekindex+1

		for node in content:
			if(node.repeatTo!=""):
				nodeid = node.repeatTo
				for node2 in content:
					if(nodeid == node2.id):
						print "found a match"
						node2.repeatFrom=node.id
						print node2.repeatFrom
						print node.repeatTo
						break
		
		#Add in the dummy nodes
		lastnode = None
		for node in content:
			if(lastnode!=None):
				if(lastnode.week!=node.week):fullcontent.append(NodeContent('dummyweek'))
			if(node.repeatFrom!=None):fullcontent.append(NodeContent('dummyrepeatstart'))
			fullcontent.append(node)
			if(node.repeatTo!=None):fullcontent.append(NodeContent('dummyrepeatend'))
			lastnode=node
		self.weeks = weekindex
		self.nodes = fullcontent
			
	def makeStudent(self):
		student = []
		for node in self.nodes:
			print node.col
			if(node.col=="OOC" or node.col=="ICS" or node.col.find('dummy')>=0):
				student.append(node)
		self.studentNodes=student

	def makeTeacher(self):
		teacher = []
		for node in self.nodes:
			if(node.col=="OOCI" or node.col=="ICI" or node.col.find('dummy')>=0):
				teacher.append(node)
		self.teacherNodes=teacher

	def makeContracted(self):
		contracted = []
		for node in self.studentNodes:
			if(node.col.find('dummy')<0 and len(contracted)>0):
				if(contracted[-1].col==node.col and contracted[-1].week==node.week):
					if(node.repeatTo!=None and contracted[-1].repeatTo==None):contracted[-1].repeatTo=node.repeatTo
					if(node.repeatFrom!=None and contracted[-1].repeatFrom==None):contracted[-1].repeatFrom=node.repeatFrom
					continue
			contracted.append(copy.deepcopy(node))
		self.studentNodesContracted=contracted

	def getStudentString(self):
		string=""
		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			string+=getPrefix(self.studentNodes,i)
			string+=node.getContents("all")
			string+=getSuffix(self.studentNodes,i)
		return string

	def getTeacherString(self):
		string=""
		for i in range(len(self.teacherNodes)):
			node = self.teacherNodes[i]
			string+=getPrefix(self.teacherNodes,i)
			string+=node.getContents("all")
			string+=getSuffix(self.teacherNodes,i)
		return string
	
	def getStudentStringTask(self):
		string=""
		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			string+=getPrefix(self.studentNodes,i)
			string+=node.getContents("task")
			string+=getSuffix(self.studentNodes,i)
		return string

	def getStudentStringContext(self):
		string=""
		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			string+=getPrefix(self.studentNodes,i)
			string+=node.getContents("context")
			string+=getSuffix(self.studentNodes,i)
		return string

	def getStudentStringContracted(self):
		string=""
		for i in range(len(self.studentNodesContracted)):
			node = self.studentNodesContracted[i]
			string+=getPrefix(self.studentNodesContracted,i)
			string+=node.getContents("column")
			string+=getSuffix(self.studentNodesContracted,i)
		return string

	def getFirstOOCTasks(self):
		string=""
		foundOOC=False
		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			if(node.col.find('dummy')>=0):continue
			if(node.col!="OOC"):
				if(foundOOC):break
				else: continue
			else:foundOOC = True
			string+=getPrefix(self.studentNodes,i,True)
			string+=node.getContents("nocolumn")
			string+=getSuffix(self.studentNodes,i,True)
		return string

	def getFirstICSTasks(self):
		string=""
		foundICS=False
		for i in range(len(self.studentNodes)):
			node = self.studentNodes[i]
			if(node.col.find('dummy')>=0):continue
			if(node.col!="ICS"):
				if(foundICS):break
				else: continue
			else: foundICS=True
			string+=getPrefix(self.studentNodes,i,True)
			string+=node.getContents("nocolumn")
			string+=getSuffix(self.studentNodes,i,True)
		return string

	def getFirstOOCITasks(self):
		string=""
		foundOOC=False
		for i in range(len(self.teacherNodes)):
			node = self.teacherNodes[i]
			if(node.col.find('dummy')>=0):continue
			if(node.col!="OOCI"):
				if(foundOOC):break
				else: continue
			else:foundOOC = True
			string+=getPrefix(self.teacherNodes,i,True)
			string+=node.getContents("nocolumn")
			string+=getSuffix(self.teacherNodes,i,True)
		return string

	def getFirstICITasks(self):
		string=""
		foundICI=False
		for i in range(len(self.teacherNodes)):
			node = self.teacherNodes[i]
			if(node.col.find('dummy')>=0):continue
			if(node.col!="ICI"):
				if(foundICI):break
				else: continue
			else: foundICI=True
			string+=getPrefix(self.teacherNodes,i,True)
			string+=node.getContents("nocolumn")
			string+=getSuffix(self.teacherNodes,i,True)
		return string

	


def getPrefix(nodeList,index,ignoreDummy=False):
	if(index==0):return ""
	node = nodeList[index]
	if(node.col.find('dummyweek')>=0 or node.col.find('dummyrepeatend')>=0):return ""

	lastNode = getLastNode(nodeList,index,ignoreDummy)
	if(lastNode==None):return ""
	nextNode=None
	if(node.col.find('dummy')>=0):nextNode = getNextNode(nodeList,index)
	else: nextNode = node
	if(nextNode==None):return ""
	if(lastNode.col!=nextNode.col):return "-"
	else:return ","
		
def getSuffix(nodeList,index,ignoreDummy=False):
	return ""
		

def getNextNode(nodeList,index):
	for i in range(index+1,len(nodeList)):
		if(nodeList[i].col.find('dummy')<0):return nodeList[i]
		elif(nodeList[i].col.find('week')>=0):return None
		
	return None


def getLastNode(nodeList,index,ignoreDummy):
	if index==0:return None
	print index
	for i in range(index,0,-1):
		print i
		if(nodeList[i-1].col.find('dummy')<0):return nodeList[i-1]
		elif(ignoreDummy==False and (nodeList[i-1].col.find('week')>=0 or nodeList[i-1].col.find('repeatstart')>=0)):return None
	return None

workflows = []
for file in os.listdir("."):
	if(file.endswith(".CFlow")):
		print(file)
		rawdata = ET.parse(file).getroot()
		wf = Workflow(file[:file.find(".CFlow")])
		wf.crawldata(rawdata);
		
		workflows.append(wf)


for wf in workflows:
	wf.makeStudent()
	wf.makeTeacher()
	wf.makeContracted()

outstring="Name,Parts,In/Out Pattern,Full Pattern,Tasks,Context,First Out of Class Tasks,First In-Class Tasks,Instructor,First OOCI, First ICI\n"
for wf in workflows:
	outstring+=wf.name+","+str(wf.weeks)+",\""+wf.getStudentStringContracted()+ "\",\""+wf.getStudentString()\
		+ "\",\""+wf.getStudentStringTask()\
		+"\",\""+wf.getStudentStringContext()+"\",\""+wf.getFirstOOCTasks()+"\",\""+wf.getFirstICSTasks()\
		+"\",\""+wf.getTeacherString()+"\",\""+wf.getFirstOOCITasks()+"\",\""+wf.getFirstICITasks()\
		+"\"\n"

outfile = open("ALA_data.csv",'w')
outfile.write(outstring)
outfile.close()

