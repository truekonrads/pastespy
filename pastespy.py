#!/usr/bin/python

from twisted.internet import reactor,defer
from treq import get
from lib.pastebin import parsePastebinArchive

def handleArchivePage(response):
	print "[*] Code is %s" % response.status_code
	response.text.addCallback(parseArchiveResults)

def parseArchiveResults(text):
	for (url,name) in parsePastebinArchive(text):
		pasteID=url[1:]
		print "`%s' has ID %s" % (name,pasteID)
		fullPageDeferred=get("http://pastebin.com/%s", pasteID)
		rawDeferred=get("http://pastebin.com/raw.php?i=%s" pasteID)
		defer.DeferredList([fullPageDeferred,rawDeferred]).addCallback(handleIndividualPaste,pasteID)
def handleIndividualPaste(paste)
	print 
	reactor.stop()
d=get('http://pastebin.com/archive').addCallback(handleArchivePage)
reactor.run()