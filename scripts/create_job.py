"""
   Creates a Compliance endpoint Job. This example hardcodes a Job *name*, but assigning a name is optional.

   This script returns JSON that describes the created Job:

   ```python

        job_details['name']
        job_details['job_id']
        job_details['upload_url']
        job_details['download_url']
        job_details['status']
        job_details['upload_expires_at']
        job_details['download_expires_at']

    ```

   curl equivalent: -X POST -H "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
   return job_details dictionary.

   This is a standalone script and has code in common with the other example scripts.
"""

import requests
from requests_oauthlib import OAuth1
import json
import os

URL = 'https://api.twitter.com/2/tweets/compliance/jobs'

# Reads in authentication tokens from the os.environ as strings.
#
# To set your enviornment variables in your terminal run the following line:
# export 'API_KEY'='<your_api_key>'
def authenticate():
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    api_token = os.environ.get("API_TOKEN")
    api_token_secret = os.environ.get("API_TOKEN_SECRET")

    auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

    return auth

#Make a POST request to the Compliance endpoint. Includes an optional 'job_name' request parameter.
# If successful, it returns a 'job_details' JSON object.
def create_tweet_compliance_job(name):

    auth = authenticate()

    response = requests.post(URL, data = {'job_name': name}, auth=auth)

    job_details = {}

    if response.status_code != 200:
        print(f"Error creating Compliance Job: {response.status_code} | {response.text}")
        return job_details #Empty dictionary is the sign that something went wrong.

    response_dict = response.json()
    data = response_dict['data']
    job_details = data['job']

    return job_details #Passing back dictionary.

if __name__ == "__main__":
    name = "My little job." #TODO: update with your Job name.

    #Create the Job.
    job_details = create_tweet_compliance_job(name)

    if len(job_details) == 0:
        print(f"Compliance Job could not be created.")
    else:
        print(f"New compliance Job created with name '{job_details['name']} amd ID {job_details['id']}:")
        print(json.dumps(job_details, indent=4, sort_keys=True))

