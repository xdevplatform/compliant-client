import requests
from requests_oauthlib import OAuth1
import os

"""
   curl equivalent: -X POST -H "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
   return job_details dictionary.
"""

URL = 'https://api.twitter.com/2/tweets/compliance/jobs'

def authenticate():
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    api_token = os.environ.get("API_TOKEN")
    api_token_secret = os.environ.get("API_TOKEN_SECRET")

    auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

    return auth

def create_tweet_compliance_job(name):

    auth = authenticate

    response = requests.post(URL, data = {'job_name': name}, auth=auth)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        pass

    response.encoding = 'utf-8'

    #print(response.text)
    response_dict = response.json()
    data = response_dict['data']
    job_details = data['job']

    return job_details #Passing back dictionary.

if __name__ == "__main__":
    name = "My example job."
    job_details = create_tweet_compliance_job(name)
    print(f"Created Job {job_details['job_id']}: Details: {job_details}")
