import requests
import json
import os

class compliance_client:
    def __init__(self):
        self.domain = 'https://api.twitter.com'
        self.path = '/2/compliance/jobs'
        self.url = f"{self.domain}{self.path}"

        #self.config_file = './config/config.yaml'
        self.headers = {}

        #TODO - Remove
        self.headers['x-des-apiservices'] = 'staging1'

        self.ids_file_path = ""
        self.results_file_path = ""

        #TODO: Getting more fancy? Managing Job list?
        #self.inbox = './inbox'
        #self.outbox = './outbox'
        #self.ids_file_path = f"{Path(__file__).parent}/{self.inbox}/tweet_ids.txt"
        #self.results_file_path = f"{Path(__file__).parent}/{self.outbox}/results.txt"

        #'job_details' is the core Job object and is a Python dictionary. No defaults:
        self.job_details = {}

        self.resumable = False #TODO?

    # def authenticate(self):
    #     api_key = os.environ.get("API_KEY")
    #     api_secret = os.environ.get("API_SECRET")
    #     api_token = os.environ.get("API_TOKEN")
    #     api_token_secret = os.environ.get("API_TOKEN_SECRET")
    #
    #     auth = OAuth1(api_key, api_secret, api_token, api_token_secret)
    #
    #     return auth

    def bearer_oauth(self, r):
        # To set your environment variables in your terminal run the following line:
        # export 'BEARER_TOKEN'='<your_bearer_token>'
        bearer_token = os.environ.get("BEARER_TOKEN")
        r.headers['Authorization'] =  "Bearer {}".format(bearer_token)

        return r

    def make_results_file_name(id):
        return "results_file_name_root_" + id + ".json"

    def create_tweet_compliance_job(self, type, name):
        """
        curl equivalent: -X POST -H "Authorization: Bearer $BEARER_TOKEN" "https://api.twitter.com/2/tweets/compliance/jobs"
        return job_details dictionary.
        """
        self.headers['Content-type'] = 'application/json'

        #Set the Job request parameters.
        data = {}
        data['type'] = type
        data['name'] = name

        data =  json.dumps(data)

        self.name = name
        response = requests.post(self.url, data = data, auth = self.bearer_oauth, headers=self.headers)
        job_details = {}

        if response.status_code != 200:
            print(f"Error creating Compliance Job: {response.status_code} | {response.text}")
            return job_details #Empty dictionary is the sign that something went wrong.  

        response.encoding = 'utf-8'

        response_dict = response.json()
        job_details = response_dict['data']

        job_details['id'] = job_details['id']

        self.job_details = job_details

        return job_details #Passing back dictionary.
    
    def list_job(self, id):

        job_details = {}

        response = requests.get(f"{self.url}/{id}", auth=self.bearer_oauth, headers=self.headers)

        if response.status_code != 200:
            print(f"Error requesting Job details: {response.status_code} | {response.text}")
            return job_details

        response_dict = response.json()

        job_details = response_dict['data']

        job_details['id'] = job_details['id']

        return job_details


    def list_jobs(self, type):
        """
        Return a 'data' array of job objects.
       """
        job_list = {}

        #Optional request parameters: status, start_time, end_time
        response = requests.get(f"{self.url}?job_type={type}", auth=self.bearer_oauth, headers=self.headers)

        if response.status_code != 200:
            print(f"Error requesting Job list: {response.status_code} | {response.text}")
            return job_list

        response_dict = response.json()

        job_list = response_dict['data']

        return job_list

    def upload_ids(self, ids_file_path, url):

        self.headers['Content-Type'] = 'text/plain'

        data = {}

        #Not passing in auth details, since the Upload URL is already signed...
        response = requests.put(url, data=open(ids_file_path, 'rb'), headers=self.headers)

        if response.status_code != 200:
            print(f"Error uploading Tweet IDs: {response.status_code} | {response.text}")
            success = False
            return success
        else:
            success = True

        return success

    def download_results(self, url, results_file_path):

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error downloading results: {response.status_code} | {response.text}")
            success = False
            return success
        else:
            success = True

        try:
            with open(results_file_path, 'w') as f:
                f.write(response.text)
        except:
            print(f"Error writing results to {results_file_path}")
            success = False
            return success

        return success
   
if __name__ == "__main__":

    client = compliance_client()

    job_details = {}

    #A set of example calls used randomly for testing and learning. 
    
    #Create Tweet Compliance Job. User Compliance methods coming later.
    name = "Getting my archive compliant. Starting with Tweets..."
    type = 'tweets'
    job_details = client.create_tweet_compliance_job(type, name)
    
    #job_details['id'] = '12345' #Copy your Job ID here.

    #Look up details for a given Job ID.
    #job_details = client.list_job(job_details['id'])
    #print(f"Retreived Job details for Job ID {job_details['id']}: {job_details}")

    #Upload IDs
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
