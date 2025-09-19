"""
Lambda Function 1:serializer
A lambda function that copies an object from S3, base64 encodes it, and 
then return it (serialized data) to the step function as `image_data` in an event.
"""
import json
import boto3
import base64

# A low-level client representing Amazon Simple Storage Service (S3)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input (You may also check lambda test)
    key = event['s3_key']                               ## TODO: fill in
    bucket = event['s3_bucket']                         ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:          # Read binary file
        image_data = base64.b64encode(f.read())      # Base64 encode binary data ('image_data' -> class:bytes)

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
   
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,      # Bytes data
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
"""
Lambda function 2 : classify

A lambda function that is responsible for the classification part. It takes the image output from the 
lambda 1 function, decodes it, and then pass inferences back to the the Step Function
"""

import json
import base64
import boto3

runtime_client = boto3.client('sagemaker-runtime')
ENDPOINT = "image-classification-2025-09-19-09-55-48-763"

def lambda_handler(event, context):
    # Defensive: handle both direct key or nested body
    if "image_data" in event:
        image_b64 = event["image_data"]
    elif "body" in event and "image_data" in event["body"]:
        image_b64 = event["body"]["image_data"]
    else:
        raise KeyError("Expected key 'image_data' not found in event")

    # Decode base64 image
    image = base64.b64decode(image_b64)

    # Call endpoint
    response = runtime_client.invoke_endpoint(
        EndpointName=ENDPOINT,
        Body=image,
        ContentType="image/png"
    )

    inferences = json.loads(response["Body"].read().decode("utf-8"))

    event["inferences"] = inferences
    return {
        "statusCode": 200,
        "body": event
    }
"""
Lambda Function 3:  filter_threshold

A lambda function that takes the inferences from the Lambda 2 function output and filters low-confidence inferences
(above a certain threshold indicating success)
"""
import json

THRESHOLD = 0.93

def lambda_handler(event, context):
    # Agar body ke andar wrapped hai to extract karo
    body = event.get("body", event)
    if isinstance(body, str):
        body = json.loads(body)

    # Grab the inferences from the event
    inferences = body.get("inferences", [])

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(i > THRESHOLD for i in inferences)

    # If threshold not met, raise error
    if not meets_threshold:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    # If threshold met, return full event
    return {
        "statusCode": 200,
        "body": body
    }
