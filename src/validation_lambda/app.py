import base64
from enum import Enum
import json
from pydantic import BaseModel, Field, ValidationError

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
    transation: Transaction
    status: str = Status.ok.value
    error: str = ""


class InvalidTransaction(BaseModel):
    data: dict
    status: Status = Status.failed
    error: str


def valid_transaction(event, _) -> dict[str, list[ValidTransaction]]:
    '''Return only valid transactions
    '''
    data: list[ValidTransaction] = []
    # Iterate over each record in the Kinesis data stream event
    for record in event['Records']:
        # Decode the base64 encoded data
        event = record['kinesis']['data']
        if isinstance(event, str):
            payload = json.loads(base64.b64decode(event).decode('utf-8'))
        else:
            payload = event
        try:
            # Validate the data using Pydantic
            data.append(ValidTransaction(
                transation=Transaction(**payload),
                error=""
            ).model_dump())
        except ValidationError as e:
            pass
    return {
        "data": data
        }
