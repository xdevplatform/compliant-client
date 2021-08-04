"""
list_job.py

Usage:
    list_job --id <id>

Options:
    -i --id ID
"""


from docopt import docopt #The above comment defines the arguments this script supports.

import requests
from requests_oauthlib import OAuth1
import os
import json

"""
   curl equivalent: -X GET "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs/:id"
   returns job_details dictionary.
"""

URL = 'https://api.twitter.com/2/compliance/jobs'

def bearer_oauth(r):
    # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers['Authorization'] =  "Bearer {}".format(bearer_token)

    return r

def list_job(id):

    job_details = {}

    headers = {}
    #TODO: remove!
    headers['x-des-apiservices'] = 'staging1'

    response = requests.get(f"{URL}/{id}", auth=bearer_oauth, headers=headers)

    if response.status_code != 200:
        if response.status_code == 404:
            print(f"Job ID {id} not found. Please check ID.")
        else:
            print(f"Error requesting Job details: {response.status_code} | {response.text}")
        return job_details

    response_dict = response.json()
    #data = response_dict['data']
    #job_details = data['job']

    return response_dict['data']

if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    job_details = list_job(arguments['--id'])

    if len(job_details) == 0:
        print(f"Compliance Job not found or error occurred.")
    else:
        print(f"Job details for ID {job_details['id']}:")
        print(json.dumps(job_details, indent=4, sort_keys=True))

