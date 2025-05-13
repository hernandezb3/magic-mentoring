import requests
import zipfile
import json
import io
import os
import sys
from library import secrets

# Setting user Parameters

try:
    apiToken = os.environ['APIKEY']
except KeyError:
    print("set environment variable APIKEY")
    sys.exit(2) 


surveyId = secrets.SURVEY_NAME_ID
dataCenter = secrets.DATA_CENTER

# Setting static parameters
requestCheckProgress = 0.0
progressStatus = "inProgress"
url = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
    }

# Step 1: Creating Data Export
data = {
        "format": "csv",
        "seenUnansweredRecode": 2
       }

downloadRequestResponse = requests.request("POST", url, json=data, headers=headers)
print(downloadRequestResponse.json())

try:
    progressId = downloadRequestResponse.json()["result"]["progressId"]
except KeyError:
    print(downloadRequestResponse.json())
    sys.exit(2)
    
isFile = None

max_retries = 5
retry_count = 0

# Step 2: Checking on Data Export Progress and waiting until export is ready
while progressStatus != "complete" and progressStatus != "failed" and isFile is None:
    if isFile is None:
        print("File not ready")
    else:
        print("ProgressStatus=", progressStatus)
    
    requestCheckUrl = url + progressId
    requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
    
    try:
     isFile = requestCheckResponse.json()["result"]["fileId"]
    except KeyError:
     1==1

    print(requestCheckResponse.json())
    requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
    print("Download is " + str(requestCheckProgress) + " complete")
    progressStatus = requestCheckResponse.json()["result"]["status"]

    if progressStatus not in ["complete", "failed"]:
        # Implement exponential backoff with a maximum number of retries
        retry_count += 1
        if retry_count > max_retries:
            print("Exceeded maximum retries. Exiting.")
            sys.exit(1)
        
        # Calculate the next sleep interval using exponential backoff (The first retry will occur after 200 seconds, the second after 400 seconds, the third after 600 seconds, and so on, until the max_retries limit is reached)
        sleep_interval = 200 ** retry_count
        print(f"Retrying in {sleep_interval} seconds...")
        time.sleep(sleep_interval)

# Step 3: Downloading file
requestDownloadUrl = url + fileId + '/file'
requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)

# Step 4: Unzipping the file
zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("MyQualtricsDownload")
print('Complete')