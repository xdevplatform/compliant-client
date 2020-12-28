"""
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
"""

from docopt import docopt #Seriously, this package is soooo nice. http://docopt.org/
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
        settings['name'] = arguments['<name>']
        settings['ids-file'] = arguments['<ids-file>']
        settings['results-file'] = arguments['<results-file>']
        #Upload and download URLs are not specified, but rather are determined when Job is created.

    if arguments['--create'] ==  True:
        settings['mode'] = 'create'
        settings['name'] = arguments['<name>']

    if arguments['--list'] == True:
        settings['mode'] = 'list'
        if arguments['--name'] == True:
            settings['name'] = arguments['<name>']

        if arguments['--id'] == True:
            settings['id'] = arguments['<id>']

        if arguments['--status'] == True:
            settings['status'] = arguments['<status>']

    if arguments['--upload'] == True:
        settings['mode'] = 'upload'
        settings['id'] = arguments['<id>']
        settings['ids-file'] = arguments['<ids-file>']

    if arguments['--download'] != False:
        settings['mode'] = 'download'
        settings['id'] = arguments['<id>']
        settings['results-file'] = arguments['<results-file>']

    return settings


def is_job_name_unique(name):
    job_list = list_jobs()
    for job in job_list:
        if job['name'] == name:
            return False
    return True

def create_job(name):
    job_details = {}

    if is_job_name_unique(name):
        job_details = compliance_client.create_tweet_compliance_job(name)
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

def list_jobs():
    jobs_list = compliance_client.list_jobs()
    return jobs_list

def list_job(id):
    job_details = compliance_client.list_job(id)
    return job_details

def do_all(name, ids_file, results_file):
    #This is a chatty method, and may benefit from a verbose/quiet setting.

    begin_dt = datetime.now() #Timing how long the process takes.

    job_details = create_job(name) #Create Tweet Compliance Job.

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
            if job_details['status'] == 'complete':
                break
            time.sleep(SLEEP_INTERVAL)
            print(f"Checking status of '{job_details['name']}' with Job ID {job_details['job_id']}.")

        duration = '%.1f' % ((time.time() - start)/60)
        print(f"Compliance Job took {duration} minutes to complete.")

        #Download results.
        start = time.time()
        success = download_results(job_details['download_url'], results_file)
        duration = '%.1f' % ((time.time() - start)/60)
        if success:
            print(f"Job completed and results written to {results_file}. Download took {duration} minutes.")

if __name__ == "__main__":
    #This script has this global reference to exercise the compliance_client class.
    #compliance_client = compliance.compliance.compliance_client()

    job_details = {}

    arguments = docopt(__doc__, version='v0.1')
    settings = handle_input(arguments)

    if settings['mode'] == 'all':

        #TODO: refactor 'do all' out of here
        do_all(settings['name'], settings['ids-file'], settings['results-file'])

        # # #Create Tweet Compliance Job.
        #
        # begin_dt = datetime.now()
        #
        # job_details = compliance_client.create_tweet_compliance_job(settings['name'])
        #
        # if len(job_details) == 0:
        #     print(f"Compliance Job could not be created.")
        # else:
        #     print(f"New Compliance Job created.")
        #     #Upload ids.
        #     results = compliance_client.upload_ids(settings['ids-file'], job_details['upload_url'])
        #
        #     #Monitor Job status until complete.
        #     start = time.time()
        #     while True:
        #         job_details = compliance_client.list_job(job_details['job_id'])
        #         if job_details['status'] == 'complete':
        #             break
        #         time.sleep(SLEEP_INTERVAL)
        #         print(f"Checking status of '{job_details['name']}' with Job ID {job_details['job_id']}.")
        #
        #     print(f"Compliance Job took {(time.time() - start)/60} minutes to complete.")
        #
        #     #Download results.
        #     success = compliance_client.download_results(job_details['download_url'], settings['results-file'])
        #     if success:
        #         print(f"Job completed and results written to {settings['results-file']}.")

    if settings['mode'] == 'create':
        #Create Tweet Compliance Job.
        job_details = create_job(settings['name'])

        if len(job_details) == 0:
            print(f"Compliance Job could not be created.")
        else:
            print(f"New compliance Job created with ID {job_details['id']}")
            print(json.dumps(job_details, indent=4, sort_keys=True))

    if settings['mode'] == 'list':

        if not 'name' in settings.keys() and not 'id' in settings.keys() and not 'status' in settings.keys():
            print(f"Making request for Jobs list.")
            jobs_list = list_jobs()
            print(f"Current Compliance Jobs: \n {json.dumps(jobs_list, indent=4, sort_keys=True)}")

        if 'name' in settings.keys():
            jobs = [] #TODO: currently duplicate names are possible, so we may have a list of Jobs.
            print(f"Making request for Jobs list to look up Job with name '{settings['name']}'.")
            jobs_list = list_jobs()
            for job in jobs_list:
                if 'name' in job.keys():
                    if job['name'] == settings['name']:
                        jobs.append(job)
            print(json.dumps(jobs, indent=4, sort_keys=True))

        if 'id' in settings.keys():
            print(f"Making request for Job ID: '{settings['id']}'.")
            job_details = list_job(settings['id'])
            print(f"Job details: {job_details}")

        #TODO: currently duplicate names are possible, so we may have a list of Jobs.
        if 'status' in settings.keys():

            print(f"Making request for Jobs list to match on Job status: '{settings['status']}'.")
            jobs = []
            jobs_list = list_jobs()

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
            elif settings['status'] == 'available':
                pass

            elif settings['status'] == 'running':
                pass
            else:
                print(f"Status '{settings['status']}' not known and not supported. Try 'complete', 'running', 'expired', or 'available'.")


            print(json.dumps(jobs, indent=4, sort_keys=True))

    if settings['mode'] == 'upload':

        #Uploading by Job name or ID.
        if 'name' in settings:
            job_list = list_jobs()
            for job in job_list:
                if 'name' in job.keys():
                    job_details = list_job(job['id'])
        elif 'id' in settings:
            job_details = list_job(settings['id'])

        success = upload_ids(settings['ids-files'], job_details['upload_url'])

        if success:
            print(f"Successfully uploaded the {settings['ids-files']} Tweet ID file.")
        else:
            print("Error uploading Tweet IDs file.")

    if settings['mode'] == 'download':
        success = download_results(settings['id'], settings['results-file'])
        if success:
            print(f"Results file successfully written to {settings['results-file']}")
        else:
            print("Error downloading results.")
