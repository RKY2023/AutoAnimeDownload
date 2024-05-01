import os
from bs4 import BeautifulSoup
import requests
import time
import datetime
from datetime import datetime as dt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import subprocess
import json
from winotify import Notification, audio
import requests
import json
from json import loads, dumps
import pandas as pd
import pymysql as ps
import pymongo

project_key = {}

csv_location = 'D:\\WORK\\MEGA_DATA_WAREHOUSE\\CSV\\anime_downloaded.csv'
anime_list = ['one-piece','kimetsu-no-yaiba-katanakaji-no-sato-hen','dr-stone-3','jujutsu-kaisen-2']
anime_list = ['one-piece','jujutsu-kaisen-2']
anime_list = ['one-piece','solo-leveling']
ts = time.time()
print('Run @', ts)

def initialize_json():
    global project_key
    myclient = pymongo.MongoClient("mongodb+srv://user_0:LksZss_WE76UdPP@publiccluster.xc4crqx.mongodb.net/?retryWrites=true&w=majority&appName=PublicCluster")
    mydb = myclient["Projects"]
    mycol = mydb["projects"]
    collist = mydb.list_collection_names()
    if "keys" in collist:
        print("The Keys collection exists.")
    x = mycol.find_one({ "_id": 'AutoAnimeDownloader' })
    print(x)
    exit()
    project_key = x

def winNotifier(name,title,msg,dur,ico):
    toast = Notification(app_id=name, title=title,msg=msg,duration="long",icon=r"D:\Images\positive-wallpapers-5330423.png")
    toast.set_audio(audio.Default, loop=False)
    toast.show()

def download(url): 
    success = 0
    # command to run
    cmd = 'rasdial "Windscribe IKEv2"'
    cmd2 = 'rasdial "Windscribe IKEv2" /DISCONNECT'

    # # run PowerShell command
    # result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
    # # print output
    # print(result.stdout)

    #the website URL
    #https://www.topcoder.com/thrive/articles/web-scraping-with-beautiful-soup
    #url_link = "https://nyaa.si/?f=0&c=0_0&q=one+piece"
    #url_link = "https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States"
    url_link = project_key['url_link'] +url
    result=""
    flag=1
    # print(url_link)
    while(flag):
        try:
            code = requests.get(url_link)
            if(code.status_code == 200):
                flag=0
                result = code.text
            print('connected')
        except:
            print('connecting..')

    doc = BeautifulSoup(result, "html.parser")
    #my_table=doc.select("a[href]")
    table=doc.find('table', class_='torrent-list')

    name=[]
    urls=[]
    try :
        td_list=table.find_all('td', colspan=2)
    except :
        td_list=[]
        return 0

    td_list=table.find_all('td', colspan=2)
    for td in td_list:
        ttt = td.find_all('a')
        for a in ttt[1: ]:
            name.append(a['title'])

    td_list=table.find_all('td', class_='text-center')
    print('------------------------------')
    # print(td_list)
    if(str(td_list).find('.torrent') > 0):
        print('Got torrent')
    print('------------------------------')

    for td in td_list:
        ttt = td.find_all('a')
        for a in ttt[1: ]:
            urls.append(a['href'])	
    if(str(urls).find('magnet') >= 0):
        print('Got magnet')
    # print(urls)
    for url in urls:
        success = 1
        os.startfile(url)
        
    # run PowerShell command
    result = subprocess.run(['powershell', '-Command', cmd2], capture_output=True, text=True)
    # print output
    print(result.stdout)
    #magnet:?xt=urn:btih:ef7847fbfdbe846b990cc367a507d10c46684d69&dn=%5BJudas%5D%20One%20Piece%20-%201011%20%5B1080p%5D%5BHEVC%20x265%2010bit%5D%5BMulti-Subs%5D%20%28Weekly%29&tr=http%3A%2F%2Fnyaa.tracker.wf%3A7777%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce
    #print(doc.prettify())
    return success

# This downloads the pending anime and then updates it.
def getUrlLinkCSV(): 
    df = pd.read_csv(csv_location)
    # print(df.to_string()) 

    # Get anime to download
    anime_to_download = df[df['downloaded'] == 0]
    # anime_to_download = df[(df['downloaded'] == 0) & (df['anime_name'] == 'one-piece')]
    # print(anime_to_download)
    # exit()
    result = anime_to_download.to_json(orient="index")
    # print(result)
    parsed = loads(result)
    # dumps(parsed, indent=2)

    for ani_dl in parsed:
        anime = parsed[ani_dl]
        print('Checking download stats', anime)
        # print(anime['anime_name'])
        # print((anime['timestamp'] - ts))
        link = anime['anime_name'].replace('-', '+')
        if( (anime['timestamp'] - ts) < 604800 ):
            time = dt.fromtimestamp(anime['timestamp']).strftime('%I:%M%p')
            day = dt.fromtimestamp(anime['timestamp']).strftime('%A')
            scheduleAnim(anime['anime_name'], day, time, str(anime['episode']))
        if(anime['timestamp'] > ts ):
            continue
        link+='+'+str(anime['episode'])
        link=link.replace(' ', '')
        # print(link)
        success =  download(link)
        if(success == 1):
            # update to dataframe
            df_up_index = df[(df['downloaded'] == 0) & (df['anime_name'] == anime['anime_name']) & (df['episode'] == anime['episode'])].index
            df['downloaded'][df_up_index] = 1
            deleteScheduleAnim(anime['anime_name'])
        if( (anime['timestamp'] - ts) < 604800 ):
            time = dt.fromtimestamp(anime['timestamp']).strftime('%I:%M%p')
            day = dt.fromtimestamp(anime['timestamp']).strftime('%A')
            scheduleAnim(anime['anime_name'], day, time, str(anime['episode']))
            
    # print(df)
    df.to_csv(csv_location, index=False)
def getUrlLinkFirebase():
    docs = db.collection('Anime').where('downloaded', '==', 0).stream()

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')
        link1 = doc.id
        link1 = link1.replace('-', '+')
        if doc.exists:
            # print(f'Document data: {doc.to_dict()}')
            data = doc.to_dict()
            if(data.get('timestamp') > ts ):
                continue
            link1+='+'+data.get('episode')
        link1=link1.replace(' ', '')
        download(link1)
        doc1 = db.collection('Anime').document(doc.id)
        doc1.update({'downloaded': 1})
# getUrlLinkFirebase()
def getUrlLinkSQL():
    try:
        cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
        cmd=cn.cursor()
        #here %S means string values 
        sql = "SELECT * FROM sys.animedownload WHERE DOWNLOAD=0"
        tuplescount = cmd.execute(sql)
        tuples = cmd.fetchall()
        print("Record Found:",tuplescount)
        for row in tuples:
            # print(row[2])
            link1 = row[0].replace('-', '+')
            dataTs = row[1]
            print(dataTs,ts)
            # if(dataTs > ts):
            #    continue
            # print(link1)
            link1+='+'+str(row[4])
            link1=link1.replace(' ', '')
            # print(link1)
            download(link1)
            # sql = "UPDATE sys.animedownload SET download=1 WHERE Name='"+row[0]+"'"
            # tuplescount = cmd.execute(sql)
        
        cn.commit()
        cn.close()

    except Exception as e:
        print(e)
# getUrlLinkSQL()
def scheduleAnim(ani, day, time, episode):
    action = "$action = New-ScheduledTaskAction -Execute 'D:\Work\HelpDesk\Windows\windows_crons\\runPy.bat'"
    trigger = "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek "+day+" -At "+time
    Register = "Register-ScheduledTask -Action $action -Trigger $trigger -TaskPath 'My Tasks' -TaskName 'Anime_Download_"+ani+"' -Description 'Episode: "+episode+"'"
    cmd = action + "; " + trigger + "; " + Register
    # print(cmd)
    result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
    print('Task Scheduled', ani, episode, result.stdout)
def deleteScheduleAnim(anime_name):
    cmd = 'schtasks /delete /tn "\My Tasks\Anime_Download_'+anime_name+'" /F'
    # print(cmd)
    result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
    print('Task Deleted', anime_name, result.stdout)
def getDataFirebase():
    for ani in anime:
        doc_ref = db.collection('Anime').document(ani)
        doc = doc_ref.get()
        if doc.exists:
            print(f'Document data: {doc.to_dict()}')
            data = doc.to_dict()
            dataTs = data.get('timestamp')
            if( (dataTs - ts) < 604800 ):
                time = dt.fromtimestamp(dataTs).strftime('%I:%M%p')
                day = dt.fromtimestamp(dataTs).strftime('%A')
                episode = data.get('episode')
                scheduleAnim(ani, day, time , episode)
                # if(result.stdout.contains('Ready')):
                #     toast = Notification(app_id="Task Scheduled", title="Anime Download",msg=day+" at "+time,duration="long",icon=r"D:\Images\positive-wallpapers-5330423.png")
                #     toast.set_audio(audio.Default, loop=False)
                #     toast.show()
        else:
            print('No such document!')
def getDataSQL():
    try:
        cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
        cmd=cn.cursor()
        #here %S means string values 
        sql = "SELECT * FROM sys.animedownload"
        tuplescount = cmd.execute(sql)
        tuples = cmd.fetchall()
        print("Record Found:",tuplescount)
        for row in tuples:
            # print(row[2])
            dataTs = row[1]
            print(row[0],dataTs - ts)
            if( (dataTs - ts) < 604800 ):
                time = dt.fromtimestamp(dataTs).strftime('%I:%M%p')
                day = dt.fromtimestamp(dataTs).strftime('%A')
                episode = row[4]
                print(time,day)
                scheduleAnim(row[0], day, time , str(episode))

        cn.commit()
        cn.close()

    except Exception as e:
        print(e)
    exit()
def checkNewSeason(url_link):
    try:
        result = requests.get(url_link).text
        doc = BeautifulSoup(result, "html.parser")
        information_section=doc.find('section', id='information-section-large')
        dateTime=information_section.find('time')["datetime"]
        out={}
        out['datetime'] = dateTime
        out['episode'] = 'null'
        out['outdated'] = True
        return out
    except NameError:
        print(NameError)
def checkAndUpdate():
    df = pd.read_csv(csv_location)
    df = pd.DataFrame(df)
    animeDataFrame = []
    try:
            
        for idx,ani in enumerate(anime_list):
            url_link = "https://animeschedule.net/anime/"+ani
            result = requests.get(url_link).text
            doc = BeautifulSoup(result, "html.parser")
            episode=doc.find('span', class_='release-time-episode-number')
            dateTime=doc.find('time', class_='release-time')
            if(hasattr(episode, 'text')):
                print(episode)
            else :
                # go for next season
                print('Check for new Season', url_link)
                animeInfo = checkNewSeason(url_link)
                if(animeInfo['outdated']):
                    print('Please update new Url for:', url_link)
                continue
            episode=episode.text.replace('Episode','')
            dateTime = dt.today().strftime("%Y") + " " + dateTime.text
            print(dateTime)
            timestamp=time.mktime(dt.strptime(dateTime,"%Y %A %d %b, %I:%M %p").timetuple())
            timestamp = timestamp+21600+18000
            # print(timestamp, dt.fromtimestamp(timestamp).strftime('%Y-%m-%d , %H:%M %p'))
            date1 = dt.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            time1 = dt.fromtimestamp(timestamp).strftime('%H:%M %p') # 01:00 pm
            time1 = dt.fromtimestamp(timestamp).strftime('%H:%M') # 13:00 
            
            # data = {"Age": 21, "Name": "emily", "likes":"pizza"}
            # db.collection('Users').document('LA').set(data)
            # data = {
            #     "timestamp": timestamp,
            #     "addedOn": datetime.datetime.now(tz=datetime.timezone.utc),
            #     "date": date1,
            #     "time": time1,
            #     "episode": episode,
            #     "downloaded": 0
            # }
            # exit()
            timestamp = int(timestamp)
            # print(ani, timestamp, date1, time1, episode)
            animeData = {idx:[ani, timestamp, date1, time1, episode, 0]}
            # print(animeData)
            # exit()
            animeData = pd.DataFrame(animeData)
            # animeData = animeData.T

            # print(len(animeDataFrame))
            # animeData = pd.DataFrame(animeData) 
            # sub1 =  pd.Series(sub) 
            if(len(animeDataFrame)== 0):
                animeDataFrame = pd.concat([animeData], axis=1)
            else :
                animeDataFrame = pd.concat([animeDataFrame, animeData], axis=1)
            # animeDataFrame = animeDataFrame.T
            
            # print(animeDataFrame)     
            # exit()
            # db.collection('Anime').document(ani).set(data)
        animeDataFrame = animeDataFrame.T # or animeDataFrame.transpose()
        animeDataFrame.columns =['anime_name', 'timestamp', 'date', 'time', 'episode', 'downloaded']
        print(animeDataFrame, '\nAdding data to CSV')
        df = pd.concat([df,animeDataFrame]).drop_duplicates().reset_index(drop=True)
        df.drop_duplicates(subset=['timestamp'], keep="first", inplace=True)
        print(df)
        df.to_csv(csv_location, index=False)
        # exit()

        # # USING SQL
        # try:
        #     cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
        #     cmd=cn.cursor()
        #     for i,row in animeDataFrame.iterrows():
        #         sql = "INSERT INTO sys.animedownload(Name,timestamp,date,time,episode,download) VALUES (%s,%s,%s,%s,%s,%s)"
        #         output = cmd.execute(sql, tuple(row))
        #         print(output)
        #         print("Record inserted: ", ani)
        #     cn.commit()
        #     cn.close()
        # except Exception as e:
        #     print(e)
        # # getDataFirebase()
        # getDataSQL()
        # exit()
    except NameError:
        print(NameError)
def insert_or_Update(update,animeDataFrame,ani):
    if(update):
        try:
            cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
            cmd=cn.cursor()
            for i,row in animeDataFrame.iterrows():
                # sql = "UPDATE sys.animedownload SET VALUES (%s,%s,%s,%s,%s,%s) WHERE Name='"+ani+"'"
                sql = "INSERT INTO sys.animedownload(timestamp,date,time,episode,download) VALUES (%s,%s,%s,%s,%s) WHERE Name='"+ani+"'"

                output = cmd.execute(sql, tuple(row))
                print(output)
                print("Record inserted: ", ani)
            cn.commit()
            cn.close()

        except Exception as e:
            print(e)
    else :
        try:
            cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
            cmd=cn.cursor()
            for i,row in animeDataFrame.iterrows():
                sql = "INSERT INTO sys.animedownload(Name,timestamp,date,time,episode,download) VALUES (%s,%s,%s,%s,%s,%s)"
                output = cmd.execute(sql, tuple(row))
                print(output)
                print("Record inserted: ", ani)
            cn.commit()
            cn.close()

        except Exception as e:
            print(e)


 #less than a week then schedule it
# def addtoSchedule(ts, tt):
# print(dt.today().strftime("%Y"))
