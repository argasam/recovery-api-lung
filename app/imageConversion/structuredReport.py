import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid, SecondaryCaptureImageStorage, ImplicitVRLittleEndian
from datetime import datetime

def create_structured_report(file, report):
    # Create the FileDataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Set transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Copy relevant attributes from the original file
    ds.PatientName = file.PatientName
    ds.PatientID = file.PatientID
    ds.StudyInstanceUID = file.StudyInstanceUID
    ds.StudyID = file.StudyID
    ds.SOPClassUID = SecondaryCaptureImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesNumber = getattr(file, 'SeriesNumber', 0) + 1
    ds.InstanceNumber = getattr(file, 'InstanceNumber', 0) + 1
    ds.Modality = 'SR'
    ds.ContentDate = datetime.now().strftime('%Y%m%d')
    ds.ContentTime = datetime.now().strftime('%H%M%S')

    # Create the Content Sequence
    content_seq = Sequence()

    # Add a CONTAINER content item
    container = Dataset()
    container.RelationshipType = "CONTAINS"
    container.ValueType = "CONTAINER"
    container.ConceptNameCodeSequence = Sequence([Dataset()])
    container.ConceptNameCodeSequence[0].CodeValue = "121070"
    container.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
    container.ConceptNameCodeSequence[0].CodeMeaning = "Findings"

    # Add Long Text Report
    text_report = Dataset()
    text_report.RelationshipType = "CONTAINS"
    text_report.ValueType = "TEXT"
    text_report.ConceptNameCodeSequence = Sequence([Dataset()])
    text_report.ConceptNameCodeSequence[0].CodeValue = "121071"
    text_report.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
    text_report.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
    text_report.TextValue = report

    # Add content items to sequences
    container.ContentSequence = Sequence([text_report])
    content_seq.append(container)

    # Add Content Sequence to the main dataset
    ds.ContentSequence = content_seq

    return ds

# from fastapi import UploadFile
# import pydicom
# import numpy as np
# from pydicom.uid import generate_uid, SecondaryCaptureImageStorage
# from pydicom.sequence import Sequence
# import highdicom as hd
# from pydicom.sr.codedict import codes
# from datetime import datetime

# def create_structured_report(file, class_label, confidence, report):

#     # Load and Set Data from original_ds
#     patient_name = file.PatientName
#     patient_ID = file.PatientID
#     study_instance_UID = file.StudyInstanceUID
#     study_ID = file.StudyID

#     file.SOPClassUID = SecondaryCaptureImageStorage  # Basic Text SR
#     file.SOPInstanceUID = generate_uid()
#     file.SeriesInstanceUID = generate_uid()
#     file.SeriesNumber += 1 # Arbitrary number for the new series
#     file.InstanceNumber += 1
#     file.Modality = 'OT'
    

#     # Standart using TID1500
#     # Contains observation_context, procedure_reported, imaging_measurements=None, 
#     # title=None, language_of_content_item_and_descendants=None, referenced_images=None

#     # Describe the context of reported observations: the person that reported
#     # the observations and the device that was used to make the observations
#     observer_person_context = hd.sr.ObserverContext(
#         observer_type=codes.cid270.Person,
#         observer_identifying_attributes=hd.sr.PersonObserverIdentifyingAttributes(
#             name='AI Identifier'
#         )
#     )
#     observer_device_context = hd.sr.ObserverContext(
#         observer_type=codes.cid270.Device,
#         observer_identifying_attributes=hd.sr.DeviceObserverIdentifyingAttributes(
#             uid=hd.UID()
#         )
#     )
#     observation_context = hd.sr.ObservationContext(
#         observer_person_context=observer_person_context,
#         observer_device_context=observer_device_context,
#     )

#     # Create Procedure
#     procedure_reported = [
#         hd.sr.CodedConcept(
#             value= "112000",
#             scheme_designator="DCM",
#             meaning="Chest CAD Report"
#         )
#     ]


#     # Create algorithm identification
#     algorithm_identification = hd.sr.AlgorithmIdentification(
#         name='AI Model Detection',
#         version='v1.0',
#     )

#     # Create AI Findings as Measurement
#     measurements_confidence = hd.sr.Measurement(
#             name=hd.sr.CodedConcept(
#                 value="Confidence",
#                 scheme_designator="OWN",
#                 meaning = "Confidence Score"
#             ),
#             value=confidence,
#             unit=hd.sr.CodedConcept(
#                 value="Null",
#                 scheme_designator="OWN",
#                 meaning="No Unit"
#             ),
#             algorithm_id=algorithm_identification
#         )
    
#     measurement_labels=hd.sr.Measurement(
#             name=hd.sr.CodedConcept(
#                 value=class_label,
#                 scheme_designator="OWN",
#                 meaning = "Labels on Detection"
#             ),
#             value= 1,
#             unit=hd.sr.CodedConcept(
#                 value="Null",
#                 scheme_designator="OWN",
#                 meaning="No Unit"
#             ),
#             algorithm_id=algorithm_identification
#         )
    
#     # Create a reference to the entire image
#     image_region = hd.sr.ImageRegion(
#         graphic_type= hd.sr.GraphicTypeValues.POINT,
#         graphic_data=np.array([[100, 100]]),  # Arbitrary point, adjust as needed
#         source_image=hd.sr.SourceImageForRegion(
#             referenced_sop_class_uid=file.SOPClassUID,
#             referenced_sop_instance_uid=file.SOPInstanceUID,
#         ) # Assuming 'file' is your DICOM dataset
#     )

#     # Long text report
#     report_item = hd.sr.TextContentItem(
#         name=hd.sr.CodedConcept(
#             value="121071",
#             scheme_designator="DCM",
#             meaning="Finding"
#         ),
#         value=report,  # This can now be a much longer string
#     )

#     # Qualitative evaluation (if needed)
#     qualitative_eval = hd.sr.QualitativeEvaluation(
#         name=hd.sr.CodedConcept(
#             value="112003",
#             scheme_designator="DCM",
#             meaning="Overall assessment"
#         ),
#         value=hd.sr.CodedConcept(
#             value=class_label,
#             scheme_designator="OWN",
#             meaning="AI Classification"
#         )
#     )

#     # Imaging measurement
#     imaging_measurement = hd.sr.PlanarROIMeasurementsAndQualitativeEvaluations(
#         tracking_identifier=hd.sr.TrackingIdentifier(uid=hd.UID(), identifier='Planar ROI Measurements'),
#         referenced_region=image_region,
#         measurements=[measurements_confidence, measurement_labels],
#         finding_type=hd.sr.CodedConcept(
#             value="121071",
#             scheme_designator="DCM",
#             meaning=class_label
#         ),
#         qualitative_evaluations=[qualitative_eval]
#     )

#     # Create a container for the report text
#     text_container = hd.sr.ContainerContentItem(
#         name=hd.sr.CodedConcept(
#             value="121070",
#             scheme_designator="DCM",
#             meaning="Findings"
#         )
#     )

#     # Measurement report
#     measurement_report = hd.sr.MeasurementReport(
#         observation_context=observation_context,
#         procedure_reported=procedure_reported,
#         imaging_measurements=[imaging_measurement],
#         title=hd.sr.CodedConcept(
#             value='125031',
#             scheme_designator='DCM',
#             meaning='Imaging Measurement Report'
#         ),
#     )

#     # Create a longer text report
#     long_report = """
#     This is a much longer report that exceeds 64 characters. It can contain multiple sentences and paragraphs to provide a detailed description or analysis. 

#     The TextContentItem allows for essentially unlimited text length, so you can include as much information as needed in your structured report.

#     You can add multiple paragraphs, lists, or any other text formatting you need within the constraints of plain text.
#     """

#     # Create the text content item
#     text_content = hd.sr.TextContentItem(
#         name=codes.DCM.FindingsImpression,
#         value=long_report
#     )

#     # Create a container for the report
#     container = hd.sr.ContainerContentItem(
#         name=codes.DCM.ImageReport,
#         template_id="5000",
#         is_content_continuous=True
#     )

#     # Add the text content to the container
#     container.ContentSequence = [text_content]

#     # Create SR dataset
#     sr_dataset = hd.sr.ComprehensiveSR(
#         evidence=[file],
#         content=container,
#         series_instance_uid= file.SeriesInstanceUID,
#         series_number= file.SeriesNumber,
#         sop_instance_uid=file.SOPInstanceUID,
#         instance_number=file.InstanceNumber,
#         manufacturer='Manufacturer'
#     )

#     return sr_dataset