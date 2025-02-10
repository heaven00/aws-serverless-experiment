import json
from datetime import datetime
from src.validation_lambda.app import valid_transaction, Status
import base64


# Helper function to encode payloadds
def encode_payload(payload):
    payload_json = json.dumps(payload)
    return base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')


def decode_payload(payload):
    return payload

# Sample valid transaction
def dummy_valid_transaction():
    return {
        "transaction_id": "T12345",
        "user_id": "U56789",
        "timestamp": datetime.utcnow().isoformat(),
        "amount": 254.67,
        "device_type": "mobile",
        "location": "California, USA",
        "is_vpn": "false",
        "card_type": "credit",
        "status": "approved",
    }


# Test case for valid transaction
def test_valid_transaction_should_process():
    event = {"Records": [{"kinesis": {"data": encode_payload(dummy_valid_transaction())}}]}

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 1
    assert response[0]["status"] == Status.ok.value
    assert response[0]["error"] == ""


def test_transaction_with_json_data_in_kinesis_event():
    event = {"Records": [{"kinesis": {"data": dummy_valid_transaction()}}]}

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 1
    assert response[0]["status"] == Status.ok.value
    assert response[0]["error"] == ""


# Test case for invalid transaction with missing fields
def test_invalid_transaction_missing_fields_should_return_empty_response():
    invalid_payload = dummy_valid_transaction()
    del invalid_payload["transaction_id"]  # Remove a required field
    event = {"Records": [{"kinesis": {"data": encode_payload(invalid_payload)}}]}

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 0


# Test case for invalid transaction with incorrect format
def test_invalid_transaction_incorrect_format_should_return_empty_response():
    invalid_payload = dummy_valid_transaction()
    invalid_payload["transaction_id"] = "12345"  # Does not match regex
    event = {"Records": [{"kinesis": {"data": encode_payload(invalid_payload)}}]}

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 0


# Test case for multiple records
def test_multiple_transactions():
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
        ]
    }

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 2
    assert all(tx["status"] == Status.ok.value for tx in response)


def test_multiple_mix_transactions_should_filter_invalid_transactions():
    invalid_payload = dummy_valid_transaction()
    invalid_payload["transaction_id"] = "12345"
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
            {"kinesis": {"data": encode_payload(invalid_payload)}},
        ]
    }

    response = decode_payload(valid_transaction(event, None))['data']

    assert len(response) == 2


def test_output_is_json_serializable():
    """Lambda expects output to be serializable"""
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(dummy_valid_transaction())}},
        ]
    }

    response = decode_payload(valid_transaction(event, None))['data']
    assert json.dumps(response)


# Test case for empty event
def test_empty_event():
    event = {"Records": []}
    response = valid_transaction(event, None)
    assert response == {'data': []}
