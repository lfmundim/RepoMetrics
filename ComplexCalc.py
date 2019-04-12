import os

class ComplexCalc:
	def GetComplexStatsByIndent(self, file):
		totalIndent = 0
		maxIndent = 0
		lineCount = 0
		
		with open(file, 'rU') as f:
			for line in f:
				lineCount += 1
				currentIndent = 0
				caracterCount = 0
				for caracter in line:
					if caracter == ' ':
						currentIndent += 1
						caracterCount += 1
					elif caracter == '\t':
						currentIndent += 4
						caracterCount += 4
					else:
						caracterCount += 1
						break
				if caracterCount == currentIndent: #ignore; empty line
					continue
				else:
					totalIndent += int(currentIndent / 4)
					if(int(currentIndent / 4) > maxIndent):
						maxIndent = int(currentIndent / 4)
		return totalIndent, maxIndent, lineCount

	def GetCTAByIndent(self, file):
		complexStats = self.GetComplexStatsByIndent(file)
		return complexStats[0]

	def GetCRAByIndent(self, file):
		complexStats = self.GetComplexStatsByIndent(file)
		if(complexStats[2] > 0):
			return complexStats[0]/complexStats[2]
		return 0

	def GetMCAByIndent(self, file):
		complexStats = self.GetComplexStatsByIndent(file)
		return complexStats[1]

	def GetCPByIndent(self, folderPath, fileExtension):
		filesCount = 0
		actualCraSum = 0
		for root, directory, files in os.walk(folderPath):
			for file in files:
				if(file.endswith(fileExtension)):
					actualCraSum += self.GetCRAByIndent(os.path.join(root, file))
					filesCount += 1
		if filesCount > 0:
			return actualCraSum/filesCount
		else:
			return 0
