# Greco Derby Day MMS Uploader


This lambda function will sit behind an AWS API Gateway and listen to requests from Twilio's webhook.  The lambda receives and incoming webhook, finds the relevant MMS URLs, and automatically uploads them to an S3 bucket for processing.

