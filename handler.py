import requests
from bs4 import BeautifulSoup

def overstalk_handler(event, context):
    r = requests.get('http://www.overstalk.io/?sources=BLIZZARD_FORUM&sources=REDDIT')
    soup = BeautifulSoup(r.text, 'html.parser')
    soup.find(class_='os-post').find(class_='os-post-meta').find('a', target='_blank')['title']