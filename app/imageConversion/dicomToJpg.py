import io
import numpy as np
from PIL import Image
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut


def preprocess_dicom_to_jpg(dicom_data):
    ds = pydicom.dcmread(io.BytesIO(dicom_data))
    image = ds.pixel_array.astype(float)

    if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
        image = (image * ds.RescaleSlope) + ds.RescaleIntercept

    if 'WindowCenter' in ds and 'WindowWidth' in ds:
        image = apply_voi_lut(image, ds)
    else:
        image = (image - image.min()) / (image.max() - image.min())

    image = (image * 255).astype(np.uint8)
    pil_image = Image.fromarray(image)

    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    return pil_image