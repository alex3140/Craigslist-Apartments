#Scrapes data from apartment and condo listings from Craigslist website
from bs4 import BeautifulSoup
import MySQLdb 
from sqlalchemy import create_engine
import pandas as pd
from pandas.io import sql
import re
import urllib2

class Scraper:

    def __init__(self, region):
        '''
            Arguments:
            region - Craigslist region, e.g., 'washingtondc', 'sfbay', etc. 
        '''
        self.df = pd.DataFrame(columns=['price',
                                     'latitude',
                                     'longitude',
                                     'footage',
                                      'num_br',
                                      'num_ba',
                                      'type',
                                      'url'])
                                      
        self.conn = MySQLdb.connect(user="root", passwd="mysql", db="apts")
        self.table = "scraped"
        self.url_root = "http://" + region + ".craigslist.org"
        self.region = region
        
    def scrape(self, start, end):
        '''
        Scrapes Craigslist pages
        Args:
            start, end define range of posts to consider (int)
        '''
        for page_index in range(start, end, 100):
            print("Scraping page_index = " + str(page_index))
            self.scrape_page(page_index)
            
    def find_lat_lon(self, bsObj):
        '''
        Args:
            bsObj - Beatiful soup object from Craigslist ad
            Returns latitude and longitude (floats)
        '''
        if bsObj.find(id = "map"):
            latitude = bsObj.find(id = "map").attrs['data-latitude']
            longitude = bsObj.find(id = "map").attrs['data-longitude']
        
            return latitude, longitude
        else:
            return None, None
            
    def find_footage(self, bsObj):
        if bsObj.find(class_ = "attrgroup"):
            string = bsObj.find(class_ = "attrgroup").text
            result = re.search(r"\b([0-9]*ft2)\b", string)
            if result:
                footage = int(result.group(0)[:-3])
                return footage
            else:
                return None
        else:
            return None
    
    #find number of bedrooms
    def find_br(self, bsObj):
        if bsObj.find(class_ = "attrgroup"):
            string = bsObj.find(class_ = "attrgroup").text
            result = re.search(r"\b([0-9]BR)\b", string)           
            if result:
                return float(result.group(0)[:-2])
            else:
                return None
        else:
            return None
    
    
    def find_ba(self, bsObj):
        '''
            Finds number of bathrooms
        '''
        if bsObj.find(class_ = "attrgroup"):
            string = bsObj.find(class_ = "attrgroup").text
            result = re.search(r"\b([1-5]Ba)\b", string)            
            if result:
                return float(result.group(0)[:-2])
            else:
                return None
        else:
            return None
            
    def find_type(self, bsObj):
        for group in bsObj.findAll(class_ = "attrgroup"):
            if group.find("span", text="apartment"):
                return "apt"
            elif group.find("span", text="condo"):
                return "condo" 
        return "else"

    def scrape_page(self, page_index):
        '''
        Scrapes a listing
        Args:
            page_index - Craigslist search page index, e.g. 100, 200, etc.
        '''
        #url = self.url_root + "/search/apa?s=" + str(page_index) + ".html"
        url = self.url_root + "/search/apa?s="+ str(page_index)+\
                    "&housing_type=1&housing_type=2"
        html = urllib2.urlopen(url)
        bsObj = BeautifulSoup(html)
        rows = bsObj.find_all("p", class_="row")
        
        for row in rows:
            try:
                price_tag = row.find("span", class_="price")
                
                if price_tag:

                    price = int(price_tag.text.replace('$', ''))

                    # Follow link and read page
                    apt_link = row.find("a").attrs["href"]
                    apt_page = urllib2.urlopen(self.url_root + apt_link)
                    bsObj = BeautifulSoup(apt_page)
                    #body = soup.find(id="postingbody").text

                    # Find latitude and longitude
                    latitude, longitude = self.find_lat_lon(bsObj)
                    
                    #Find footage
                    footage = self.find_footage(bsObj)
                    
                    #Find number of bedrooms and bathrooms
                    num_br = self.find_br(bsObj)     
                    num_ba = self.find_ba(bsObj)   
                    
                    #Find type
                    type_apt=self.find_type(bsObj)

                    # Include in dataframe if latitude and longitude
                    # were found and if listing had not been found before
                    if longitude and latitude and \
                            (apt_link not in list(self.df.url)):
                        df_row = pd.DataFrame([{'price': price,    
                                            'latitude': latitude,
                                            'longitude': longitude,
                                            'footage':footage,
                                            'num_ba':num_ba,
                                            'num_br':num_br,
                                            'url':apt_link,
                                            'type':type_apt}])
                                                
                        self.df = self.df.append(df_row, ignore_index=True)

                        print "Processing:", apt_link,"\n"
            except:
               print("\n Error occurred!\n")
        
    def save(self, create_or_add):
        '''
        Saves scraped data to database. User can choose whether
        to create a new database table or to add entries to 
        existing table.
        Arguments:
            create_or_add - 'create' or 'add'. 
        '''
            
        if create_or_add == 'create':
            self.df.to_sql(con=self.conn, name=self.table, 
                       if_exists='replace', flavor='mysql')
            
        elif create_or_add == 'add':
            self.df.to_sql(con=self.conn, name=self.table, 
                       if_exists='add', flavor='mysql')
        else:
            raise ValueError("Please provide 'create' or 'add'")
        

s = Scraper("washingtondc")
s.scrape(0,2500)

s.df.to_csv('C:\\Users\\alex314\\Desktop\\CraigslistProject\\craigslist_data.csv')


engine = create_engine('mysql://root:mysql@localhost/apts', echo=False)
result.to_sql('load_data', engine, if_exists='replace')

s.df.to_sql(con=s.conn, name=s.table, if_exists='replace', flavor='mysql')
