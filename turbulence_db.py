from datetime import datetime, timezone
import time
from bs4 import BeautifulSoup
import requests
import ssl
import urllib.request

def get_files():
    ssl._create_default_https_context = ssl._create_unverified_context
    page = requests.get('https://tgftp.nws.noaa.gov/SL.us008001/DC.avspt/DS.gtggb/PT.grid_DF.gr2/')
    soup = BeautifulSoup(page.content, 'html.parser')
    table_rows = soup.find_all('tr')
    for row in table_rows:
        if 'sn.' in row.text:
            search_date, search_time = row.text[11:30].split(' ')[0], row.text[11:30].split(' ')[1].replace(':',"")
            file_name = str(search_date) + '_' + str(search_time)
            now_file = 'https://tgftp.nws.noaa.gov/SL.us008001/DC.avspt/DS.gtggb/PT.grid_DF.gr2/' + row.text[0:11]
            path_file = 'BINs/' + str(file_name)+'.bin'
            with urllib.request.urlopen(now_file) as response, open(path_file, 'wb') as out_file:
                data = response.read()
                out_file.write(data)

import os
from os import listdir
from os.path import isfile, join
ssl._create_default_https_context = ssl._create_unverified_context
onlyfiles = [f for f in listdir('BINs') if isfile(join('BINs', f))]


def update_files():
    page = requests.get('https://tgftp.nws.noaa.gov/SL.us008001/DC.avspt/DS.gtggb/PT.grid_DF.gr2/')
    soup = BeautifulSoup(page.content, 'html.parser')
    table_rows = soup.find_all('tr')
    rows = []
    for row in table_rows:
        if 'sn.' in row.text:
            search_date, search_time = row.text[11:30].split(' ')[0], row.text[11:30].split(' ')[1].replace(':',"")
            file_name = str(search_date) + '_' + str(search_time)
            rows.append(file_name)
    rows = sorted(rows)
    files = [file for file in onlyfiles]

    def find_filename(new_filename_list):
        formatted = []
        for new_file in new_filename_list:
            date = new_file.split('_')[0]
            time = new_file.split('_')[1][0:2] + ':' + new_file.split('_')[1][2:4]
            formatted.append((date, time))
        indexer = 0
        file_names = []
        try:
            for row in table_rows:
                if 'sn.' in row.text:
                    if formatted[indexer][0] in row.text and formatted[indexer][1] in row.text:
                        file_names.append(row.text[0:11])
                        indexer +=1
        except IndexError:
            pass
        return list(zip(file_names, new_filename_list))


    def most_recent(db_list, live_list):
        ###return a list of the outdated DATABASE files and the newest LIVE URL files
        database_files = [file.strip('.bin') for file in db_list]
        delete_files=[]
        new_files = []
        for ind_file in database_files:
            if ind_file not in live_list:
                delete_files.append(ind_file+'.bin')
        for new_file in live_list:
            if new_file not in database_files:
                new_files.append(new_file)
        return delete_files, new_files

    new_file_list = most_recent(files, rows)[1]
    old_file_list = most_recent(files, rows)[0]

    print('ADDED')
    for new_file_path, new_filename in find_filename(new_file_list):
        new_url = 'https://tgftp.nws.noaa.gov/SL.us008001/DC.avspt/DS.gtggb/PT.grid_DF.gr2/' + new_file_path
        path_file = 'BINs/' + str(new_filename)+'.bin'

        with urllib.request.urlopen(new_url) as response, open(path_file, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            print(path_file.strip('BINs/'))

    print('REMOVED')
    for old_files in old_file_list:
        file_path = 'BINs/' + str(old_files)
        os.remove(file_path)
        print(old_files)



update_files()