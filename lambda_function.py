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
            picture_bucket = "grecoderbyday-source"
            text_bucket = "grecoderbyday-messages"
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
                    picture_key = "pics/original/2019/" + rand_uuid + ".png"
                    text_key = "messages/" + rand_uuid + ".txt"
                    resp_url = "https://s3-us-east-1.amazonaws.com/{0}/{1}".format(picture_bucket, str(picture_key))
                    m_data = {'fromNumber': from_number, 'url': resp_url}
                    s3.Bucket(picture_bucket).put_object(Key=picture_key, Body=image.read(), ACL='public-read', ContentType='image/png', Metadata=m_data)
                    s3.Bucket(text_bucket).put_object(Key=text_key, Body=str(event), ACL='private',ContentType='text/plain', Metadata=m_data)   
                return_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Thank you for your submission.  Visit https://grecoderbyday.com to view images</Message></Response>'
                print(return_xml)
                return return_xml
            else:
                success_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>No image found.  Please attach an image.</Message></Response>'
                print(success_xml)
                return success_xml
        else:
            print("Request is invalid")
            return_error_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Sorry Dave, I cannot do that.</Message></Response>'
            return return_error_xml

    else:
        return_message = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Hell No</Message></Response>'
        return return_message

