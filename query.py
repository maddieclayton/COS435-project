import re, csv, sys

keys1 = open("keys")
keys = []
for key in keys1:
	keys.append(key[:-1])


query = sys.argv[1]
queryWords = query.split()
scoreDict = {}
for word in queryWords:
<<<<<<< HEAD
	print (word)
	if word in keys:
		print ("s")
=======
	if word in keys:
>>>>>>> 7531d348b35e8b2f5ccf92df593cf9c14eabde76
		listDocs = csv.reader(open("output/" + word + ".csv"))
		listDocs1 = next(listDocs)
		for doc in listDocs1:
			if doc in scoreDict:
				scoreDict[doc] = scoreDict[doc] + 1/len(listDocs1)
			else:
				scoreDict[doc] = 1/len(listDocs1)

result = max(scoreDict, key=scoreDict.get)
<<<<<<< HEAD
print (result)
=======
print (result)
>>>>>>> 7531d348b35e8b2f5ccf92df593cf9c14eabde76
