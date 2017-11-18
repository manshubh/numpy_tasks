from datetime import datetime
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile

def sec_dataframe():
	url="https://www.sec.gov/help/foiadocsinvafoiahtm.html"
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page)
	table=soup.find('table', class_='list')
	a=[]
	for row in table.find_all("tr"):
	    for data in row.find_all("td"):
	        if data.find("a")!=None :
	            a.append(data.find("a"))


	data=pd.DataFrame(a,columns=['File_URL'])

	data["File_URL"]=data["File_URL"].apply(lambda x : "https://www.sec.gov" + str(x).split("href=\"")[1].split("\">")[0])
	data["Date"]=data["File_URL"]
	data["Date"]=data["Date"].apply(lambda x:x.split("/ia")[1][:6])

	data["Date"]=data["Date"].apply(lambda x:datetime.strptime(x,'%m%d%y'))
	data["type"]=data["File_URL"].apply(lambda x:"non-exempt" if x.split(".zip")[0][-6:]!="exempt" else "exempt")
	return data

def get_sec_zip_by_period(periods = [], is_exempt = False, only_most_recent=False):
	data=sec_dataframe()
	parse=pd.DataFrame()
	result=[]
	exempts="exempt" if is_exempt else "non-exempt"
	if len(periods)>0:
		for x in periods:
			parse=pd.concat([parse,data[data["Date"]==x][data["type"]==exempts]],axis=0)
	else:
		parse=pd.concat([parse,data[data["type"]==exempts][:1]],axis=0)

	listurl=list(parse["File_URL"])

	for url in listurl:
		urlreq=urllib.request.urlopen(url)
		zipfile = ZipFile(BytesIO(urlreq.read()))
		foofile = zipfile.open(zipfile.namelist()[0])
		result.append(pd.read_excel(foofile))
	return result



answer=get_sec_zip_by_period(is_exempt=True,only_most_recent=True)
print("A list of requested Dat Frames is returned")
print(type(answer))