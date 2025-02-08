from enum import Enum
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


class Status(Enum):
    ok = "ok"
    failed = "failed"


class ValidatedTransaction(BaseModel):
    data: Transaction
    status: Status
    error: str


def handler(event, _) -> list[ValidatedTransaction]:
    data: list[ValidatedTransaction] = []
    # Iterate over each record in the Kinesis data stream event
    for record in event['Records']:
        # Decode the base64 encoded data
        payload = json.loads(record['kinesis']['data'])
        try:
            # Validate the data using Pydantic
            transaction = Transaction(**payload)
            data.append(ValidatedTransaction(
                data=transaction,
                status=Status.ok,
                error=""
            ))
        except ValidationError as e:
            data.append(ValidatedTransaction(
                data=transaction,
                status=Status.failed,
                error=e
            ))    
    return data
