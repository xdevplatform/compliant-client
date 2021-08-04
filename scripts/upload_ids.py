"""
upload_ids.py

Usage:
    upload_ids --ids-file <ids_file> --url <url>

Options:
    -i --ids-file IDSFILE ID
    -u --url URL
"""

from docopt import docopt #The above comment defines the arguments this script supports.

import requests
import json

def upload_ids(ids_file_path, url):
    success = False

    headers = {}
    headers['Content-Type'] = 'text/plain'

    #Not passing in auth details, since the Upload URL is already signed...
    response = requests.put(url, data=open(ids_file_path, 'rb'), headers=headers)

    if response.status_code != 200:
        print(f"Error uploading Tweet IDs: {response.status_code} | {response.text}")
        success = False
        return success
    else:
        success = True

    return success

if __name__ == "__main__":

    arguments = docopt(__doc__, version='v1.0')

    #Call the method for uploading the ID file.
    success = upload_ids(arguments['--ids-file'], arguments['--url'])

    if success:
        print(f"Uploaded IDs.")
    else:
        print("Upload failed.")
