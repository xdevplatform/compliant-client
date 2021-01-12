import requests
from requests_oauthlib import OAuth1
import os

"""
   curl equivalent: -X GET "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs/:id"
   returns job_details dictionary.
"""

URL = 'https://api.twitter.com/2/tweets/compliance/jobs'

def authenticate():
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    api_token = os.environ.get("API_TOKEN")
    api_token_secret = os.environ.get("API_TOKEN_SECRET")

    auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

    return auth

def list_job(id):

    auth = authenticate()

    job_details = {}

    response = requests.get(f"{URL}/{id}", auth=auth)

    if response.status_code != 200:
        print(f"Error requesting Job details: {response.status_code} | {response.text}")
        return job_details

    response_dict = response.json()
    data = response_dict['data']
    job_details = data['job']

    return job_details

if __name__ == "__main__":
    job_id = '' #Put your Job ID here.
    job_details = list_job(job_id)
    print(f"Job details: \n {json.dumps(job_details, indent=4, sort_keys=True)}")
