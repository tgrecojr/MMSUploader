import boto3
import json
import urllib
import os
import random

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

        # print("Form params:",form_parameters,"validity:",request_valid)
        # If the request is valid and this is from the master number,
        # give the secret!
        if request_valid:
            # The message is validated and is from the master number
            print("Request is valid:")
            num_media = event['NumMedia']
            
            if num_media != '0':
                from_number = event['From']
                pic_url = event['MediaUrl0']
                decoded_pic = urllib.parse.unquote_plus(pic_url)
                print("decoded pic: " + str(decoded_pic))
                twilio_pic = urllib.request.Request(decoded_pic, headers={'User-Agent': "Magic Browser"})
                image = urllib.request.urlopen(twilio_pic)
                bucket = "grecoderbyday-source"
                rand_num = str(random.getrandbits(64))
                key = "pics/original/2019/" + rand_num + ".png"
                resp_url = "https://s3-us-east-1.amazonaws.com/{0}/{1}".format(bucket, str(key))
                m_data = {'fromNumber': from_number, 'url': resp_url}
                s3.Bucket(bucket).put_object(Key=key, Body=image.read(), ACL='public-read', ContentType='image/png', Metadata=m_data)
                return_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Thank you for your submission.  Visit http://grecoderbyday.com to view images</Message></Response>'
                print(return_xml)
                return return_xml
            else:
                success_xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>No image found.  Please attach an image.</Message></Response>'
                print(success_xml)
                return success_xml
            

        else:
            # Validation failed in some way; don't give up the secret
            print("Request is invalid")
            return_error = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Sorry Dave, I cannot do that.</Message></Response>'
            return return_error

    else:
        return_message = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>Hell No</Message></Response>'
        return return_message