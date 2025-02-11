import json
import base64
import boto3
import os
from datetime import datetime
from moto import mock_aws
import pytest
from src.validation_lambda.app import valid_transaction, Status, write_to_s3

# Setup environment variables for S3
VALID_BUCKET = "valid-bucket"
INVALID_BUCKET = "invalid-bucket"
os.environ["VALIDDATA_BUCKET_NAME"] = VALID_BUCKET
os.environ["INVALIDDATA_BUCKET_NAME"] = INVALID_BUCKET


@pytest.fixture(scope="function")
def s3_mock():
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=VALID_BUCKET)
        s3.create_bucket(Bucket=INVALID_BUCKET)
        yield s3


def encode_payload(payload):
    payload_json = json.dumps(payload)
    return base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")


# Sample valid transaction
def dummy_valid_transaction():
    return {
        "transaction_id": "T12345",
        "user_id": "U56789",
        "timestamp": datetime.utcnow().isoformat(),
        "amount": 254.67,
        "device_type": "mobile",
        "location": "California, USA",
        "is_vpn": False,
        "card_type": "credit",
        "status": "approved",
    }


def test_valid_transaction_should_process(s3_mock):
    event = {
        "Records": [{"kinesis": {"data": encode_payload(dummy_valid_transaction())}}]
    }
    response = valid_transaction(event, None)["data"]

    assert len(response) == 1
    assert response[0]["status"] == Status.ok.value
    assert response[0]["error"] == ""

    # Check if data is written to S3
    s3_objects = s3_mock.list_objects(Bucket=VALID_BUCKET)
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 1

    # should not write to invalid bucket
    s3_objects = s3_mock.list_objects(Bucket=INVALID_BUCKET)
    assert "Contents" not in s3_objects


def test_invalid_transaction_should_write_to_invalid_s3(s3_mock):
    invalid_payload = dummy_valid_transaction()
    del invalid_payload["transaction_id"]  # Remove a required field
    event = {"Records": [{"kinesis": {"data": encode_payload(invalid_payload)}}]}

    valid_transaction(event, None)  # Process transaction

    # Check if invalid transaction is written to INVALID S3 bucket
    s3_objects = s3_mock.list_objects(Bucket=INVALID_BUCKET)
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 1

    # should not write to valid bucket 
    s3_objects = s3_mock.list_objects(Bucket=VALID_BUCKET)
    assert "Contents" not in s3_objects


def test_multiple_transactions(s3_mock):
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
        ]
    }
    response = valid_transaction(event, None)['data']

    assert len(response) == 2
    assert all(tx["status"] == Status.ok.value for tx in response)


def test_output_is_json_serializable(s3_mock):
    """Lambda expects output to be serializable"""
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
        ]
    }

    response = valid_transaction(event, None)['data']
    assert json.dumps(response)


def test_write_to_s3(s3_mock):
    content = json.dumps({"test": "data"})
    write_to_s3(VALID_BUCKET, "test_transaction", content)

    s3_objects = s3_mock.list_objects(Bucket=VALID_BUCKET)
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 1
