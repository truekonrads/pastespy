from bs4 import BeautifulSoup

def parsePastebinArchive(response):
	soup=BeautifulSoup(response)
	table=soup.find("table",class_="maintable")
	links=table("a",href=lambda h: not h.startswith("/archive"))
	return map(lambda x: [x['href'],x.text],links)

