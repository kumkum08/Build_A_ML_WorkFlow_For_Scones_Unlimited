
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
