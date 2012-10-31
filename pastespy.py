#!/usr/bin/python
from twisted.python import log
from twisted.internet import reactor,defer
from twisted.web.client import HTTPConnectionPool
pool = HTTPConnectionPool(reactor, persistent=True)
pool.maxPersistentPerHost = 1
from treq import get
import sys,re
from lib.pastebin import parsePastebinArchive, parsePastebinIndividualPaste
from lib.hashfinder import findHashesInRawPaste
log.startLogging(sys.stdout)


# def findHashesInRawPaste(paste):
# 	for line in paste.split("\n"):
# 		for word in re.split("[\S,:.\[\]]",line):
# 			results,result_details=get_type_of(word,['win','web','unix','db','other'])
# 			if(len(results['confident']) + len(results['likely']) + len(results['possible'])> 0):
# 				for key in results.keys():
# 					if(len(results[key]) > 0):
# 						log.msg("Possible hash found: %s/%s"  %(key,results[key]))

semaphore=defer.DeferredSemaphore(5)
def semaphoreGet(*args,**kwargs):

	d=semaphore.acquire().addCallback(lambda x: get(*args,**kwargs)).addCallback(semaphoreGetContinue)
	return d

def semaphoreGetContinue(d):
	semaphore.release()
	return d

def handleArchivePage(response):
	log.msg( "Archive page code is %s" % response.status_code)
	d=response.content.addCallback(parseArchiveResults)
	return d

def parseArchiveResults(text):
	pages=[]
	for (url,name) in parsePastebinArchive(text):
		pasteID=url[1:]
		# log.msg("`%s' has ID %s" % (name,pasteID))
		fullPageDeferred=semaphoreGet("http://pastebin.com/%s" % pasteID).addCallback(lambda r: r.content)
		rawDeferred=semaphoreGet("http://pastebin.com/raw.php?i=%s" % pasteID).addCallback(lambda r: r.content)
		d=defer.DeferredList([fullPageDeferred,rawDeferred]).addCallback(handleIndividualPaste,pasteID)
		pages.append(d)
	return d

def handleIndividualPaste(dd,pasteID):
	(fullPageResponse,rawPageResponse)=dd
	if fullPageResponse[0] and rawPageResponse[0]:
		# log.msg("DDDDDDD Type is " + str(fullPageResponse[1].__class__.__name__))
		pageDetails=parsePastebinIndividualPaste(fullPageResponse[1])
		rawPaste=rawPageResponse[1]
		pageDetails['snippet']=rawPaste.split("\n")[0]
		fixedPasteDetails={}
		for (k,v) in pageDetails.items():
			fixedPasteDetails[k]=v.decode('utf8','ignore')
		log.msg("%(author)s on %(date)s posted the following about `%(title)s': %(snippet)s" % fixedPasteDetails)
		hashwords=findHashesInRawPaste(rawPaste,["confident"])
		for h in hashwords:
			log.msg("%s found in pastebin ID: %s" % (h,pasteID))
d=semaphoreGet('http://pastebin.com/archive').addCallback(handleArchivePage).addBoth(lambda x: reactor.stop())
reactor.run()