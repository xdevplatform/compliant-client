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

# https://docs.google.com/document/d/1l7cd_jeoHwoAa3XqNI4c6anXu6AibFqRhVU9y-rT748/edit?usp=sharing
# https://developer.twitter.com/en/docs/twitter-api/tweets/compliance/introduction
# https://developer.twitter.com/en/docs/twitter-api/tweets/compliance/api-reference

from docopt import docopt #Seriously, this package is soooo nice. http://docopt.org/
import time
import compliance.compliance

SLEEP_INTERVAL = 60

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
        if arguments['name'] == True:
            settings['name'] = arguments['<name>'] #TODO: this is not supported until after the "list all" method is available.
        else:
            settings['id'] = arguments['<id>']

    if arguments['--upload'] == True:
        settings['mode'] = 'upload'
        settings['id'] = arguments['<id>'] #TODO: add support for <name> when ready?
        settings['ids-file'] = arguments['<ids-file>']

    if arguments['--download'] != False:
        settings['mode'] = 'download'
        settings['id'] = arguments['<id>'] #TODO: add support for <name> when ready?
        settings['results-file'] = arguments['<results-file>']

    return settings

if __name__ == "__main__":
    compliance_client = compliance.compliance.compliance_client()

    job_details = {}

    arguments = docopt(__doc__, version='v0.1')
    settings = handle_input(arguments)

    if settings['mode'] == 'all':
        #Create Tweet Compliance Job.
        job_details = compliance_client.create_tweet_compliance_job(settings['name'])

        #Upload ids.
        results = compliance_client.upload_ids(settings['ids-file'], job_details['upload_url'])

        #Monitor Job status until complete.
        start = time.time()
        while True:
            job_details = compliance_client.list_job(job_details['job_id'])
            if job_details['status'] == 'complete':
                break
            time.sleep(SLEEP_INTERVAL)
            print(f"Checking status of '{job_details['name']}' with Job ID {job_details['job_id']}.")

        duration = time.time() - start

        #Download results.
        results = compliance_client.download_results(job_details['download_url'], settings['results-file'])

        print(f"Job completed and results written to {settings['results-file']}. Completed in {duration} seconds.")

    if settings['mode'] == 'create':
        #Create Tweet Compliance Job.
        job_details = compliance_client.create_tweet_compliance_job(settings['name'])
        print(f"New compliance Job created with ID {job_details['id']}")
        print(job_details)

    if settings['mode'] == 'list':

        if settings['name'] == None and settings['id'] == None:
            print(f"Listing all jobs is not available yet.")

        if settings['name'] != None:
            print("The ability to look up a Job by name is not available yet.")

            pass
        if settings['id'] != None:
            job_details = compliance_client.list_job(settings['id'])
            pass
        print(f"Job details: {job_details}")

    if settings['mode'] == 'upload':
        job_details = compliance_client.list_job(settings['id'])
        results = compliance_client.upload_ids(job_details['upload_url'], settings['ids-files'])

    if settings['mode'] == 'download':
        job_details = compliance_client.list_job(settings['id'])
        results = compliance_client.download_results(settings['results-file'], job_details['download_url'])


