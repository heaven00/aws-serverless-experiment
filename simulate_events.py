import boto3
import json
import random
from datetime import datetime, timedelta
import argparse

# Initialize a session using Amazon Kinesis
kinesis_client = boto3.client('kinesis', region_name='ca-central-1')

# Function to generate a random transaction
def generate_random_transaction(transaction_id):
    user_ids = ["U56789", "U12345", "U67890", "U98765"]
    device_types = ["mobile", "desktop", "tablet"]
    locations = ["California, USA", "Texas, USA", "New York, USA", "Florida, USA"]
    card_types = ["credit", "debit"]
    statuses = ["approved", "declined"]

    transaction = {
        "transaction_id": f"{datetime.now().strftime('%Y%m%d%H%M%S')}{transaction_id:05}",  # Combination of timestamp and incrementing number
        "user_id": random.choice(user_ids),
        "timestamp": (datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))).isoformat() + 'Z',
        "amount": round(random.uniform(1.0, 1000.0), 2),
        "device_type": random.choice(device_types),
        "location": random.choice(locations),
        "is_vpn": random.choice([True, False]),
        "card_type": random.choice(card_types),
        "status": random.choice(statuses)
    }
    
    return transaction

# Function to send a transaction to the Kinesis stream
def send_transaction_to_kinesis(transaction, stream_name):
    partition_key = str(transaction['user_id'])  # Use user_id as the partition key
    data = json.dumps(transaction).encode('utf-8')
    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data,
        PartitionKey=partition_key,
        StreamARN="arn:aws:kinesis:ca-central-1:294331937131:stream/294331937131-kinesis-stream"
    )
    return response

# Parse command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send simulated transaction events to a Kinesis Stream.")
    parser.add_argument("--stream-name", required=True, help="Name of the Kinesis Stream")
    parser.add_argument("--num-transactions", type=int, default=10, help="Number of transactions to send (default: 10)")
    
    args = parser.parse_args()
    
    stream_name = args.stream_name
    num_transactions = args.num_transactions
    
    # Simulate sending multiple transactions
    for i in range(num_transactions):
        transaction = generate_random_transaction(i)
        print(f"Sending transaction: {transaction}")
        response = send_transaction_to_kinesis(transaction, stream_name)
        print(f"Response from Kinesis: {response}")


# usage
# uv run python simulate_events.py --stream-name your-aws-account-id-kinesis-stream --num-transactions 10
