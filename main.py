#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 16:41:28 2020

@author: apolat
"""

from tdv_ia_funs import by_keyword, get_article

'''
start with a keyword and get search results
'''
keyword = 'rumi'
results = by_keyword(keyword)

'''
take a result from results and use its key to fetch url
if you want to get pdf output set as_pdf True (might not work in ide, use terminal)
if you want [header,info,body] output set save False, info might not exist
'''

