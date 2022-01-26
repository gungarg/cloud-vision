from google.cloud import vision
from google.cloud import storage
import os
clientStorage = storage.Client()

"""
Triggered when a new file is uploaded to Cloud Storage bucket
"""
def init(event, context):
    bucketName = event['bucket']
    fileName = event['name']

    bucket = clientStorage.get_bucket(bucketName)
    blob = bucket.get_blob(fileName)
    uri = "gs://" + bucketName + "/" + fileName

    image = vision.Image()
    image.source.image_uri = uri

    clientVision = vision.ImageAnnotatorClient()
    response = clientVision.safe_search_detection(image=image)
    safe = response.safe_search_annotation

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN','VERY_UNLIKELY','UNLIKELY','POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')

    if ((likelihood_name[safe.violence] in likelihood_name[3:]) or
        (likelihood_name[safe.racy] in likelihood_name[3:]) or
        (likelihood_name[safe.adult] in likelihood_name[3:])):

        print("Copy {} to flagged bucket".format(fileName))
        copy_blob(bucketName, fileName, os.environ.get('BUCKET_FLAGGED',''), fileName)
    else:
        print("Copy {} to safe bucket".format(fileName))
        copy_blob(bucketName, fileName, os.environ.get('BUCKET_SAFE',''), fileName)

"""
Copy file from one bucket to another
"""
def copy_blob(
    source_bucket_name, source_blob_name, destination_bucket_name, destination_blob_name):

    source_bucket = clientStorage.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)
    destination_bucket = clientStorage.bucket(destination_bucket_name)

    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )
