import requests

def download_results(url, results_file_path):

    success = False

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        return False

    with open(results_file_path, 'w') as f:
        f.write(response.text)

    success = True    

    return success

if __name__ == "__main__":

    #Set the Job ID, which will be used in output file name. E.g., the numeric Job ID assigned when Job was created.
    job_id = '123456'

    #Set the path to where you want your files with Tweet IDs.
    results_file_path = f"../outbox/results_{job_id}.json"

    #Set the upload path for this Job. The URL was generated when the job was create. Results are ready when Job "status" is 'complete'.
    download_url = ''
    
    #Call the method for uploading the ID file.
    success = download_results(download_url, results_file_path)

    if success:
        print(f"Downloaded results to file {results_file_path}.")
