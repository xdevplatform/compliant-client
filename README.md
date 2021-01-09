# The Compliant (python) client

tl;dr This repository provides both simple example scripts and a more elaborate example *client* for the "batch Compliance" endpoint.

## Introduction
This repository (in the ./scripts folder) hosts a set of simple Python scripts for the Compliance endpoints. These five scripts map to the fundamental methods that are called on the new Compliance endpoint:
1) Create a Compliance Job.
2) Once Job is created, upload a set of Twitter Tweet IDs (and User) to check for Compliance events related to them.
3) Request the status of a Job. Determine if a Job was created, whether it is in progress or completed.
4) Request the status of all "active" Jobs. Only one Job at a time can be running, and uploading an ID file triggers the start of procoessing. 
5) Once a Job has the status of 'completed', download the results that indicate which Tweets have been deleted, or some other Compliance event such as geo-scrubbing. 

There is also a 
more elaborate example 'compliant-client' script that helps manage Compliance Jobs and their lifecycles. 

The 'compliant-client.py' script lets you provide all that is needed in one "all" command. The script creates a new Job, uploads
the specified Tweet ID file, checks on the Job status every 30 seconds, then downloads the results when the Job completes.  

Here is an example command-line:   

```bash
$python compliant-client.py --all --name "MyJob" --ids-file "../inbox/tweet_ids.txt" --results-file "../outbox/results.json"
```
 
## Getting started

   + Setting up access to Compliance endpoint.   
   + Authentication: these scripts and example client share common code for authenticating with the endpoint. The Compliance endpoint relies on OAuth 1.0a authentication. Twitter consumer and user tokens are imported from the local environment.  
   + Preparing Tweet (and User) ID files. IDs should be in simple text with one ID per line. When uploading 
   the files, a 'Content-Type' header should be set to 'text/plain'. 
   + Build methods to import and update Tweet archives. Once the Compliance results are downloaded, code is needed to update your archives accordingly. This may take the form of making database deletes or writing new file data files. 
 
## Job attributes and lifecycles 
 
Compliance Jobs have a lifecycle, from being created, having Twitter IDs assigned, a period of time while the results are generated, to generating a file containing JSON that describes Compliance events associated with submitted IDs. When a Job is created, locations for uploading IDs and downloading results are provided. When Twitter IDs are uploaded, the process of checking each ID for Compliance events starts. This process will take many minutes (depending on the number of IDs submitted). After the job completes, the results can be download for post-processing. The results have the form of JSON that descibes the type of Compliance event that took place.  

Let's dig into some of the details... 

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
These Job details include an URL for uploading your ID. There is also an expiration time for that URL. Once a Job is created the upload link is available for 15 minutes. If the link expires before you upload the IDs, a new Job will need to be created. 
 
* Tweet IDs are uploaded to a cloud file system. Tweet IDs are written to a simple text file with one ID per line. 

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

* Uploaded Tweets are checked for Compliance, a process that can take many minutes (and hours?) to complete. 

```json
{
  "status": "in_progress"
}

```

The Job will remain in the "in_progress" status until it finishes and enters a final "completed" status


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

To set your enviornment variables in your terminal run the following lines to load your tokens into these environmental variables. Note that there variables are session-specific, so if you stop and restart a terminal these will need to be reloaded unless you auto-load them or persist them somehow. 

```bash
export 'API_KEY'='<your_api_key>'
export 'API_SECRET'='<your_api_secret>'
export 'API_TOKEN'='<your_api_token>'
export 'API_TOKEN_SECRET'='<your_api_token_secret>'
```
The example scripts and example client code includes this common code that loads these tokens in from the local environment: 

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

The commannd-line supports the following commands (these are displayed with the -h or --help command):

```
compliant-client.py
Usage:
    compliant-client --all --name <name> --ids-file <ids-file> --results-file <results-file>
    compliant-client --create --name <name>
    compliant-client --list [--name <name> | --id <id> | --status <status>]
    compliant-client --upload (--name <name> | --id <id>) --ids-file <ids-file>
    compliant-client --download (--name <name> | --id <id>) --results-file <results-file>
    compliant-client --help
    compliant-client --version
Options:
    -a --all
    -c --create
    -l --list
    -s --status
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

Here are some example command, and illustrate how to manage a Job from creation to downloading results.
 
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

## Example workflow

Create a new job with name "Storm event data". This command:

```
/compilant-client/apps/compliant-client.py --create --name "Harvey event data"
```

Outputs:
```
New compliance Job created with ID 1347687194924773377
{
    "download_expires_at": "2021-01-15T23:30:40.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/delivery/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=9fc04d94029432e72b021c71e4f0a66b9897f53ce54b5254421006aaf317c3c154947b819c30df56fe3143cc8b65d19b87a232f22307906a348b58947c6fa3036f7b9f515475a7d63f15db3941c180c3f9f2a7d44e900b929a1343d0633d1c7804893705c9b5e3e55730231b906be2ffed525f54ad3aa66e7e2a655c47d39cc559a36c0bfa6955dfa43f3e946b4ca1e180cca2c0f576756c1a0edfcbead586756841ebcb098691900fd97e932df5109d9f4e8c596eaeefcf784faedf6cd6bbdb42ff3e3aee905d00c36ce588f016cd4e568411e452f29aebc604dc9f51e6335abfca5e0fd545fa47c1f8b1514118e0c2a636e1743ca1dfd8d79218112a9eef2e",
    "id": "1347687194924773377",
    "job_id": "1347687194924773377",
    "name": "Harvey event data",
    "upload_expires_at": "2021-01-08T23:45:40.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/submission/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=1474ab38331b6e600a667e8fa5c9a112bf3e4aa267f34cabb958b87dd3a1b888c711bc1173475a3e0ab1a1980dab9efee7b30d327d9273da1ff6708cf789b590dc7b304d53be0b684ccd926ba2ee04eea86931b974ec790942cf7466231a5170fcdb175e6ee9dac7bbdc01c86ed1e48811fa90b7c22c799a080a3b345e0cdb7b78727aebc6060e396f4761ba364f2162929cfad02b625feda9d4d3488789229f7790ad11c90a02ec19ae0f923f2c652df29d67e65ab6786b22f72ac56cc6a51ed5ee16adc890c8cba2e719f304d9941d6ce91c17103ed609e35c0499268a8ca12478f2f114e4b26cc00980373d339bb8a8cb39bdeb16af6fa948eb19e02383d1"
}

```

Now, let's list that job and see its status. This command:

```
/compilant-client/apps/compliant-client.py  --list --id 1347687194924773377
```

Outputs:
```
Making request for Job ID: '1347687194924773377'.
Job details: 
 {
    "download_expires_at": "2021-01-15T23:30:40.000Z",
    "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/delivery/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=9fc04d94029432e72b021c71e4f0a66b9897f53ce54b5254421006aaf317c3c154947b819c30df56fe3143cc8b65d19b87a232f22307906a348b58947c6fa3036f7b9f515475a7d63f15db3941c180c3f9f2a7d44e900b929a1343d0633d1c7804893705c9b5e3e55730231b906be2ffed525f54ad3aa66e7e2a655c47d39cc559a36c0bfa6955dfa43f3e946b4ca1e180cca2c0f576756c1a0edfcbead586756841ebcb098691900fd97e932df5109d9f4e8c596eaeefcf784faedf6cd6bbdb42ff3e3aee905d00c36ce588f016cd4e568411e452f29aebc604dc9f51e6335abfca5e0fd545fa47c1f8b1514118e0c2a636e1743ca1dfd8d79218112a9eef2e",
    "id": "1347687194924773377",
    "job_id": "1347687194924773377",
    "name": "Harvey event data",
    "status": "created",
    "upload_expires_at": "2021-01-08T23:45:40.000Z",
    "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/submission/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=1474ab38331b6e600a667e8fa5c9a112bf3e4aa267f34cabb958b87dd3a1b888c711bc1173475a3e0ab1a1980dab9efee7b30d327d9273da1ff6708cf789b590dc7b304d53be0b684ccd926ba2ee04eea86931b974ec790942cf7466231a5170fcdb175e6ee9dac7bbdc01c86ed1e48811fa90b7c22c799a080a3b345e0cdb7b78727aebc6060e396f4761ba364f2162929cfad02b625feda9d4d3488789229f7790ad11c90a02ec19ae0f923f2c652df29d67e65ab6786b22f72ac56cc6a51ed5ee16adc890c8cba2e719f304d9941d6ce91c17103ed609e35c0499268a8ca12478f2f114e4b26cc00980373d339bb8a8cb39bdeb16af6fa948eb19e02383d1"
}
```

We can also look up the Job by name. This command:
```
/compilant-client/apps/compliant-client.py  --list --name "Harvey event data" 
```

Outputs:
```
Making request for Jobs list to look up Job with name 'Harvey event data'.
[
    {
        "download_expires_at": "2021-01-15T23:30:40.000Z",
        "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/delivery/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=9fc04d94029432e72b021c71e4f0a66b9897f53ce54b5254421006aaf317c3c154947b819c30df56fe3143cc8b65d19b87a232f22307906a348b58947c6fa3036f7b9f515475a7d63f15db3941c180c3f9f2a7d44e900b929a1343d0633d1c7804893705c9b5e3e55730231b906be2ffed525f54ad3aa66e7e2a655c47d39cc559a36c0bfa6955dfa43f3e946b4ca1e180cca2c0f576756c1a0edfcbead586756841ebcb098691900fd97e932df5109d9f4e8c596eaeefcf784faedf6cd6bbdb42ff3e3aee905d00c36ce588f016cd4e568411e452f29aebc604dc9f51e6335abfca5e0fd545fa47c1f8b1514118e0c2a636e1743ca1dfd8d79218112a9eef2e",
        "id": "1347687194924773377",
        "name": "Harvey event data",
        "status": "created",
        "upload_expires_at": "2021-01-08T23:45:40.000Z",
        "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347687194924773377/submission/16529675_1347687194924773377?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T233040Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=1474ab38331b6e600a667e8fa5c9a112bf3e4aa267f34cabb958b87dd3a1b888c711bc1173475a3e0ab1a1980dab9efee7b30d327d9273da1ff6708cf789b590dc7b304d53be0b684ccd926ba2ee04eea86931b974ec790942cf7466231a5170fcdb175e6ee9dac7bbdc01c86ed1e48811fa90b7c22c799a080a3b345e0cdb7b78727aebc6060e396f4761ba364f2162929cfad02b625feda9d4d3488789229f7790ad11c90a02ec19ae0f923f2c652df29d67e65ab6786b22f72ac56cc6a51ed5ee16adc890c8cba2e719f304d9941d6ce91c17103ed609e35c0499268a8ca12478f2f114e4b26cc00980373d339bb8a8cb39bdeb16af6fa948eb19e02383d1"
    }
]
```

Now let's upload a Tweet ID file. 


```
--upload --name "Harvey event data" --ids-file "./inbox/tweet_ids_228000.txt"
```

```
Making 'list Jobs' request...
Successfully uploaded the ./inbox/tweet_ids_228000.txt Tweet ID file.
```

Recheck the status:

```
--list --name "Storm event data"
```

```
Making request for Jobs list to look up Job with name 'Storm event data'.
[
    {
        "download_expires_at": "2021-01-15T23:51:53.000Z",
        "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347692535167111169/delivery/16529675_1347692535167111169?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T235153Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=b8e2f3afd2ec30145bf32eb8ee468183133e6d41953f00321d980bdf97be91db01ffdea105b675d7419056e49760de490ea4ed9aeff6758d5bee00d9aba4af2afdc42811a93677573ce52f5f509deed0d4292cbb6d69c75dc09c90cfd81030f05dfffb02777f0df17aeeff69be9f241d77d9d02251e4edcd9960a88837338b79ba0d813256fa4cc0d0b6d59a613e2ccef4485bb4d255b8670fdf6f8be015aca55f71644e87e072e1a79581709e023b8a01d4f32b218f0e5941f1dca8ac4e0eeea9fb856d04ce37f21d7cade7e57fef6cb40af812d87866e9d89f427f8ae96d063d8ab17d74786764f1abcfd15785261270e795b1daa62355ef56093665e6d3c6",
        "id": "1347692535167111169",
        "name": "Storm event data",
        "status": "in_progress",
        "upload_expires_at": "2021-01-09T00:06:53.000Z",
        "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347692535167111169/submission/16529675_1347692535167111169?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T235153Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=3437a246f8b2ab28f586da6867a90cb8bf8fff5f80318d2a9828e7ca07adfd983712ae2ca83c3cd6abb698da490b1aadb1a67b2626915e2f28987adafd415a99664debaed4ec6fb1e741d2ffaea13e3e761e379d412715333aa9c271073bbfd711530a0c9ebdd4f63a7a1085d98a2388a9b7f305e54acb593ec7648001e84e149d1d0b4f51c2094d6d9ffe722b2024ad521c0a24672cf23d3ecb52033e2aa8162d9670483817f9ae058a8af69791bbae8a15ab54a46ebac63c6a0e57d2416e7864e8cae943291a92c95f160aaf2004580a1a8429378a222c7c77b4f018d0c637d171f88e667d33e92e55d8934c91b96cb4a103dc34bd7223f649f2e555b87b5c"
    }
]

```

After a few minutes we recheck, and see that the Job has completed.

```
Making request for Jobs list to look up Job with name 'Storm event data'.
[
    {
        "download_expires_at": "2021-01-15T23:51:53.000Z",
        "download_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347692535167111169/delivery/16529675_1347692535167111169?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T235153Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=b8e2f3afd2ec30145bf32eb8ee468183133e6d41953f00321d980bdf97be91db01ffdea105b675d7419056e49760de490ea4ed9aeff6758d5bee00d9aba4af2afdc42811a93677573ce52f5f509deed0d4292cbb6d69c75dc09c90cfd81030f05dfffb02777f0df17aeeff69be9f241d77d9d02251e4edcd9960a88837338b79ba0d813256fa4cc0d0b6d59a613e2ccef4485bb4d255b8670fdf6f8be015aca55f71644e87e072e1a79581709e023b8a01d4f32b218f0e5941f1dca8ac4e0eeea9fb856d04ce37f21d7cade7e57fef6cb40af812d87866e9d89f427f8ae96d063d8ab17d74786764f1abcfd15785261270e795b1daa62355ef56093665e6d3c6",
        "id": "1347692535167111169",
        "name": "Storm event data",
        "status": "complete",
        "upload_expires_at": "2021-01-09T00:06:53.000Z",
        "upload_url": "https://storage.googleapis.com/twttr-tweet-compliance/1347692535167111169/submission/16529675_1347692535167111169?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210108%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210108T235153Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=3437a246f8b2ab28f586da6867a90cb8bf8fff5f80318d2a9828e7ca07adfd983712ae2ca83c3cd6abb698da490b1aadb1a67b2626915e2f28987adafd415a99664debaed4ec6fb1e741d2ffaea13e3e761e379d412715333aa9c271073bbfd711530a0c9ebdd4f63a7a1085d98a2388a9b7f305e54acb593ec7648001e84e149d1d0b4f51c2094d6d9ffe722b2024ad521c0a24672cf23d3ecb52033e2aa8162d9670483817f9ae058a8af69791bbae8a15ab54a46ebac63c6a0e57d2416e7864e8cae943291a92c95f160aaf2004580a1a8429378a222c7c77b4f018d0c637d171f88e667d33e92e55d8934c91b96cb4a103dc34bd7223f649f2e555b87b5c"
    }
]
``
