"""
create_job.py

Usage:
    create_job --type <type> --name <name>

Options:
    -t --type TYPE
    -n --name NAME

"""

from docopt import docopt #The above comment defines the arguments this script supports.

"""
   Creates a Compliance endpoint Job. 

   This script returns JSON that describes the created Job:

   ```python

        job_details['name']
        job_details['id']
        job_details['upload_url']
        job_details['download_url']
        job_details['status']
        job_details['upload_expires_at']
        job_details['download_expires_at']
    ```
   curl equivalent: -X POST -H "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/compliance/jobs"
   return job_details dictionary.

   This is a standalone script and has code in common with the other example scripts.
"""

import requests
from requests_oauthlib import OAuth1
import json
import os

URL = 'https://api.twitter.com/2/compliance/jobs'

def bearer_oauth(r):
    # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers['Authorization'] =  "Bearer {}".format(bearer_token)

    return r

#Make a POST request to the Compliance endpoint. Includes an optional 'name' request parameter.
# If successful, it returns a 'job_details' JSON object.
def create_tweet_compliance_job(type, name):

    headers = {}
    headers['Content-type'] = 'application/json'
    headers['User-Agent'] = "BatchCompliancePythonScript"
    #TODO: remove!
    headers['x-des-apiservices'] = 'staging1'

    #Set the Job request parameters.
    data = {}
    data['type'] = type
    data['name'] = name

    data =  json.dumps(data)

    response = requests.post(URL, data = data, auth=bearer_oauth, headers=headers)

    job_details = {}

    if response.status_code != 200:
        print(f"Error creating Compliance Job: {response.status_code} | {response.text}")
        return job_details #Empty dictionary is the sign that something went wrong.

    response_dict = response.json()
    data = response_dict['data']
    job_details = data['job']

    return job_details #Passing back dictionary.

if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    #Create the Job.
    job_details = create_tweet_compliance_job(arguments['--type'], arguments['--name'])

    if len(job_details) == 0:
        print(f"Compliance Job could not be created.")
    else:
        print(f"New compliance Job created with name '{job_details['name']} and ID {job_details['id']}:")
        print(json.dumps(job_details, indent=4, sort_keys=True))

