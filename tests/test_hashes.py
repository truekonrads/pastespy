#Hash related tests
# -*- coding: utf-8 -*- 

import unittest,os,inspect
from lib.hashfinder import findHashesInRawPaste
os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
SIMPLE_MD5_FILE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"simple_md5.txt")
# PASTEBIN_INDIVIDUAL_FILE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"pastebin.com_individual.html")
from twisted.python import log
class MyObserver():
	def __init__(self):
		self.messages=[]
	def observe(self,message):
		self.messages.append(message['message'])


class HashTest(unittest.TestCase):
	def test_find_simple_md5(self):
		# observer=MyObserver()
		# log.addObserver(observer.observe)

		text=file(SIMPLE_MD5_FILE_PATH,'rb').read()
		#text=UGLY_HACK
		hashwords=findHashesInRawPaste(text)
		self.assertTrue(len(hashwords)>0,"No messages received")
		for i in hashwords:
			if "80a751fde577028640c419000e33eba6" in i and "md5" in i:
				break
		else:
			self.fail("Expected md5 value not found :(")
		# self.assertEquals(parsePastebinArchive(text)[0:4],firstFourResults)

	
