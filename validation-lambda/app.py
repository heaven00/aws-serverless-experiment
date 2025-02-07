import json

def handler(event, context):
    # Iterate over each record in the Kinesis data stream event
    for record in event['Records']:
        # Decode the base64 encoded data
        payload = json.loads(record['kinesis']['data'])
        
        # Validate the data (example validation: check if 'name' and 'age' fields exist)
        if 'name' not in payload or 'age' not in payload:
            print(f"Invalid record: {payload}")
            continue
        
        # Additional validation can be added here
        if not isinstance(payload['name'], str) or not isinstance(payload['age'], int):
            print(f"Invalid data types in record: {payload}")
            continue
        
        # If the record is valid, process it (example processing: just print)
        print(f"Valid record: {payload}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data validation complete')
    }
