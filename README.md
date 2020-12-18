# The Compliant (python) client

A set of example Python scripts for the compliance endpoints. Scripts for:
  1) Creating a Job.
  2) Checking on Job status and retrieving Job details.
  3) Uploading a text file with Tweet IDs (one per line).
  4) Downloading results which consist of one JSON object for each Tweet that has had Compliance event (e.g. has been deleted).
  
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
 
 ### Example compliance client
 #### Command-line app for working with the Twitter API v2 compliance endpoint. 
 
Also, the start of a simple command-line app that references a *compliance* class.

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
### Some usage notes

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

### Core objects

This code works with a **job_details** object. The compliance endpoint is used to manage a compliance **Job** through its lifecycle. 

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
