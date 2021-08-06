"""
compliant-client.py

Usage:
    compliant-client --all --type <type> --name <name> --ids-file <ids-file> --results-file <results-file>
    compliant-client --create --type <job-type> --name <name>
    #Not sure how to plug in job-type into this 'super' method that does both id and all lists...
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
"""

from docopt import docopt
import time
from datetime import datetime
import json
import compliance.compliance

#Create a reference to the compliance_client class.
compliance_client = compliance.compliance.compliance_client()

#When running in 'all' mode, this script repeatedly check the Job status, and waits this inteval between calls.
SLEEP_INTERVAL = 30 #TODO: This would be a fine configuration item.

def handle_input(arguments):
    """
        Validates command-line arguments, and returns setting dictionary.
        Manages defaults: config file if present, otherwise internal value, unless overridden from command-line.

        :param args:
        :return: settings dictionary

        """
    settings = {}

    if arguments['--all'] == True:
        settings['mode'] = 'all'
        settings['job-type'] = arguments['--job-type']
        settings['name'] = arguments['--name']
        settings['ids-file'] = arguments['--ids-file']
        settings['results-file'] = arguments['--results-file']
        #Upload and download URLs are not specified, but rather are determined when Job is created.

    if arguments['--create'] ==  True:
        settings['mode'] = 'create'
        settings['job-type'] = arguments['--job-type']
        settings['name'] = arguments['--name']

    if arguments['--list'] == True:
        settings['mode'] = 'list'
        if arguments['--name'] != None:
            settings['name'] = arguments['--name']

        if arguments['--id'] != None:
            settings['id'] = arguments['--id']

        if arguments['--job-type'] != None:
            settings['job-type'] = arguments['--job-type']

        if arguments['--status'] != None:
            settings['status'] = arguments['--status']

        #TODO: Do some checking and see if we have what we need...

    if arguments['--upload'] == True:
        settings['mode'] = 'upload'

        settings['ids-file'] = arguments['--ids-file']

        if arguments['--id'] != None:
            settings['id'] = arguments['--id']
        elif arguments['--name'] != None:
            settings['name'] = arguments['--name']

    if arguments['--download'] == True:
        settings['mode'] = 'download'
        settings['results-file'] = arguments['--results-file']

        if arguments['--id'] != None:
            settings['id'] = arguments['--id']
        elif arguments['--name'] != None:
            settings['name'] = arguments['--name']

    return settings

def is_job_name_unique(type, name):
    #TODO: check both types and comapre with combined list?
    job_list = list_jobs(type)
    for job in job_list:
        if job['name'] == name:
            return False
    return True

def create_job(type, name):
    job_details = {}

    if is_job_name_unique(type, name):
        job_details = compliance_client.create_tweet_compliance_job(type, name)
    else:
        print(f"This client script requires that Job names be unique. A Job with name '{name}' already exists.")

    return job_details

#ids_file --> upload_url
def upload_ids(ids_file, upload_url):
    success = compliance_client.upload_ids(ids_file, upload_url)
    return success

#download_url --> results_file
def download_results(download_url, results_file):
    success = compliance_client.download_results(download_url, results_file)
    return success

def list_jobs(type):
    jobs_list = compliance_client.list_jobs(type)
    return jobs_list

def list_job(id):
    job_details = compliance_client.list_job(id)
    return job_details

def do_all(type, name, ids_file, results_file):
    #This is a chatty method, and may benefit from a verbose/quiet setting.

    begin_dt = datetime.now() #Timing how long the process takes.

    job_details = create_job(type, name) #Create Tweet Compliance Job.

    if len(job_details) == 0: #No Job details returned? Something went wrong.
        print(f"Compliance Job could not be created.")
    else:
        print(f"New Compliance Job named '{name}' created.")

        start = time.time()
        success =  upload_ids(ids_file, job_details['upload_url'])
        duration = '%.1f' % ((time.time() - start)/60)
        print(f"Upload Job took {duration} minutes to complete.")

        #TODO: handle not successful

        #Monitor Job status until complete.
        start = time.time()
        while True:
            job_details = list_job(job_details['id'])
            #TODO: remove
            print(job_details['status'])
            if job_details['status'] == 'complete':
                break
            time.sleep(SLEEP_INTERVAL)
            print(f"Checking status of '{job_details['name']}' with Job ID {job_details['id']}.")

        duration = '%.1f' % ((time.time() - start)/60)
        print(f"Compliance Job took {duration} minutes to complete.")

        #Download results.
        start = time.time()
        success = download_results(job_details['download_url'], results_file)
        duration = '%.1f' % ((time.time() - start)/60)
        if success:
            print(f"Job completed and results written to {results_file}. Download took {duration} minutes.")

def list_by_status(settings):

    print(f"Making request for Jobs list to match on Job that are: '{settings['status']}'.")
    jobs = []

    if not 'type' in settings.keys():

        #Get Tweet jobs
        jobs_list = list_jobs('tweets')

        #Get User jobs
        jobs_list = jobs_list + list_jobs('users')

    else:
        jobs_list = list_jobs(settings['type'])

    if settings['status'] == 'complete':
        for job in jobs_list:
            if job['status'] == 'complete':
                jobs.append(job)
    elif settings['status'] == 'expired':
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        now_time = datetime.strptime(datetime.now().strftime(date_format), date_format)

        for job in jobs_list:
            #Convert Job download expiration ISO ISO 8601/RFC 3339 string to date object and compare.
            expiration_time = datetime.strptime(job['download_expires_at'], date_format)

            if expiration_time < now_time:
                jobs.append(job)

    elif settings['status'] == 'created':
        for job in jobs_list:
            if job['status'] == 'created':
                jobs.append(job)
    elif settings['status'] == 'available':
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        now_time = datetime.strptime(datetime.now().strftime(date_format), date_format)

        for job in jobs_list:
            #Convert Job download expiration ISO ISO 8601/RFC 3339 string to date object and compare.
            expiration_time = datetime.strptime(job['download_expires_at'], date_format)

            if expiration_time > now_time:
                jobs.append(job)
    elif settings['status'] == 'running':
        for job in jobs_list:
            if job['status'] == 'in_progress':
                jobs.append(job)
    else:
        print(f"Status '{settings['status']}' not known and not supported. Try 'complete', 'running', 'expired', or 'available'.")

    return jobs

if __name__ == "__main__":
    #This script has this global reference to exercise the compliance_client class.
    #compliance_client = compliance.compliance.compliance_client()

    job_details = {}

    arguments = docopt(__doc__, version='v1.0')
    settings = handle_input(arguments)

    if settings['mode'] == 'all':

        do_all(settings['type'], settings['name'], settings['ids-file'], settings['results-file'])

    if settings['mode'] == 'create':
        #Create Tweet Compliance Job.
        job_details = create_job(settings['type'], settings['name'])

        if len(job_details) == 0:
            print(f"Compliance Job could not be created.")
        else:
            print(f"New compliance Job created with ID {job_details['id']}")
            print(json.dumps(job_details, indent=4, sort_keys=True))

    if settings['mode'] == 'list':

        if not 'job-type' in settings.keys() and not 'name' in settings.keys() and not 'id' in settings.keys() and not 'status' in settings.keys():
            print(f"Making request for list of Tweets Jobs")
            jobs_list = list_jobs('tweets')
            print(f"Current Tweet Compliance Jobs: \n {json.dumps(jobs_list, indent=4, sort_keys=True)}")
            print(f"Making request for list of User Jobs")
            jobs_list = list_jobs('users')
            print(f"Current User Compliance Jobs: \n {json.dumps(jobs_list, indent=4, sort_keys=True)}")

        if 'job-type' in settings.keys() and not 'status' in settings.keys():
            print(f"Making request for list of Jobs of type {settings['type']}")
            jobs_list = list_jobs(settings['type'])
            print(f"Current User Compliance Jobs: \n {json.dumps(jobs_list, indent=4, sort_keys=True)}")

        if 'name' in settings.keys() and not 'status' in settings.keys():
            jobs = [] #Currently duplicate names are possible, so we may have a list of Jobs.
            print(f"Making request for Jobs list to look up Job with name '{settings['name']}'.")
            jobs_list = list_jobs('tweets')
            for job in jobs_list:
                if 'name' in job.keys():
                    if job['name'] == settings['name']:
                        jobs.append(job)

            jobs_list = list_jobs('users')
            for job in jobs_list:
                if 'name' in job.keys():
                    if job['name'] == settings['name']:
                        jobs.append(job)

            print(json.dumps(jobs, indent=4, sort_keys=True))

        if 'id' in settings.keys() and not 'status' in settings.keys():
            print(f"Making request for Job ID: '{settings['id']}'.")
            job_details = list_job(settings['id'])
            print(f"Job details: \n {json.dumps(job_details, indent=4, sort_keys=True)}")

        #Currently duplicate names are possible, so we may have a list of Jobs.
        #This client was recently updated to prevent duplicate names.
        if 'status' in settings.keys():
            jobs = list_by_status(settings)
            print(json.dumps(jobs, indent=4, sort_keys=True))

    if settings['mode'] == 'upload':

        print("Making 'list Jobs' request...")

        #Uploading Job by name or ID.
        if 'name' in settings:
            job_list = list_jobs()
            for job in job_list:
                if 'name' in job.keys():
                    job_details = list_job(job['id'])
        elif 'id' in settings:
            job_details = list_job(settings['id'])

        success = upload_ids(settings['ids-file'], job_details['upload_url'])

        if success:
            print(f"Successfully uploaded the {settings['ids-file']} Tweet ID file.")
        else:
            print("Error uploading Tweet IDs file.")

    if settings['mode'] == 'download':

        print("Making 'list Jobs' request...")

        #Downloading Job by name or ID.
        if 'name' in settings:
            job_list = list_jobs()
            for job in job_list:
                if 'name' in job.keys():
                    job_details = list_job(job['id'])
        elif 'id' in settings:
            job_details = list_job(settings['id'])

        success = download_results(job_details['download_url'], settings['results-file'])

        if success:
            print(f"Results file successfully written to {settings['results-file']}")
        else:
            print("Error downloading results.")
