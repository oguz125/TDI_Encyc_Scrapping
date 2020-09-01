#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 12:11:23 2020

@author: apolat
"""

import tabula
import unicodedata as ud
import requests
from bs4 import BeautifulSoup
import time
import pdfkit

'''
hyperparameters for pdf scrapping of the index pdf
'''

top = 145
left1 = 110
left2 = 299
width = 187
height = 567
number_of_pages = 525

#Sinple get function with multiple tries
def get_url_data(url, max_tries=3):
    remaining_tries = max_tries
    while remaining_tries > 0:
        try:
            return requests.get(url)
        except:
            time.sleep(10)
        remaining_tries = remaining_tries - 1
    return None

'''
Creates the list of entries using the provided 'maddeler.pdf'
'''
def maddeler():
    maddeler=[]
    
    for i in range(number_of_pages+1):
        if i==0:
            continue
        col1_raw = tabula.read_pdf('maddeler.pdf', encoding = 'utf-8', pages = i, area=[top,left1,top+height,left1+width], multiple_tables=False, pandas_options={'header':None})
        col2_raw = tabula.read_pdf('maddeler.pdf', encoding = 'utf-8', pages = i, area=[top,left2,top+height,left2+width], multiple_tables=False, pandas_options={'header':None})
        
        if len(col1_raw)>0:
            l1 = list(set(col1_raw[0][0].apply(madde_extractor).dropna().tolist()))
        if len(col2_raw)>0:
            l2 = list(set(col2_raw[0][0].apply(madde_extractor).dropna().tolist()))
        
        maddeler.extend(l1+l2)
        
        if i%50==0:
            print('%.0f/%.0f pages done!' %(i,number_of_pages))
    
    return list(set(maddeler))
    
'''
An auxilary function to create the list of entries that uses unicodedata package to detect arabic letters
'''
def madde_extractor(string):
    if string[:2]=='el' or ('CAPITAL' in ud.name(string[0]) and 'CAPITAL' in ud.name(string[1])):
        madde=''
        for h in string:
            if ud.name(h)=='COMMA' or 'ARABIC' in ud.name(h):
                break
            madde += h
        madde = madde.replace('(','')
        madde = madde.strip()
    else:
        madde = None
    return madde

'''
Given a search keyword returns the list of related entries
'''
def by_keyword(string):
    ret={}
    no_page=1
    url = 'https://islamansiklopedisi.org.tr/arama/'+string
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text,'html.parser')
    if len(soup.findAll('li', {'class':'number'}))>0:
        no_page=int(soup.findAll('li', {'class':'number'})[-1].text)
    for i in range(no_page):
        if i>1:
            url = 'https://islamansiklopedisi.org.tr/arama/'+string+'?q='+string+'&page='+str(i)
            page = requests.get(url, verify=False)
            soup = BeautifulSoup(page.text,'html.parser')
        for item in soup.findAll('div', {'class':"madde_liste_satir"}):
            key = item.find('a').text.split('\xa0')[0]
            href = 'https://islamansiklopedisi.org.tr'+item.find('a')['href']
            if key is not None:
                ret[key]=href
    return ret   

'''
Given an entry url returns and saves the article as html(default) or pdf 
'''

def get_article(url, save = True, as_pdf = False):
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text,'html.parser')
    html = str('<meta charset="utf-8">')
    header = soup.find('div', {'class':"article_title"})
    html += str(header)
    ret=[header]
    info = soup.find('div', {'class':"article_info"})
    if info is not None:
        html += str(info)
        ret.append(info)
    if soup.find('div', {'class':"pure-u-1 madde_sayfa_atif"}) is not None:
        body = soup.find('div', {'class':"pure-u-1 madde_sayfa_atif"})
        html += str(body)+str('<page>')
        ret.append(body)
    elif len(soup.findAll('div', {'class':"m-content"}))>0:
        body=''
        for item in soup.findAll('div', {'class':"m-content"}):
            body += str(item)
        html += str(body)
        ret.append(body)
    if save is True:
        with open("article.html", "w") as file:
            file.write(html)
        if as_pdf is True:
            pdfkit.from_file('article.html', 'article.pdf')
        ret=None
        
    return ret

            


