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

    #Set the path to your file with Tweet IDs.
    ids_file_path = './inbox/tweet_ids_1000.txt'
    #Set the upload path for this Job. This URL was generated when the Job was created. 
    upload_url = "https://storage.googleapis.com/twttr-tweet-compliance/1349131465015975937/submission/16529675_1349131465015975937?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mesos-svc-account%40twttr-compliance-public-prod.iam.gserviceaccount.com%2F20210112%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210112T230941Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=1a81e016a214cfa33050f863f556758691e598c09a9758c065e198abf0671a63673dad010724aaa3f7d6f2051d20973b635dcbc70f0ea74d566e929eb377250f20a3225fcf31c9525712a383790907607772a04656153174a3e204edc8ef72b78fd9401a90626421493ffe8819c97a1caa22d64a7f3f4009a7772ddcbc23d19f9ed3213bcbe324078983b8c7d40db8b8a62d15fe3b87e9d2c417b90ccf18417a93cbaa26e111eb3bd110d92f0c086ab398668730ac7d27761ecc8f0b0263a3b719790b3c6a67e3db7b8cb32d8e9c821f2adeaa9cdf75da23acab46fbd56b06b96c0de8e52cc1ff122a2d909ee946977a3b9ee350af892c5305404905fa0eb49d"
    #Call the method for uploading the ID file.
    success = upload_ids(ids_file_path, upload_url)

    if success:
        print(f"Uploaded IDs.")
