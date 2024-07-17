from fastapi import UploadFile
import pydicom
import numpy as np
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid, SecondaryCaptureImageStorage
from pydicom.sequence import Sequence
import highdicom as hd
from pydicom.sr.codedict import codes
from datetime import datetime

def create_structured_report(file, class_label, confidence):

    # Load and Set Data from original_ds
    patient_name = file.PatientName
    patient_ID = file.PatientID
    study_instance_UID = file.StudyInstanceUID
    study_ID = file.StudyID

    file.SOPClassUID = SecondaryCaptureImageStorage  # Basic Text SR
    file.SOPInstanceUID = generate_uid()
    file.SeriesInstanceUID = generate_uid()
    file.SeriesNumber += 1 # Arbitrary number for the new series
    file.InstanceNumber += 1
    file.Modality = 'OT'
    

    # Standart using TID1500
    # Contains observation_context, procedure_reported, imaging_measurements=None, 
    # title=None, language_of_content_item_and_descendants=None, referenced_images=None

    # Describe the context of reported observations: the person that reported
    # the observations and the device that was used to make the observations
    observer_person_context = hd.sr.ObserverContext(
        observer_type=codes.cid270.Person,
        observer_identifying_attributes=hd.sr.PersonObserverIdentifyingAttributes(
            name='AI Identifier'
        )
    )
    observer_device_context = hd.sr.ObserverContext(
        observer_type=codes.cid270.Device,
        observer_identifying_attributes=hd.sr.DeviceObserverIdentifyingAttributes(
            uid=hd.UID()
        )
    )
    observation_context = hd.sr.ObservationContext(
        observer_person_context=observer_person_context,
        observer_device_context=observer_device_context,
    )

    # Create Procedure
    procedure_reported = [
        hd.sr.CodedConcept(
            value= "112000",
            scheme_designator="DCM",
            meaning="Chest CAD Report"
        )
    ]

    # Define the image region (a circle) using image coordinates
    region = hd.sr.ImageRegion(
       graphic_type=hd.sr.GraphicTypeValues.CIRCLE,
       graphic_data=np.array([[45.0, 55.0], [45.0, 65.0]]),
       source_image=hd.sr.SourceImageForRegion.from_source_image(file),
    )

    # Create algorithm identification
    algorithm_identification = hd.sr.AlgorithmIdentification(
        name='AI Model Detection',
        version='v1.0',
    )

    # Create AI Findings as Measurement
    measurements_confidence = hd.sr.Measurement(
            name=hd.sr.CodedConcept(
                value="Confidence",
                scheme_designator="OWN",
                meaning = "Confidence Score"
            ),
            value=confidence,
            unit=hd.sr.CodedConcept(
                value="Null",
                scheme_designator="OWN",
                meaning="No Unit"
            ),
            algorithm_id=algorithm_identification
        )
    
    measurement_labels=hd.sr.Measurement(
            name=hd.sr.CodedConcept(
                value=class_label,
                scheme_designator="OWN",
                meaning = "Labels on Detection"
            ),
            value= 1,
            unit=hd.sr.CodedConcept(
                value="Null",
                scheme_designator="OWN",
                meaning="No Unit"
            ),
            algorithm_id=algorithm_identification
        )
    

    

    # Compile Measurements using Type
    imaging_measurement = hd.sr.PlanarROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=hd.sr.TrackingIdentifier(uid=hd.UID(), identifier='Planar ROI Measurements'),
            measurements=[measurements_confidence, measurement_labels],
            finding_type=hd.sr.CodedConcept(
                value="121071",
                scheme_designator="DCM",
                meaning="Finding"
            ),
            referenced_region=region
        )

    # Create Report
    measurement_report = hd.sr.MeasurementReport(
        observation_context=observation_context,
        procedure_reported=procedure_reported,
        imaging_measurements=[imaging_measurement],
        title=hd.sr.CodedConcept(
            value='125031',
            scheme_designator='DCM',
            meaning='Imaging Measurement Report'
        ),
    )

    sr_dataset = hd.sr.ComprehensiveSR(
        evidence=[file],
        content=measurement_report,
        series_instance_uid= file.SeriesInstanceUID,
        series_number= file.SeriesNumber,
        sop_instance_uid=file.SOPInstanceUID,
        instance_number=file.InstanceNumber,
        manufacturer='Manufacturer'
    )

    return sr_dataset