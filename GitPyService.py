import io
import os
import time
import numpy as np
import shutil
import collections
import re as regex
import ComplexCalc as cc
from git import Repo
from datetime import datetime
import warnings
import GraphLib as gl
import networkx as nx

class GitPyService:
	def __init__(self, url, path):
		self.url = url
		self.path = path
		self.repo = self.InitializeRepo(url, path)

	def InitializeRepo(self, url = '[empty]', path = ''):
		if url != '[empty]':
			try:
				Repo.clone_from(url, path)
			except:
				shutil.rmtree(path, ignore_errors=True)
				Repo.clone_from(url, path)
		return Repo(path)

	def hasSomeIgnoredExtension(self, file):
		ignoredExtensions = ['.xml', '.json', '.csproj', '.yml', '.yaml', '.md', '.config', '.dll', '.sln', '.gitignore', '.gitattributes', '.lock', '.ide', '.db', '.nuspec', '.exe', '.out', '.png', '.pdf', '.csv', '.bmp', '.ico', '.jpg', '.jpeg', '.pfx', '.pyc', '.DS_Store', '.dockerignore', '.txt', 'LICENSE', 'Dockerfile', 'ISSUE_TEMPLATE', '.resx', '.patch', '.targets']

		for extension in ignoredExtensions:
			if(file.lower().endswith(extension.lower())):
				return True

		return False
	
	def GetCommitsByTime(self, commits):
		commitsByTime = collections.OrderedDict()

		if(len(commits) >= 2):
			days = (time.mktime(time.gmtime(commits[-1])) - time.mktime(time.gmtime(commits[0])))/86400
			count = 1
			lastTimestamp = None

			for commit in commits:
				if((days/30) >= 3):
					label = time.strftime("%Y", time.gmtime(commit)) if (days/365) >= 3 else time.strftime("%B-%Y", time.gmtime(commit))
					if(label in commitsByTime):
						commitsByTime[label] += 1
					else:
						commitsByTime[label] = 1
				else:
					diffSecs = (time.mktime(time.gmtime(commit)) - time.mktime(time.gmtime(lastTimestamp)))
					label = 'day'
					changeLabel = False
					if((days/7) >= 3):
						label = 'week'
						changeLabel = diffSecs/86400 > 7
					else:
						changeLabel = diffSecs/86400 > 1

					if lastTimestamp is not None and changeLabel:
						count += 1
					dictLabel = "{} #{}".format(label, count)
					if(dictLabel in commitsByTime):
						commitsByTime[dictLabel] += 1
					else:
						commitsByTime[dictLabel] = 1
					lastTimestamp = commit
		return commitsByTime
		
	def GetCommitedComplexityMetrics(self, commit):
		self.repo.git.checkout(commit)
		craDic = {}
		ctaDic = {}
		mcaDic = {}
		complexCalc = cc.ComplexCalc()

		for root, directory, files in os.walk(self.path):
			for file in files:
				if not self.hasSomeIgnoredExtension(file) and ".git" not in root.split('/'):
					fullPath = os.path.join(root, file)
					craDic[fullPath] = complexCalc.GetCRAByIndent(fullPath)
					ctaDic[fullPath] = complexCalc.GetCTAByIndent(fullPath)
					mcaDic[fullPath] = complexCalc.GetMCAByIndent(fullPath)

		with warnings.catch_warnings():
			warnings.simplefilter("ignore", category=RuntimeWarning)
			CraAverage = round(np.array(list(craDic.values())).mean(),3)
			CtaAverage = round(np.array(list(ctaDic.values())).mean(),3)
			McaAverage = round(np.array(list(mcaDic.values())).mean(),3)

		return CraAverage, CtaAverage, McaAverage

	def get_metrics(self):
		graph = gl.GraphLib()
		allCommits = self.repo.iter_commits()
		committers = collections.OrderedDict()
		modifiedFiles = collections.OrderedDict()
		commitsTimeStamp = []
		CraByCommit = []
		CtaByCommit = []
		McaByCommit = []		
		graphLib = gl.GraphLib()

		while True:
			try:
				commit = next(allCommits)

				commitFiles = commit.stats.files
				for file in commitFiles:
					file = file.split('/')[-1]
					for otherFile in commitFiles:
						otherFile = otherFile.split('/')[-1]
						if file == otherFile:
							continue
						graphLib.addEdge(file, otherFile)
				
				complexMetrics = self.GetCommitedComplexityMetrics(commit)
				
				if complexMetrics[0] > 0: CraByCommit.append(complexMetrics[0])
				if complexMetrics[1] > 0: CtaByCommit.append(complexMetrics[1])
				if complexMetrics[2] > 0: McaByCommit.append(complexMetrics[2])

				if(len(commitsTimeStamp) == 0 or commitsTimeStamp[-1] < commit.committed_date):
					commitsTimeStamp.append(commit.committed_date)
				else:
					commitsTimeStamp.insert(0, commit.committed_date)

				if commit.author.email in committers:
					committers[commit.author.email] = committers[commit.author.email] + 1
				else:
					committers[commit.author.email] = 1
				commitFiles = commit.stats.files
				for key in commit.stats.files:
					if not self.hasSomeIgnoredExtension(key):
						for otherFile in commitFiles:
							if key == otherFile or self.hasSomeIgnoredExtension(otherFile):
								continue
							graph.addEdge(key, otherFile)
						if key in modifiedFiles:
							modifiedFiles[key] = modifiedFiles[key] + 1
						else:
							modifiedFiles[key] = 1
			except StopIteration:
				break

		g = graphLib.graph
		removeList = []
		for edge in g.edges:
			actualEdge = g[edge[0]][edge[1]]
			if actualEdge['weight'] < 5:
				removeList.append((edge[0], edge[1]))
				removeList.append((edge[1], edge[0]))
		g.remove_edges_from(removeList)
		g.edges()

		removeList = []
		for node in g.nodes:
			if sum(1 for neighbor in nx.neighbors(g, node)) <= 1:
				removeList.append(node)
		g.remove_nodes_from(removeList)

		ordered_committers = {}
		for key, value in sorted(committers.items(), key=lambda kv: kv[1], reverse=True):
			ordered_committers[key] = value
			
		ordered_files = {}
		for key, value in sorted(modifiedFiles.items(), key=lambda kv: kv[1], reverse=True):
			if('/' in key):
				key = (key.split('/'))[-1]
			ordered_files[key] = value
			
		no_config_ordered_files = {}
		for key, value in sorted(modifiedFiles.items(), key=lambda kv: kv[1], reverse=True):
			if not self.hasSomeIgnoredExtension(key):
				no_config_ordered_files[key] = value
		
		commitsByTime = self.GetCommitsByTime(commitsTimeStamp)

		heaviest_edges = graph.getHeaviestEdges()
		mostImportantFiles = graph.GetMostImportantFiles()
		
		self.repo.git.checkout('master')
		CraByCommit.reverse()
		CtaByCommit.reverse()
		McaByCommit.reverse()
		return len(commitsTimeStamp), ordered_committers, ordered_files, no_config_ordered_files, commitsByTime, CraByCommit, CtaByCommit, McaByCommit, mostImportantFiles[:10], heaviest_edges[:10], g