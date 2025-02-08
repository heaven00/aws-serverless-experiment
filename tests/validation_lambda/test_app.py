import json
from datetime import datetime
from src.validation_lambda.app import valid_transaction_handler, Status

# Helper function to encode payload


def encode_payload(payload):
    return json.dumps(payload)


def decode_payload(payload):
    return payload

# Sample valid transaction
def valid_transaction():
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
def test_valid_transaction():
    event = {"Records": [{"kinesis": {"data": encode_payload(valid_transaction())}}]}

    response = decode_payload(valid_transaction_handler(event, None))['data']

    assert len(response) == 1
    print(response)
    assert response[0]["status"] == Status.ok.value
    assert response[0]["error"] == ""


# Test case for invalid transaction with missing fields
def test_invalid_transaction_missing_fields():
    invalid_payload = valid_transaction()
    del invalid_payload["transaction_id"]  # Remove a required field
    event = {"Records": [{"kinesis": {"data": encode_payload(invalid_payload)}}]}

    response = decode_payload(valid_transaction_handler(event, None))['data']

    assert len(response) == 0


# Test case for invalid transaction with incorrect format
def test_invalid_transaction_incorrect_format():
    invalid_payload = valid_transaction()
    invalid_payload["transaction_id"] = "12345"  # Does not match regex
    event = {"Records": [{"kinesis": {"data": encode_payload(invalid_payload)}}]}

    response = decode_payload(valid_transaction_handler(event, None))['data']

    assert len(response) == 0


# Test case for multiple records
def test_multiple_transactions():
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(valid_transaction())}},
            {"kinesis": {"data": encode_payload(valid_transaction())}},
        ]
    }

    response = decode_payload(valid_transaction_handler(event, None))['data']

    assert len(response) == 2
    assert all(tx["status"] == Status.ok.value for tx in response)


def test_multiple_mix_transactions():
    invalid_payload = valid_transaction()
    invalid_payload["transaction_id"] = "12345"
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(valid_transaction())}},
            {"kinesis": {"data": encode_payload(valid_transaction())}},
            {"kinesis": {"data": encode_payload(invalid_payload)}},
        ]
    }

    response = decode_payload(valid_transaction_handler(event, None))['data']

    assert len(response) == 2


def test_output_is_json_serializable():
    """Lambda expects output to be serializable"""
    event = {
        "Records": [
            {"kinesis": {"data": encode_payload(valid_transaction())}},
        ]
    }

    response = decode_payload(valid_transaction_handler(event, None))['data']
    assert json.dumps(response)


# Test case for empty event
def test_empty_event():
    event = {"Records": []}
    response = valid_transaction_handler(event, None)
    assert response == {'data': []}
