from lib.codetective import get_type_of
import re
from twisted.python import log
def findHashesInRawPaste(paste,confidence=["confident","likely","possible"]):
	for line in paste.split("\n"):
		# print line
		hashwords=[]
		for word in re.split("[\s,:.\[\]]",line):
			# print "Word: %s" % word
			logEntries=[]
			results,result_details=get_type_of(word,['win','web','unix','db','other'])
			count=0
			for k in confidence:
				count+=len(results[k])
			if(count> 0):
				for key in results.keys():
					if(key in confidence and len(results[key]) > 0):
						hashwords.append("%s: %s/%s"  %(word,key,results[key]))
						# log.msg("Possible hash found: %s/%s"  %(key,results[key]))
				# log.msg(word + ":" + ", ".join(logEntries))
	return hashwords

