import requests

def upload_ids(ids_file_path, url):
    success = False

    headers = {}
    headers['Content-Type'] = 'text/plain'

    #Not passing in auth details, since the Upload URL is already signed...
    response = requests.put(url, data=open(ids_file_path, 'rb'), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        pass
    else:
        success = True

    return success

if __name__ == "__main__":

    #Set the path to your file with Tweet IDs.
    ids_file_path = './inbox/tweet_ids.txt'
    #Set the upload path for this Job. This URL was generated when the Job was created. 
    upload_url = ""
    #Call the method for uploading the ID file.
    success = upload_ids(ids_file_path, upload_url)

    if success:
        print(f"Uploaded IDs.")
