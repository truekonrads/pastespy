#!/usr/bin/python

from twisted.internet import reactor
from treq import get
from lib.pastebin import parsePastebinArchive

def handleArchivePage(response):
	for (url,name) in parsePastebinArchive(response.text):
		print "%s is at %s" % (name,url)
	reactor.shutdown()
d=get('http://pastebin.com/archive').addCallback(handleArchivePage)

reactor.run()