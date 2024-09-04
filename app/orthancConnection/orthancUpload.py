import aiohttp
import json
from io import BytesIO

# Load Secrets from JSON    
with open("app/secrets.json") as f:
    secrets = json.load(f)

ORTHANC_URL = secrets["ORTHANC_URL"]
ORTHANC_USERNAME = secrets["ORTHANC_USERNAME"]
ORTHANC_PASSWORD = secrets["ORTHANC_PASSWORD"]


# Function to upload the DICOM file to Orthanc
async def upload_to_orthanc(dicom_file: BytesIO):
    dicom_file.seek(0)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ORTHANC_URL}/instances", 
            data=dicom_file.read(), 
            headers={"Content-Type": "application/dicom"},
            auth=aiohttp.BasicAuth(ORTHANC_USERNAME, ORTHANC_PASSWORD)) as response:
                response_text = await response.text()  # Log the raw response text
                print("Orthanc Response Text:", response_text)  # Log the response text
                
                resp_json = await response.json()
                if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
                    return resp_json
                else:
                    return {"error": "Unexpected response type", "response_text": resp_json}