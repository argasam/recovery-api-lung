# Library
## .env
import io
import numpy as np
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

## local
from model.model import preprocess_image
from imageConversion.dicomToJpg import preprocess_dicom_to_jpg
from imageConversion.structuredReport import create_structured_report
from orthancConnection.orthancUpload import upload_to_orthanc

app = FastAPI()

# Load Secrets from JSON    
with open("secrets.json") as f:
    secrets = json.load(f)

ORTHANC_URL = secrets["ORTHANC_URL"]
ORTHANC_USERNAME = secrets["ORTHANC_USERNAME"]
ORTHANC_PASSWORD = secrets["ORTHANC_PASSWORD"]

@app.get("/")
async def root():
    return {"health_check": "OK", "model_version": "v1.0"}


@app.post("/prediction/")
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()

    # Convert file bytes to BytesIO object
    dcm_file = io.BytesIO(file_bytes)
    
    # Read Dicom file
    # Process the DICOM file with pydicom
    try:
        dataset = pydicom.dcmread(dcm_file)
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": "Error processing DICOM file", "details": str(e)})
    
    # Process to JPG
    img = preprocess_dicom_to_jpg(file_bytes)
    # img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    prediction = preprocess_image(img_bytes)
    class_label = 'Pneumonia' if prediction > 0.5 else 'Normal'
    confidence = float(prediction) if class_label == 'Pneumonia' else float(1 - prediction)

    dataset.ContentDate = "20220101"
    dataset.ContentTime = "120000"
    
    # Set required attributes for saving
    dataset.is_little_endian = True
    dataset.is_implicit_VR = True

    sr = create_structured_report(dataset, class_label, confidence)

    dicom_file = io.BytesIO()
    sr.save_as(dicom_file)
    dicom_file.seek(0)

    orthanc_response = await upload_to_orthanc(dicom_file)
    date_now = str(datetime.now())

    response = JSONResponse(content={
        "filename": file.filename,
        "prediction": class_label,
        "confidence": confidence,
        "date": date_now,
        # "structured_report": sr_json,
        "orthanc_response": orthanc_response
    })

    print(json.dumps(json.loads(response.body.decode()), indent=4))
    
    return response
