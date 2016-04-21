import re, csv, sys

keys = open("keys")
#for key in keys:
#	print (key)

query = sys.argv[1]
queryWords = query.split()
scoreDict = {}
for word in queryWords:
	if word+"\n" in keys:
		listDocs = csv.reader(open("output/" + word + ".csv"))
		listDocs1 = next(listDocs)
		for doc in listDocs1:
			print (doc)
			if doc in scoreDict:
				scoreDict[doc] = scoreDict[doc] + 1/len(listDocs1)
			else:
				scoreDict[doc] = 1/len(listDocs1)

#result = max(scoreDict, key=scoreDict.get)
#print (result)