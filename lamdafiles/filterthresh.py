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
