from bs4 import BeautifulSoup
import re
def parsePastebinArchive(response):
	soup=BeautifulSoup(response)
	table=soup.find("table",class_="maintable")
	links=table("a",href=lambda h: not h.startswith("/archive"))
	return map(lambda x: [x['href'],x.text],links)



# <div class="paste_box_info">
# 			<div class="paste_box_line1" title="CXF XML"><img src="/i/t.gif"  class="i_p0" width="16" height="16" title="Public paste, everybody can see this paste." alt=""  border="0" /><h1>CXF XML</h1> </div>
# 			<div class="paste_box_line2">By: a guest  on Oct 31st, 2012 &nbsp;|&nbsp; syntax: <a href="/archive/xml">XML</a> &nbsp;|&nbsp; size: 0.47 KB &nbsp;|&nbsp; hits: 17 &nbsp;|&nbsp; expires: in 23 hours</div>
# 			<div class="paste_box_line3"><a href="/download.php?i=FDs3spZv" rel="nofollow">download</a> &nbsp;|&nbsp; <a href="/raw.php?i=FDs3spZv" target="_blank" rel="nofollow">raw</a> &nbsp;|&nbsp; <a href="/embed.php?i=FDs3spZv" rel="nofollow">embed</a> &nbsp;|&nbsp; <a href="/report.php?i=FDs3spZv" rel="nofollow">report abuse</a></div>
# 		</div>


def parsePastebinIndividualPaste(response):
	soup=BeautifulSoup(response)
	div=soup.find("div",class_="paste_box_info")
	title=div.find("h1").text
	line2=div.find("div",class_="paste_box_line2").text
	# print line2
	author,pasteDate=re.search("^By: (.+?) on (\w+ \d+\w+, \d+)",line2).groups()
	return {
		"title":title,
		"author":author.strip(),
		"date":pasteDate,
	}

