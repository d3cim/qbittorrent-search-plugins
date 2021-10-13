#VERSION: 1.1
#AUTHORS: quindecim, mauricci

from helpers import retrieve_url
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
import re, urllib.request, urllib.error, urllib.parse
from urllib.error import HTTPError

try:
    #python3
    from html.parser import HTMLParser
except ImportError:
    #python2
    from HTMLParser import HTMLParser
         
class solotorrent(object):
    url = 'https://solotorrent.group/'
    name = 'SoloTorrent'
    supported_categories = {'all': 'all'}
    
    class MyHTMLParser(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.url = 'https://solotorrent.group/'
            self.insideData = False
            self.insideDataTitle = False
            self.fullResData = []
            self.singleResData = self.getSingleData()
            
        def getSingleData(self):
            return {'name':'-1','seeds':'-1','leech':'-1','size':'-1','link':'-1','desc_link':'-1','engine_url':self.url}
        
        def handle_starttag(self, tag, attrs):
            if tag == 'li' and dict(attrs).get('class','').lower().find('s-item') != -1:
                self.insideData = True
            if self.insideData and tag == 'a' and len(attrs) > 0:
                 Dict = dict(attrs)
                 if 'href' in Dict:
                     self.singleResData['desc_link'] = Dict['href']
                     self.insideDataTitle = True
                     
        def handle_data(self, data):
            if self.insideData and self.insideDataTitle:
                if self.singleResData['name'] == '-1':
                    self.singleResData['name'] = data.strip()
                else:
                    self.singleResData['name'] += data.strip()

        def handle_endtag(self, tag):
            if tag == 'a':
                self.insideDataTitle = False
            if tag == 'li':
                self.insideData = False
                if len(self.singleResData) > 0:
                    #ignore trash stuff
                    if self.singleResData['name'] != '-1':
                        if self.singleResData['desc_link'] != '-1' or self.singleResData['link'] != '-1':
                            prettyPrinter(self.singleResData)
                            self.fullResData.append(self.singleResData)
                    self.singleResData = self.getSingleData()

        def feed(self,html):
            HTMLParser.feed(self,html)
            self.insideData = False
            self.insideDataTitle = False


    def getHtml(self, url):
        #The server is badly configured, it returns search results with 500 error
        res = ''
        user_agent = 'Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0'
        headers    = {'User-Agent': user_agent}
        req = urllib.request.Request(url, headers = headers)
        try:
            handler = urllib.request.urlopen(req)
            res = handler.read()
        #500 error, i need to bypass and get results anyway
        except HTTPError as e:
            res = e.read()
        return str(res)
        
    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        currCat = self.supported_categories[cat]
        what = what.replace('%20','+')
        parser = self.MyHTMLParser()
        #analyze firt 5 pages
        for currPage in range(1,6):
            url = self.url+'/page/{1}?s={0}'.format(what,currPage)
            #print(url)
            html = self.getHtml(url)
            parser.feed(html)
            if len(parser.fullResData) <= 0:
                break
        data = parser.fullResData
        parser.close()

if __name__ == "__main__":
    s = solotorrent()
    s.search('tomb%20raider')
