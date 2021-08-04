"""
download_results.py

Usage:
    download_results --id <id> --url <url>

Options:
    -i --id ID
    -u --url URL
"""

from docopt import docopt #The above comment defines the arguments this script supports.
import requests

def download_results(url, results_file_path):

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error uploading Tweet IDs: {response.status_code} | {response.text}")
        return False

    with open(results_file_path, 'w') as f:
        f.write(response.text)

    return True #Success!

if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    #Set the path to where you want your files with Tweet IDs.
    results_file_path = f"../outbox/results_{arguments['--id']}.json"

    #Call the method for uploading the ID file.
    success = download_results(arguments['--url'], results_file_path)

    if success:
        print(f"Downloaded results to file {results_file_path}.")
    else:
        print(f"Download failed.")
