import base64
from datetime import datetime
from enum import Enum
import json
from pydantic import BaseModel, Field, ValidationError
import os
import boto3

class Transaction(BaseModel):
    transaction_id: str = Field(..., pattern=r'^T\d+$')
    user_id: str = Field(..., pattern=r'^U\d+$')
    timestamp: str
    amount: float
    device_type: str
    location: str
    is_vpn: bool
    card_type: str
    status: str


class Status(Enum):
    ok = "ok"
    failed = "failed"


class ValidTransaction(BaseModel):
    transaction: Transaction
    status: str = Status.ok.value
    error: str = ""


class InvalidTransaction(BaseModel):
    transaction: dict
    status: Status = Status.failed
    error: str


def valid_transaction(event, _) -> dict[str, list[ValidTransaction]]:
    '''Return only valid transactions
    '''
    # get environment variables
    valid_data_bucket_name = os.getenv('VALIDDATA_BUCKET_NAME')
    # fraud_detection_model_function_name = os.getenv('FRAUDDETECTIONMODEL_FUNCTION_NAME')
    # fraud_detection_model_function_arn = os.getenv('FRAUDDETECTIONMODEL_FUNCTION_ARN')
    invalid_data_bucket_name = os.getenv('INVALIDDATA_BUCKET_NAME')

    data: list[ValidTransaction] = []
    invalid_data: list[InvalidTransaction] = []
    # Iterate over each record in the Kinesis data stream event
    for record in event['Records']:
        # Decode the base64 encoded data
        event = record['kinesis']['data']    
        payload = json.loads(base64.b64decode(event).decode('utf-8'))
        try:
            # Validate the data using Pydantic
            valid_trx = ValidTransaction(
                transaction=Transaction(**payload),
                error=""
            )
            data.append(valid_trx.model_dump())
            write_to_s3(
                valid_data_bucket_name,
                valid_trx.transaction.transaction_id,
                valid_trx.model_dump_json()
                )
        except ValidationError as e:
            invalid_trx = InvalidTransaction(
                transaction=payload,
                error=str(e)
            )
            invalid_data.append(invalid_trx.model_dump())
            write_to_s3(
                invalid_data_bucket_name,
                hash(str(invalid_trx.transaction)),
                invalid_trx.model_dump_json()
                )
    return {
        "data": data
    }


def write_to_s3(bucket_name, name, content):
    s3 = boto3.client('s3')
    today = datetime.now()
    year, month, date = today.year, today.month, today.day
    object_name = f"{year}/{month}/{date}/{name}.json"
    response = s3.put_object(Bucket=bucket_name, Key=object_name, Body=content)
    return response
