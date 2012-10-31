#!/usr/bin/python
from twisted.python import log
from twisted.internet import reactor,defer
from twisted.web.client import HTTPConnectionPool
pool = HTTPConnectionPool(reactor, persistent=True)
pool.maxPersistentPerHost = 5
from treq import get
import sys
from lib.pastebin import parsePastebinArchive, parsePastebinIndividualPaste
log.startLogging(sys.stdout)

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
		log.msg("`%s' has ID %s" % (name,pasteID))
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
		pageDetails['snippet']=rawPageResponse[1].split("\n")[0]
		log.msg("%(author)s on %(date)s posted the following about `%(title)s': %(snippet)s" % pageDetails)
	
d=semaphoreGet('http://pastebin.com/archive').addCallback(handleArchivePage).addBoth(lambda x: reactor.stop())
reactor.run()