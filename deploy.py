from __future__ import print_function

import boto3
import zipfile
import os
import sys
from pprint import pprint

def write_python_files_to_zipfile(out_zip, in_folder):
    files = [x for x in os.listdir(in_folder) if x.endswith('.py')]
    for file in files:
        out_zip.write(file)

def write_folder_to_zipfile(out_zip, in_folder):
    # based on http://stackoverflow.com/a/1855118/895407
    for root, dirs, files in os.walk(in_folder):
        for file in files:
            #print(file)
            if 'boto' in root: continue
            abs_path = os.path.join(root, file)
            relative_path = os.path.relpath(abs_path, in_folder)
            out_zip.write(abs_path, relative_path)

def create_zipfile():
    with zipfile.ZipFile('deployment_package.zip', 'w') as out_zip:
        write_python_files_to_zipfile(out_zip, '.')
        write_folder_to_zipfile(out_zip, 'env/Lib/site-packages')
    with open('deployment_package.zip', 'rb') as in_zip:
        return in_zip.read()

def create_function(function_name, role_name):
    print('Creating function called {} ...'.format(function_name))
    aws_lambda = boto3.client('lambda')
    print('...creating deployment package')
    zip_file_bytes = create_zipfile()
    print('...uploading function')
    response = aws_lambda.create_function(
        FunctionName=function_name,
        Runtime='python2.7',
        Role=role_name,
        Handler='handler.overstalk_handler',
        Code={
            'ZipFile': zip_file_bytes
        },
        Description='Check overstalk.io for updates'
    )
    print('...done')
    pprint(response)

def update_function(function_name):
    print('Creating function called {} ...'.format(function_name))
    aws_lambda = boto3.client('lambda')
    print('...creating deployment package')
    zip_file_bytes = create_zipfile()
    print('...uploading function')
    response = aws_lambda.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_file_bytes
    )
    print('...done')
    pprint(response)
        
if __name__ == '__main__':
    if len(sys.argv) < 3: print('Usage: deploy.py [create|update] [func_name] [role_arn]')
    elif sys.argv[1] == 'create': create_function(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'update': update_function(sys.argv[2])