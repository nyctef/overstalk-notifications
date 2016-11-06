from __future__ import print_function

import requests
from bs4 import BeautifulSoup
import boto3

def overstalk_handler(event, context):
    print('...pulling overstalk.io')
    r = requests.get('http://www.overstalk.io/?sources=BLIZZARD_FORUM&sources=REDDIT')
    print('...parsing html')
    soup = BeautifulSoup(r.text, 'html.parser')
    print('...scraping for last_modified_date:')
    last_modified_date = soup.find(class_='os-post')\
        .find(class_='os-post-meta')\
        .find('a', target='_blank')['title']
    print(last_modified_date)
        
if __name__ == '__main__':
    overstalk_handler(None, None)