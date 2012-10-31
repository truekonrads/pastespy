#Pastebin related tests
# -*- coding: utf-8 -*- 
import os,inspect
from lib.pastebin import parsePastebinArchive, parsePastebinIndividualPaste
import unittest
os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
PASTEBIN_ARCHIVE_FILE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"pastebin.com_archive.html")
PASTEBIN_INDIVIDUAL_FILE_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"pastebin.com_individual.html")


class PastebinTest(unittest.TestCase):
	def test_archive_parser(self):
		firstFourResults=[
		['/w6FQeBnx', u'Untitled'], 
		['/iiNQUMdk', u'Untitled'], 
		['/Spdm3AJx', u'Untitled'], 
		['/n8eAtrZu', u'Untitled']]

		text=file(PASTEBIN_ARCHIVE_FILE_PATH,'rb').read()
		#text=UGLY_HACK
		self.assertEquals(parsePastebinArchive(text)[0:4],firstFourResults)

	def test_indivudal_parser(self):
		expectedResults={
		'author': 'a guest',
		'date': 'Oct 31st, 2012',
		'title': 'CXF XML'
		}
		text=file(PASTEBIN_INDIVIDUAL_FILE_PATH,'rb').read()
		self.assertEquals(parsePastebinIndividualPaste(text),expectedResults)
