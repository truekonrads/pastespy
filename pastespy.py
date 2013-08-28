#!/usr/bin/python
from twisted.python import log
import logging
import treq,txmongo,datetime
from twisted.internet import reactor,defer
from twisted.web.client import HTTPConnectionPool
pool = HTTPConnectionPool(reactor, persistent=True)
pool.maxPersistentPerHost = 1
from treq import get
import sys,re,itertools
from lib.pastebin import parsePastebinArchive, parsePastebinIndividualPaste
from lib.hashfinder import findHashesInRawPaste
log.startLogging(sys.stdout)
from twisted.internet.task import LoopingCall, deferLater

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

IPADDRS=itertools.cycle(['0.0.0.0'])
CURRENTIP=None
class DoghouseException(Exception):
	pass

semaphore=defer.DeferredSemaphore(5)

def semaphoreGet(*args,**kwargs):
        kwargs['bindAddress']=CURRENTIP
        nargs=[get]
        nargs.extend(args)
	d=semaphore.run(*nargs,**kwargs)
	return d

def handleArchivePage(response):
	log.msg( "Archive page code is %s" % response.code)
	if response.code ==403:
		log.msg("Oh oh - looks like we're in the doghouse")
		CURRENTIP=next(IPADDRS)
		log.msg("Switching IP to %s" % str(CURRENTIP))
		raise DoghouseException("Couldn't get archive - code was %i" % response.code)
	d=treq.content(response).addCallback(parseArchiveResults)
	return d

def parseArchiveResults(text):
	
	pastes=[url[1:] for (url,name) in parsePastebinArchive(text)]
	d=findUniquePastes(pastes)
	d.addCallback(getIndividualPastes)
	return d

def getIndividualPastes(uniqueList):
	pages=[]
	log.msg("Fetching %i unique pastes" % len(uniqueList))
	for pasteID in uniqueList:
		fullPageDeferred=semaphoreGet("http://pastebin.com/%s" % pasteID.encode('utf8')).addCallback(treq.content)
		rawDeferred=semaphoreGet("http://pastebin.com/raw.php?i=%s" % pasteID.encode('utf8')).addCallback(treq.content)
		d=defer.DeferredList([fullPageDeferred,rawDeferred]).addCallback(handleIndividualPaste,pasteID)
		pages.append(d)	
	return defer.DeferredList(pages)
	

def handleIndividualPaste(dd,pasteID):
	(fullPageResponse,rawPageResponse)=dd
	if fullPageResponse[0] and rawPageResponse[0]:
		pageDetails=parsePastebinIndividualPaste(fullPageResponse[1])
		try:
			rawPaste=rawPageResponse[1].decode('utf8','ignore')
		except (UnicodeDecodeError,UnicodeEncodeError), e:
			log.msg("The type of rawPageResponse[1] is %s" % str(type(rawPageResponse[1])))
			log.msg(str(e))
			raise e
		try:
			pageDetails['snippet']=rawPaste.split("\n")[0]
			fixedPasteDetails={}
			for (k,v) in pageDetails.items():
				fixedPasteDetails[k]=v.encode('utf8','ignore')
		except (UnicodeDecodeError,UnicodeEncodeError), e:
			log.msg("The type of v for key %s  is %s" % (k,str(type(v))))
			log.msg(str(e))
			raise e
		for k in "author date title snippet".split(" "):
		    if not fixedPasteDetails.has_key(k):
			fixedPasteDetails[k]='__Unknown__'
		log.msg("%(author)s on %(date)s posted the following about `%(title)s': %(snippet)s" % fixedPasteDetails)
		hashwords=findHashesInRawPaste(rawPaste,["confident"])		
		for h in hashwords:
			log.msg("%s found in pastebin ID: %s" % (h,pasteID))
		return storePaste(pasteID,fixedPasteDetails,rawPaste,hashwords)

def findUniquePastes(archiveList):
	query={'pasteID' : { '$in' : archiveList}}
	d=MongoPool().getMongoConnection().addCallback(lambda cnx: cnx.pastebin.pastes.find(query,fields=['pasteID']))
	d.addCallback(lambda res: set(archiveList) - set([x["pasteID"] for x in res]))
	return d
	
def storePaste(pasteID,details,raw,hashwords):
	data=details.copy()
	data['pasteID']=pasteID
	data['raw']=raw
	data['hashwords']=hashwords
	d=MongoPool().getMongoConnection()
	return d.addCallback(lambda cnx: cnx.pastebin.pastes.insert(data))

@singleton
class MongoPool:
	_instance=None
	def __init__(self):
		self._connection=None
	
	def getMongoConnection(self):
		if self._connection:
			log.msg("Returning an existing Mongo connection",logLevel=logging.DEBUG)
			return defer.succeed(self._connection)
		else:
			d=txmongo.MongoConnection()
			return d.addCallback(self.storeMongoConnection)

	def storeMongoConnection(self,cnx):
		self._connection=cnx	
		return defer.succeed(self._connection)

def runIteration():
    now=datetime.datetime.now()
    d=semaphoreGet('http://pastebin.com/archive')
    d.addCallback(handleArchivePage)
    d.addCallback(lambda _: log.msg("Done with current iteration"))
    d.addErrback(log.err,'from runIteration')
    #d.addBoth(lambda x:deferLater(reactor,60,runIteration))
    d.addBoth(sleepAndRun)
    return d
	#d.addBoth(lambda x: reactor.stop())

def sleepAndRun(d):
    reactor.callLater(60,runIteration)

def main():
    if len(sys.argv)>1:
	global IPADDRS
	global CURRENTIP
	IPADDRS=itertools.cycle(sys.argv[1:])
        log.msg("Got %i IP adresses to cycle: %s" % (len(sys.argv[1:]),str(sys.argv[1:])))
        CURRENTIP=next(IPADDRS)
        log.msg("Using IP address %s" % str(CURRENTIP))
    runIteration()
    reactor.run()     

if __name__=="__main__":
    main()

