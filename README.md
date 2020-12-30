# The Compliant (python) client

This **compliant-client** repository hosts a set of simple Python scripts for the Compliance endpoints. There is also a 
more elaborate example 'compliant-client' script that helps manage Compliance Jobs and their lifecycles. 

The 'compliant-client.py' script lets you provide all that is needed in one "all" command. The script creates a new Job, uploads
the specified Tweet ID file, checks on the Job status every 30 seconds, then downloads the results when the Job completes.  

Here is an example command-line:   

```bash
$python compliant-client.py --all --name "MyJob" --ids-file "../inbox/tweet_ids.txt" --results-file "../outbox/results.json"
```
 
## Getting started

   + Setting up access to Compliance endpoint:  
   + Authentication:  
   + Preparing Tweet (and User) ID files. IDs should be in simple text with one ID per line. When uploading 
   the files, a 'Content-Type' header should be set to 'text/plain'. 
   + Build methods to update Tweet archives. 
 
## Job attributes and lifecycles 
 
Compliance Jobs have the following life-cycle:


{summary}


* Job are created with an optional (and recommended) name. The 'create' process creates a new job with the following attributes:
 
```json
{
    "id": "12345678888888",
    "name": "ArchivedTweets_2017_09",
    "status": "created",
    "upload_expires_at": "YYYY-MM-DDTHH:mm:ss.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/12345678888888/submission..."
}
```

 
* Tweet IDs are uploaded to a cloud file system. Tweet IDs are written to a simple text file with one ID per line. 


```json
{
    "upload_expires_at": "YYYY-MM-DDTHH:mm:ss.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/12345678888888/submission..."
}
```

* Uploaded Tweets are checked for Compliance, a process that can take many minutes (and hours?) to complete. 

```json
{
  "status": "processing"
}

```

The Job will remain in the "processing" status until it finishes and enters a final "completed" status


```json
{
    "download_expires_at": "YYYY-MM-DDTHH:mm:ss.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/12345678888888/delivery/...",
    "id": "12345678888888",
    "name": "ArchivedTweets_2017_09",
    "status": "complete"
}    
```

* After the job is 'completed', the results can be downloaded from a cloud file service. 

```json
{
    "download_expires_at": "YYYY-MM-DDTHH:mm:ss.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/12345678888888/delivery/..."
}
```

## Compliance results objects  
  
  Here is an example:
  
  ```json
  {
	  "id": "906972198136631298",
	  "action": "delete",
	  "created_at": "2017-09-10T20:06:37.421Z",
	  "redacted_at": "2020-07-21T23:37:55.607Z",
	  "reason": "deleted"
  }
 ``` 


## Setting up authentication

To set your enviornment variables in your terminal run the following line:

```bash
export 'API_KEY'='<your_api_key>'
```

```python
import requests
from requests_oauthlib import OAuth1
import os


def authenticate():
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    api_token = os.environ.get("API_TOKEN")
    api_token_secret = os.environ.get("API_TOKEN_SECRET")

    auth = OAuth1(api_key, api_secret, api_token, api_token_secret)

    return auth
```

## Simple scripts
### compliant-client/scripts

The /scripts folder contains a set of Python scripts for the compliance endpoints. These scripts can be used to create 
and manage Compliance Jobs and their lifecycles:

These scripts all include a 'main' section that includes some hardcoded settings such as a Job's name or ID. 

```python
if __name__ == "__main__":
    name = "My example job."
    job_details = create_tweet_compliance_job(name)
    print(f"Created Job {job_details['job_id']}: Details: {job_details}")
```
There are five scripts:
  1) **create_job.py** Creating a Job: 
  2) **list_jobs.py** Requesting a list of all existing Jobs: 
  3) **list_job.py** Checking on a specific Job status and retrieving its details: 
  4) **upload_ids.py**Uploading a text file with Tweet IDs (one per line):  
  5) **download_results.py** Downloading results which consist of one JSON object for each Tweet that has had Compliance event (e.g. has been 
  deleted):  

## Example client
+ compliant-client/apps/compliant-client.py
+ Command-line app for working with the Twitter API v2 compliance endpoint. 


```
compliant-client.py
Usage:
    compliant-client --all --name <name> --ids-file <ids-file> --results-file <results-file>
    compliant-client --create --name <name>
    compliant-client --list (--name <name> | --id <id>)
    compliant-client --upload (--name <name> | --id <id>) --ids-file <ids-file>
    compliant-client --download (--name <name> | --id <id>) --results-file <results-file>
    compliant-client --help
    compliant-client --version
Options:
    -a --all
    -c --create
    -l --list
    -u --upload
    -d --download
    -n --name
    -i --id
    -f --ids-file
    -r --results-file
    -h --help
    -v --version
```    

### Example calls
 
```bash
$python compliant-client.py --create --name "MyJob"
``` 
 
```bash
$python compliant-client.py --list
``` 

```bash
$python compliant-client.py --upload --name "MyJob" --ids-file "./inbox/tweet_ids.txt"
``` 

```bash
$python compliant-client.py --download --name "MyJob" --results-file "./oubox/results.txt"
``` 
 

```bash
$pythomcompliant-client.py --all --name "MyJob" --ids-file "../inbox/tweet_ids.txt" --results-file "../outbox/results.json"
``` 


## Compliance-client class

### compliant-client/compliance/compliance.py

The *compliance.py* class lives in a *../compliance folder*. The *../compliance/compliance.py* file defines a **compliance_client** class. 

```python
import compliance.compliance

compliance_client = compliance.compliance.compliance_client() #Geez, that some odd looking syntax. 

job_details = compliance_client.create_tweet_compliance_job(settings['name'])
results = compliance_client.upload_ids(settings['ids-file'], job_details['upload_url'])
results = compliance_client.download_results(job_details['download_url'], settings['results-file'])
current_jobs = compliance_client.list_jobs()
job_details = compliance_client.list_job(settings['id'])

```
  
  
  


## Core objects

### Job details

This code works with a **job_details** object. The compliance endpoint is used to manage a compliance **Job** through its lifecycle. 


```json
{
    "download_expires_at": "2020-12-30T00:05:30.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1341535366134689792/delivery/...",
    "id": "1341535366134689792",
    "name": "80M Tweet test",
    "status": "complete",
    "upload_expires_at": "2020-12-23T00:20:30.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1341535366134689792/submission/..."
}
```

The Python dictionary that encapsulates Job objects looks like:

```python

job_details = {}
job_details['name']
job_details['job_id']
job_details['upload_url']
job_details['download_url']
job_details['status']
job_details['upload_expires_at']
job_details['download_expires_at']


```