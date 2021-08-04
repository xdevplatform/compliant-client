import requests
from requests_oauthlib import OAuth1
import os
import json

"""
   curl equivalent: -X GET "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
   returns job_details dictionary.
"""

URL = 'https://api.twitter.com/2/compliance/jobs'

def authenticate():
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    api_token = os.environ.get("API_TOKEN")
    api_token_secret = os.environ.get("API_TOKEN_SECRET")

    auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

    return auth

def list_jobs(job_type):

    auth = authenticate()

    job_list = {}

    response = requests.get(f"{URL}?job_type={job_type}", auth=auth)

    if response.status_code != 200:
        print(f"Error requesting Job list: {response.status_code} | {response.text}")
        return job_list

    response_dict = response.json()
    job_list = response_dict['data']

    return job_list

if __name__ == "__main__":
    job_list = list_jobs()
    print(json.dumps(job_list, indent=4, sort_keys=True))

    job_type = 'tweets' #Put the job type here: 'tweets or users.
    job_details = list_jobs(job_type)
    print(f"Job details: \n {json.dumps(job_details, indent=4, sort_keys=True)}")

