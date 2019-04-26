import boto3
import json
import urllib
import os
import uuid

from twilio import twiml
from twilio.request_validator import RequestValidator
from boto3.session import Session

s3 = boto3.resource('s3')
session = Session()


def lambda_handler(event, context):
    
    print("Received event: " + str(event))

    if u'twilioSignature' in event and u'Body' in event:
        form_parameters = {
            k: urllib.parse.unquote_plus(v) for k, v in event.items()
            if k != u'twilioSignature'
        }
        validator = RequestValidator(os.environ['AUTH_TOKEN'])
        request_valid = validator.validate(
            os.environ['REQUEST_URL'],
            form_parameters,
            event[u'twilioSignature']
        )
        if request_valid:
            num_media = event['NumMedia']
            picture_bucket = os.environ['PICTURE_BUCKET']
            text_bucket = os.environ['TEXT_BUCKET']
            if num_media != '0':
                from_number = event['From']
                int_nummedia = int(num_media)
                for i in range(int_nummedia):
                    media_number = 'MediaUrl' + (str(i)) 
                    pic_url = event[media_number]
                    decoded_pic = urllib.parse.unquote_plus(pic_url)
                    twilio_pic = urllib.request.Request(decoded_pic, headers={'User-Agent': "Magic Browser"})
                    image = urllib.request.urlopen(twilio_pic)
                    rand_uuid = str(uuid.uuid4())
                    picture_key = os.environ['PICTURE_KEY'] + rand_uuid + ".png"
                    text_key = os.environ['TEXT_KEY'] + rand_uuid + ".txt"
                    resp_url = "https://s3-us-east-1.amazonaws.com/{0}/{1}".format(picture_bucket, str(picture_key))
                    m_data = {'fromNumber': from_number, 'url': resp_url}
                    s3.Bucket(picture_bucket).put_object(Key=picture_key, Body=image.read(), ACL='public-read', ContentType='image/png', Metadata=m_data)
                    s3.Bucket(text_bucket).put_object(Key=text_key, Body=str(event), ACL='private',ContentType='text/plain', Metadata=m_data)   
                return_xml = os.environ['RETURN_XML']
                print(return_xml)
                return return_xml
            else:
                no_image_xml = os.environ['NO_IMAGE_XML']
                print(no_image_xml)
                return no_image_xml
        else:
            print("Request is invalid")
            invalid_request_xml = os.environ['INVALID_REQUEST_XML']
            return invalid_request_xml

    else:
        no_signature_xml = os.environ['NO_SIGNATURE_XML']
        return no_signature_xml

