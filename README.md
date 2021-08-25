# The Compliant (Python) client

**tl;dr** This repository provides both simple scripts and a more elaborate *client* for working with the "batch 
Compliance" endpoints. There is a simple script for each of the 5 stages of managing a Job life-cycle, while the 
client automates a Compliance Job's life-cycle, from creating a Job to downloading the results.

## Introduction

This repository contains Python code for working with the Twitter Batch Compliance endpoints. To learn more about these 
endpoints, check out their documentation at: {link}

### Simple scripts
This repository hosts a set of simple Python scripts (in the ./scripts folder) for the Compliance endpoints. These 
scripts support a simple command line interface.  

These five scripts map to the fundamental methods that are called on the new Compliance endpoint:
1) Create a Compliance Job.
2) Once Job is created, upload a set of Twitter Tweet IDs or User IDs to check for Compliance events related to them.
3) Request the status of a Job. Determine if a Job was created, whether it is in progress or completed.
4) Request the status of all "active" Jobs. Only one Job at a time can be running, and uploading an ID file triggers the 
   start of procoessing. 
5) Once a Job has the status of 'completed', download the results that indicate which Tweets have been deleted, which User accounts have updates, or some other Compliance event such as geo-scrubbing. 

### Example client

There is also a more elaborate example 'compliant-client' script that helps manage Compliance Jobs and their lifecycles. 
For example, the 'apps/compliant-client.py' script enables you to manage Jobs by name and not just ID. More interestingly, 
this client code lets you provide all that is needed in one "all" command. The script creates a new Job, uploads
a specified User ID or Tweet ID file, checks on the Job status every 30 seconds, then downloads the results when the Job completes.  

When making an 'all' command, you need to specify the Job type, a Job name, the path to the IDs file for uploading, and the path to 
file where you want the results written. The Batch Compliance endpoints support two types of Compliance requests, one for Tweet Compliance 
events, and one for User Compliance events.

Here is an example command-line for creating a Job, uploading a Tweet ID file, monitoring a Job's progress, and writing the downloaded results to a local file:   

```bash
$python apps/compliant-client.py --all --type tweets --name "Checking Tweets" --ids-file "../inbox/tweet_ids.txt" --results-file "../outbox/tweet_results.json"
```
Here's an example client command-line for working with a User ID file:  

```bash
$python apps/compliant-client.py --all --type users --name "Checking Users" --ids-file "../inbox/user_ids.txt" --results-file "../outbox/user_results.json"
```
 
## Getting started

The first step when starting with the batch Compliance endpoint is establishing access and generating the authentication 
token needed to make requests. You will need to have an approved developer account and have access to the Twitter 
Developer Portal. You will need to have a Twitter App, and have its Bearer Token on-hand to start making requests. Bearer 
Tokens can be generated in the Developer Portal (yay!). Authentication tokens are only displayed on the Developer Portal
once (when generated), so be ready to save those tokens in a secure place. 

The simple scripts and the example client share common code that imports your Bearer Token from the local os 
environment/session (this client was developed on the MacOS. If you are on Windows you may want to update how Tokens are 
managed). See the "Setting up authentication" section below for more details.

So far, a package has not been generated for this project. To start working with the client code, the repository can be 
cloned in your environment. Currently, there is not any configuration file needed, and the only 'configuration' needed is 
setting up of a "BEARER_TOKEN" environment variable. 

### Python packages
The scripts and example app import the following Python Packages:
* requests
* json
* os
* docopt (A package that converts simple header documentation into a set of command-line parameters, options, and switches.)

... and that's it!

Other steps for preparing to use the batch Compliance endpoint include: 

   + Preparing Tweet and User ID files. IDs should be in simple text with one ID per line. When uploading 
   the files, a 'Content-Type' header should be set to 'text/plain'. See below for an example. 
   + Build methods to import and update Tweet archives. Once the Compliance results are downloaded, code is needed to update 
     your archives accordingly. This may take the form of making database deletes, deleting stored JSON files, or 
     writing new file data files. 

## Job attributes and lifecycles 
 
Compliance Jobs have a lifecycle, from being created, having Twitter IDs assigned, a period of time while the results 
are generated, to having a file to download that contains JSON that describes Compliance events associated with submitted IDs. 

When a Job is created, URLs for uploading IDs and downloading results from are provided. When Twitter IDs are uploaded, 
the process of checking each ID for Compliance events starts. This process will take many minutes (depending on the 
number of IDs submitted). After the job completes, the results can be downloaded for post-processing. The results have the 
form of JSON that describes the type of Compliance event that took place.  

Let's dig into some of the details... 

* Job are created with an optional (and recommended) name. 
  
The 'create' process creates a new job with the following 
  attributes:
 
```json
{
  "created_at": "2021-08-25T00:21:54.000Z",
  "download_expires_at": "2021-09-01T00:21:54.000Z",
  "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1430324519596564483/delivery/992443111073660928_1430324519596564483?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=complianceapi-public-svc-acct%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210825%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210825T002154Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=4066eea9ff73d297d5f51ac6f1260540bd8656b473f33e2cc0925afe9c58c8bc66c6c8a501a059ee90bc3c78144c1b32ea774660a3672f33e44c0083f2c9da3ff7fcf6efd8499e158733b81fb9ad9e3f91144d988d903404f5e3718f37719627014fe34b1b4fd7af41ca76393e0a6564cdd03b1cb1aa3d385a639940f9e52f6b5f3d9e5d023a55811bbbed6e5b54e077a2d413a392afd5088b3906ce3d40162f4ca4f62b26e363f70a57ea252594b091e6a50480753f9a528f6bd1c7890883b66b55750220e45fff8aa64067cf08c390517b597d4d80d759c124be5352446e57f9b57dcf3c070bee913cd6140897485a6eabd92157faee46f857f1939931c0f9",
  "id": "1430324519596564483",
  "name": "Checking my stored Tweets",
  "resumable": false,
  "status": "created",
  "type": "tweets",
  "upload_expires_at": "2021-08-25T00:36:54.000Z",
  "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1430324519596564483/submission/992443111073660928_1430324519596564483?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=complianceapi-public-svc-acct%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210825%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210825T002154Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=c20ecee2fea6e4ada2cb04f08b3350b039d9a608dd343b9c1ac2a003d2c26e6abac7546a5589bc3146d87b3e9e6023309c96bb9cddf96f8281e2a17fa63fdd8f711a997317c4be6dfead08d728b48381f4d95e515d01b91066aa4eb0c876bcd12195d2521ec2720c8e92d2830ae4ef17340c4fb92c58203f05bef9474d8d91404f48eff41b3b04adb662668eecd14b4ccc848d4d0e7df690a48e5befca081e0ce429a4387ba763a47bec7e88a3a57fdb2b97f7a2a04294aaafe102d9704dce62967e2a85c6c3170c689a8ba8f079afaf63ba850846aadd4ef7a99a7f67e0c05bf65a628809af79251b31051e8a785e262c28b81f2b3aa2839adaf1f5d078e9c2"
}
```
These Job details include an URL for uploading your ID. There is also an expiration time for that URL. Once a Job is 
created the upload link is available for 15 minutes. If the link expires before you upload the IDs, a new Job will need 
to be created. 
 
* Tweet and User IDs are uploaded to a cloud file system. The IDs are written to a simple text file with one ID per line. 
  Below is an example for a set of Tweet IDs, and the format is identical for User Ids. 

#### Tweet ID file 

```
900145569397649408
900145765250732032
900148142313754624
900148877004861440
900149201455263746
900149551985819648
900149689252802560
900149981465673732
900150802534342657
900152816081219584
```

* Uploaded IDs are checked for Compliance, a process that can take many minutes (and hours?) to complete. 

```json
{
  "status": "in_progress"
}

```

The Job will remain in the "in_progress" status until it finishes and enters a final "completed" status


```json
{
  "created_at": "2021-08-25T00:21:54.000Z",
  "download_expires_at": "2021-09-01T00:21:54.000Z",
  "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1430324519596564483/delivery/992443111073660928_1430324519596564483?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=complianceapi-public-svc-acct%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210825%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210825T002154Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=4066eea9ff73d297d5f51ac6f1260540bd8656b473f33e2cc0925afe9c58c8bc66c6c8a501a059ee90bc3c78144c1b32ea774660a3672f33e44c0083f2c9da3ff7fcf6efd8499e158733b81fb9ad9e3f91144d988d903404f5e3718f37719627014fe34b1b4fd7af41ca76393e0a6564cdd03b1cb1aa3d385a639940f9e52f6b5f3d9e5d023a55811bbbed6e5b54e077a2d413a392afd5088b3906ce3d40162f4ca4f62b26e363f70a57ea252594b091e6a50480753f9a528f6bd1c7890883b66b55750220e45fff8aa64067cf08c390517b597d4d80d759c124be5352446e57f9b57dcf3c070bee913cd6140897485a6eabd92157faee46f857f1939931c0f9",
  "id": "1430324519596564483",
  "name": "Checking my stored Tweets",
  "resumable": false,
  "status": "complete",
  "type": "tweets",
  "upload_expires_at": "2021-08-25T00:36:54.000Z",
  "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1430324519596564483/submission/992443111073660928_1430324519596564483?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=complianceapi-public-svc-acct%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210825%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210825T002154Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=c20ecee2fea6e4ada2cb04f08b3350b039d9a608dd343b9c1ac2a003d2c26e6abac7546a5589bc3146d87b3e9e6023309c96bb9cddf96f8281e2a17fa63fdd8f711a997317c4be6dfead08d728b48381f4d95e515d01b91066aa4eb0c876bcd12195d2521ec2720c8e92d2830ae4ef17340c4fb92c58203f05bef9474d8d91404f48eff41b3b04adb662668eecd14b4ccc848d4d0e7df690a48e5befca081e0ce429a4387ba763a47bec7e88a3a57fdb2b97f7a2a04294aaafe102d9704dce62967e2a85c6c3170c689a8ba8f079afaf63ba850846aadd4ef7a99a7f67e0c05bf65a628809af79251b31051e8a785e262c28b81f2b3aa2839adaf1f5d078e9c2"
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
  
  Here is an example for a Tweet Compliance event:
  
  ```json
  {
  "id": "906972198136631298",
  "action": "delete",
  "created_at": "2017-09-10T20:06:37.421Z",
  "redacted_at": "2020-07-21T23:37:55.607Z",
  "reason": "deleted"
  }
 ``` 

Here is an example for a User Compliance event:

  ```json
  {
  "id": "#######",
  "action": "delete",
  "created_at": "2013-03-26T02:46:15+00:00",
  "reason": "protected"
}
 ``` 

Other reasons include: "deleted" and "suspended"


## Setting up authentication

To set your enviornment variables in your terminal run the following lines to load your tokens into these environmental variables. Note that there variables are session-specific, so if you stop and restart a terminal these will need to be reloaded unless you auto-load them or persist them somehow. 

```bash
export 'BEARER_TOKEN'='<your_api_key>'
```

A quick way to test your authentication is to make a request for the current "list Jobs." 


```bash
$python ./scripts/list_jobs.py --type tweets
```

```bash
$python ./apps/compliant-client.py --list --type tweets
```


The example scripts and example client code includes this common code that loads these tokens in from the local environment: 

```python
import requests
import os

def bearer_oauth(self, r):
    # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers['Authorization'] =  "Bearer {}".format(bearer_token)

    return r

URL = 'https://api.twitter.com/2/compliance/jobs'
headers = {}
response = requests.get(f"{URL}/{id}", auth=bearer_oauth, headers=headers)

```



## Simple scripts
##### ./scripts

The /scripts folder contains a set of Python scripts for the compliance endpoints. These scripts can be used to create 
and manage Compliance Jobs and their lifecycles:

These scripts all support command-line arguments for passing in settings when creating a Job, or when listing Jobs. Here
is an example for the list_job.py script. 

```python
if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    job_details = list_job(arguments['--id'])

    if len(job_details) == 0:
        print(f"Compliance Job not found or error occurred.")
    else:
        print(f"Job details for ID {job_details['id']}:")
        print(json.dumps(job_details, indent=4, sort_keys=True))
```
There are five scripts:
  1) **create_job.py** Creating a Job: ```python create_job.py --type tweets --name "My new Compliance Job"```
  2) **list_jobs.py** Requesting a list of all existing Jobs: ```python list_jobs.py --type tweets```
  3) **list_job.py** Checking on a specific Job status and retrieving its details: ```python list_jobs.py --id <JOB_ID>```
  4) **upload_ids.py**Uploading a text file with Tweet IDs (one per line): ```python upload_ids.py --ids-file <IDS_FILE> --url <UPLOAD_URL>```
  5) **download_results.py** Downloading results which consist of one JSON object for each Tweet that has had Compliance event (e.g. has been 
  deleted): ```python download_results.py --id <JOB_ID> --url <DOWNLOAD_URL>```

## Example client
##### ./apps/compliant-client.py
+ Command-line app for working with the Twitter API v2 compliance endpoint. 

The commannd-line supports the following commands (these are displayed with the -h or --help command):

```
compliant-client.py

Usage:
    compliant-client --all --type <type> --name <name> --ids-file <ids-file> --results-file <results-file>
    compliant-client --create --type <job-type> --name <name>
    #Client will return both Tweet and User jobs if type is not specified.
    compliant-client --list [--type <type> | --name <name> | --id <id> | --status <status>]
    compliant-client --upload (--name <name> | --id <id>) --ids-file <ids-file>
    compliant-client --download (--name <name> | --id <id>) --results-file <results-file>
    compliant-client --help
    compliant-client --version

Options:
    -a --all
    -c --create
    -l --list
    -s --status STATUS
    -u --upload
    -d --download
    -t --type TYPE
    -n --name NAME
    -i --id ID
    -f --ids-file IDSFILE
    -r --results-file RESULTSFILE
    -h --help
    -v --version
```    

### Example calls

Here are some example commands, and illustrate how to manage a Job from creation to downloading results.
 
This will create a new Tweets compliance Job, and apply the name "MyTweetsJob." Assigning a name will enable you to 
manage Jobs by that name instead of its ID. That can be a nice convenience. 
```bash
$python compliant-client.py --create --type tweets --name "Checking my stored Tweets"
``` 

This will list the status of all Tweets Jobs.  
```bash
$python compliant-client.py --list --type tweets
``` 

You can also look up a Job status by name. 
```bash
$python compliant-client.py --list --name "Checking my stored Tweets"
``` 

This command will upload the Tweet IDs for the Job named "MyTweetsJob".
```bash
$python compliant-client.py --upload --type tweets --name "Checking my stored Tweets" --ids-file "./inbox/tweet_ids.txt"
``` 

When the Job is finished, this will download the results for the Job named "MyTweetsJob" to the file specified. 
```bash
$python compliant-client.py --download --type tweets --name "Checking my stored Tweets" --results-file "./oubox/results.txt"
``` 
 
**If you want to make a single 'all' call**, the script will manage the Job from creation to downloading the results: 
```bash
$python compliant-client.py --all --name "Checking my stored Tweets" --ids-file "../inbox/tweet_ids.txt" --results-file "../outbox/results.json"
``` 


## Compliance-client class

### compliant-client/compliance/compliance.py

The *compliance.py* class lives in a *../compliance folder*. The *../compliance/compliance.py* file defines a 
**compliance_client** class. 

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

This code works with a **job_details** object. The compliance endpoint is used to manage a compliance **Job** through its 
lifecycle. 


```json
{
    "download_expires_at": "2020-12-30T00:05:30.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1341535366134689792/delivery/...",
    "id": "1341535366134689792",
    "name": "80M Tweet test",
    "status": "complete",
    "type": "tweets",
    "upload_expires_at": "2020-12-23T00:20:30.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1341535366134689792/submission/..."
}
```

The Python dictionary that encapsulates Job objects looks like:

```python

job_details = {}
job_details['name']
job_details['type']
job_details['id']
job_details['upload_url']
job_details['download_url']
job_details['status']
job_details['upload_expires_at']
job_details['download_expires_at']


```

