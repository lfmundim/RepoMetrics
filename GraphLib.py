import networkx as nx

class GraphLib:
	def __init__(self):
		self.graph = nx.Graph()

	def addEdge(self, fileA, fileB):
		try:
			edge = self.graph[fileA][fileB]
			newEdgeWeight = edge['weight'] + 1
			self.graph.add_edge(fileA, fileB, weight=newEdgeWeight)
		except KeyError as e:
			self.graph.add_edge(fileA, fileB, weight=1)

	def getHeaviestEdges(self):
		heaviestEdges = []
		for edge in self.graph.edges:
			actualEdge = (self.graph[edge[0]][edge[1]])
			newItem = ((edge[0],edge[1]), actualEdge['weight'])
			heaviestEdges.append(newItem)
		return sorted(heaviestEdges, key=lambda tup: tup[1], reverse=True)

	def getMostRelatedNodes(self):
		mostRelatedNodes = []
		for node in self.graph.nodes:
			neighborCount = sum(1 for neighbor in nx.neighbors(self.graph, node))
			newItem = (node, neighborCount)
			mostRelatedNodes.append(newItem)
		return sorted(mostRelatedNodes, key=lambda tup: tup[1], reverse=True)

	def GetMostImportantFiles(self):
		removedCount = 0
		total = 0
		removeList = []
		for edge in self.graph.edges:
			actualEdge = self.graph[edge[0]][edge[1]]
			if actualEdge['weight'] == 1:
				removeList.append((edge[0], edge[1]))
				removeList.append((edge[1], edge[0]))
				removedCount += 2
			total += 1
		self.graph.remove_edges_from(removeList)
		total -= removedCount
		listSize = 0
		weightList = []
		for edge in self.graph.edges:
			actualEdge = self.graph[edge[0]][edge[1]]
			if actualEdge['weight'] in weightList:
				continue
			else:
				weightList.append(actualEdge['weight'])
				listSize += 1		
		medianIndex = int(listSize/2)
		median = weightList[medianIndex]
		removedCount = 0
		removeList = []
		for edge in self.graph.edges:
			actualEdge = self.graph[edge[0]][edge[1]]
			if actualEdge['weight'] >= median:
				removeList.append((edge[0], edge[1]))
				removeList.append((edge[1], edge[0]))
				removedCount += 2
		self.graph.remove_edges_from(removeList)
		total -= removedCount
		return self.getMostRelatedNodes()
