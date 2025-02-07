import json
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str = Field(..., regex=r'^T\d+$')
    user_id: str = Field(..., regex=r'^U\d+$')
    timestamp: datetime
    amount: float
    device_type: str
    location: str
    is_vpn: bool
    card_type: str
    status: str

def handler(event, context):
    # Iterate over each record in the Kinesis data stream event
    for record in event['Records']:
        # Decode the base64 encoded data
        payload = json.loads(record['kinesis']['data'])
        
        try:
            # Validate the data using Pydantic
            transaction = Transaction(**payload)
            print(f"Valid record: {transaction}")
        except ValidationError as e:
            print(f"Invalid record: {payload} - Error: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data validation complete')
    }
