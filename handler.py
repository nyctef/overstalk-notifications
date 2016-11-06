from __future__ import print_function

import requests
from bs4 import BeautifulSoup
import boto3
import dateutil
import config

def read_s3(key):
    s3 = boto3.client('s3')
    return s3.get_object(
        Bucket='overstalk-notifications-bucket',
        Key=key
    )
def read_s3_string(key):
    return read_s3(key)['Body'].read().decode('utf8')
    
def write_s3(key, bytes):
    s3 = boto3.client('s3')
    return s3.put_object(
        Bucket='overstalk-notifications-bucket',
        Key=key,
        Body=bytes
    )
def write_s3_string(key, string):
    return write_s3(key, string.encode('utf8'))
    
def send_email(subject, body):
    ses = boto3.client('ses')
    return ses.send_email(
        Source=config.email,
        Destination={'ToAddresses': [config.email]},
        Message={
            'Subject':{'Data':subject},
            'Body':{'Text':{'Data':body}, 'Html':{'Data':body}},
        }
   )

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
    print('...parsing')
    parsed_last_modified_date = dateutil.parser.parse(last_modified_date)
    print(repr(parsed_last_modified_date))
    
    print('... reading previous-last-modified-date')
    try:
        previous_last_modified_date = read_s3_string('previous-last-modified-date')
        parsed_previous_last_modified_date = dateutil.parser.parse(previous_last_modified_date)
    except Exception as e:
        print('... reading previous-last-modified-date failed')
        print(e)
        previous_last_modified_date = parsed_previous_last_modified_date = None
    print(previous_last_modified_date, repr(parsed_previous_last_modified_date))
    
    print('...checking if updated date has updated')
    if parsed_previous_last_modified_date is None or\
        parsed_last_modified_date > parsed_previous_last_modified_date:
        print('an update has happened')
        print('...sending email')
        send_email('overstalk.io has been updated',
            'http://www.overstalk.io/?sources=BLIZZARD_FORUM&sources=REDDIT has been updated')
        print('...email sent')
    else:
        print('update not detected')
    
    write_s3_string('previous-last-modified-date', last_modified_date)
        
if __name__ == '__main__':
    overstalk_handler(None, None)