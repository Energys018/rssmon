from qbittorrent import Client
import feedparser
import sqlite3
import certifi
import urllib3

def check_status(url):
    rss = feedparser.parse(url)
    if rss.status == 200:
        print("Connesction normal", rss.status)
    else:
        print("Some Econnection error", rss.status)
        exit(1)
def get_url(url):
    bzda = feedparser.parse(url)

def post_torrent(link):
    qb = Client('https://qbittorr.traefik.home.lab/')
    savepath = "/downloads/python"
    category = "LostFilm_RSS"
    qb.download_from_link(link, savepath=savepath, category=category)
    print(link)

def get_title(url):
    resolution = "1080p"
    bzda = feedparser.parse(url)
    if bzda.status == 200:
        numberOfHeadlines = len(bzda['entries'])
        for i in range(0,numberOfHeadlines):
            if resolution in bzda['entries'][i]['title']:
                print(bzda['entries'][i]['title'])
        print(bzda['entries'][i]['published']) #Date Time puplish
        print(bzda['entries'][i]['link'])
    else:
        print("Some connection error", bzda.status)



def get_link(url, resolution):
    bzda = feedparser.parse(url)
    tvList = ["Riverdale",
              "Snowpiercer",
              "Genius",
              "Nancy.Drew",
              "The.Walking.Dead",
              "WandaVision",
              "Resident.Alien"]
    if bzda.status == 200:
        numberOfHeadlines = len(bzda['entries'])
        for i in range(0,numberOfHeadlines):
            for tvShow in tvList:
                if tvShow in bzda['entries'][i]['title']:
                    if resolution in bzda['entries'][i]['title']:
                        post_torrent(bzda['entries'][i]['link'])



def insert_serials(name, resolution):
    conn = sqlite3.connect('example.db')
    #db = TinyDB("./db.json")
    #db.insert({"tvName": name, "tvResolution": resolution})
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tvShow
                         (tvName, tvResolution)''')
    c.execute('''INSERT INTO tvShow VALUES ("name",resulution)''')

def main():
    #insert_serials("WandaVision", "1080p")
    #insert_serials("Riverdale", "1080p")
    get_link("https://rss.bzda.ru/rss.xml", "1080p")

main()

#qb = Client('https://qbittorr.traefik.home.lab/', verify=False)


#get_title("https://rss.bzda.ru/rss.xml")


#check_status("https://rss.bzda.ru/rss.xml")


#for file in files:
#    if self.prefix in file 
