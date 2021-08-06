"""
list_jobs.py

Usage:
    list_jobs --type <type>

Options:
    -t --type TYPE
"""

from docopt import docopt #The above comment defines the arguments this script supports.

import requests
from requests_oauthlib import OAuth1
import os
import json

"""
   curl equivalent: -X GET "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
   returns job_details dictionary.
"""

URL = 'https://api.twitter.com/2/compliance/jobs'

def bearer_oauth(r):
    # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers['Authorization'] =  "Bearer {}".format(bearer_token)

    return r

def list_jobs(type):

    job_list = {}

    headers = {}
    #TODO: remove!
    headers['x-des-apiservices'] = 'staging1'

    #Injecting Job type into the request...
    response = requests.get(f"{URL}?job_type={type}", auth=bearer_oauth, headers=headers)

    if response.status_code != 200:
        print(f"Error requesting Job list: {response.status_code} | {response.text}")
        return job_list

    response_dict = response.json()
    job_list = response_dict['data']

    return job_list

if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    job_list = list_jobs(arguments['--type'])
    print(json.dumps(job_list, indent=4, sort_keys=True))

