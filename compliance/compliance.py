import requests
from requests_oauthlib import OAuth1
import json
import os

class compliance_client:
    def __init__(self):
        self.domain = 'https://api.twitter.com'
        self.path = '/2/tweets/compliance/jobs'
        self.url = f"{self.domain}{self.path}"

        #self.config_file = './config/config.yaml'
        self.headers = {}
        self.auth = self.authenticate() #Set up authentication when class is created.

        self.ids_file_path = ""
        self.results_file_path = ""

        #TODO: Getting more fancy? Managing Job list?
        #self.inbox = './inbox'
        #self.outbox = './outbox'
        #self.ids_file_path = f"{Path(__file__).parent}/{self.inbox}/tweet_ids.txt"
        #self.results_file_path = f"{Path(__file__).parent}/{self.outbox}/results.txt"

        #No defaults:
        self.job_details = {}

        self.resumable = False #TODO?

    def authenticate(self):
        api_key = os.environ.get("API_KEY")
        api_secret = os.environ.get("API_SECRET")
        api_token = os.environ.get("API_TOKEN")
        api_token_secret = os.environ.get("API_TOKEN_SECRET")

        auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

        return auth

    def make_results_file_name(job_id):
        return f"results_file_name_root_{job_id}.json"

    def create_tweet_compliance_job(self, job_name):
        """
        curl equivalent: -X POST -H "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
        return job_details dictionary.
        """
        self.name = job_name
        response = requests.post(self.url, data = {'job_name': job_name}, auth = self.auth, headers=self.headers)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
            pass

        response.encoding = 'utf-8'

        response_dict = response.json()
        data = response_dict['data']

        job_details = data['job']
        job_details['job_id'] = job_details['id'] #TODO: return 'job-id' instead?

        self.job_details = job_details

        return job_details #Passing back dictionary.

    def list_job(self, job_id):

        response = requests.get(f"{self.url}/{job_id}", auth=self.auth, headers=self.headers)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
            pass

        response_dict = response.json()

        data = response_dict['data']
        job_details = data['job']

        job_details['job_id'] = job_details['id'] #TODO: for consistency, seems this attribute should be returned as 'job_id'

        return job_details

    #TODO: Method not available yet.
    def list_jobs(self):
        """
        Return a 'data' array of job objects.
        """
        #Optional request parameters: status, start_time, end_time
        response = requests.get(self.url, auth = self.auth, headers=self.headers)

        if response.status_code != 200:
            print(response._content)
            raise Exception(response.status_code, response.text)
            pass

        print(json.dumps(response, indent=4, sort_keys=True))

        return json.loads(response)

    def upload_ids(self, ids_file_path, url):
        success = False

        self.headers['Content-Type'] = 'text/plain'

        data = {}

        #Not passing in auth details, since the Upload URL is already signed...
        response = requests.put(url, data=open(ids_file_path, 'rb'), headers=self.headers)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
            pass
        else:
            success = True

        return success

    def download_results(self, url, results_file_path):

        success = False

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
            return success

        with open(results_file_path, 'w') as f:
            f.write(response.text)

        success = True

        return success

if __name__ == "__main__":

    client = compliance_client()

    #TODO: Load in configuration? Should we persist Job metadata, or wait until list_jobs is available.
    #Load Job details from config YAML file?
    #TODO: Code for loading in Job metadata.
    #with open(r'./jobs/job_1331380573407825920.yaml') as file:
    #    job_details = yaml.load(file)

    job_details = {}

    job_details['job_id'] = '12345' #Copy your Job ID here.

    #Create Tweet Compliance Job. User Compliance methods coming later.
    #name = "Getting my archive compliant."
    #job_details = client.create_tweet_compliance_job(name)

    #TODO: Look up details for a given Job ID.
    job_details = client.list_job(job_details['job_id'])
    print(f"Retreived Job details for Job ID {job_details['job_id']}: {job_details}")

    #TODO: Upload IDs
    #compliance_client.ids_file_path = "../inbox/tweet_ids.txt"
    #success = client.upload_ids(compliance_client.ids_file_path, job_details['upload_url'])

    #Download Job
    if job_details['status'] == 'complete':

        #TODO: Loading an example download URL.
        #job_details['download_url'] = '' 

        compliance_client.results_file_path = "../outbox/results.json" #TODO: create if needed!
        success = client.download_results(job_details['download_url'], compliance_client.results_file_path)
    else:
        print(f"Job has status: {job_details['status']}")
