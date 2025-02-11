import random
import uuid
import pandas as pd
from datetime import datetime, timedelta

def generate_dummy_historic_data(
    total_users=100,
    fraction_one_time=0.3,
    max_txn_regular=5,
    fraud_baseline_prob=0.02,
    output_file="dummy_historic_data.csv"
):
    """
    Generates a CSV of dummy transactions with two user types:
      1. One-time users (exactly 1 transaction)
      2. Regular users (2 to max_txn_regular transactions)

    Columns:
      - user_id (string)
      - transaction_id (string)
      - timestamp (ISO format, ascending overall)
      - amount (float)
      - device_type (string)
      - location (string)
      - is_vpn (bool)
      - fraud (bool) ~2% baseline for example

    :param total_users: Total number of users in the dataset.
    :param fraction_one_time: Fraction of users that are one-time users.
    :param max_txn_regular: Maximum number of transactions for a regular user.
    :param fraud_baseline_prob: Baseline fraud probability (imbalance).
    :param output_file: Name of the output CSV file.
    """

    # Basic user distribution
    one_time_user_count = int(total_users * fraction_one_time)
    regular_user_count = total_users - one_time_user_count

    # Date range for the entire dataset
    start_date = datetime(2022, 1, 1)
    end_date   = datetime(2023, 12, 31)

    # We'll store all transactions in a list, then sort by timestamp at the end
    all_transactions = []

    # Possible categorical values
    device_types = ["desktop", "mobile", "tablet"]
    locations = [
        "California, USA",
        "New York, USA",
        "Texas, USA",
        "Ontario, Canada",
        "London, UK",
        "Berlin, Germany",
        "Tokyo, Japan"
    ]

    # 1) Generate transactions for one-time users
    for i in range(one_time_user_count):
        user_id = f"U{random.randint(10000,99999)}"

        # Assign a random date for this single transaction
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        random_seconds = random.randint(0, 24*60*60 - 1)
        txn_datetime = start_date + timedelta(days=random_days, seconds=random_seconds)

        transaction_id = "T" + str(uuid.uuid4())[:8].upper()
        amount = round(random.uniform(1.0, 1000.0), 2)
        device_type = random.choice(device_types)
        location = random.choice(locations)
        is_vpn = random.choice([True, False])
        fraud_flag = (random.random() < fraud_baseline_prob)  # Imbalanced fraud label

        all_transactions.append({
            "user_id": user_id,
            "transaction_id": transaction_id,
            "timestamp": txn_datetime,
            "amount": amount,
            "device_type": device_type,
            "location": location,
            "is_vpn": is_vpn,
            "fraud": fraud_flag
        })

    # 2) Generate transactions for regular users
    for i in range(regular_user_count):
        user_id = f"U{random.randint(10000,99999)}"

        # This user will have between 2 and max_txn_regular transactions
        num_txns = random.randint(2, max_txn_regular)

        # We'll pick a random "start" date for the first transaction,
        # and subsequent transactions will have increasing dates.
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        random_seconds = random.randint(0, 24*60*60 - 1)
        current_datetime = start_date + timedelta(days=random_days, seconds=random_seconds)

        for _ in range(num_txns):
            transaction_id = "T" + str(uuid.uuid4())[:8].upper()
            amount = round(random.uniform(1.0, 1000.0), 2)
            device_type = random.choice(device_types)
            location = random.choice(locations)
            is_vpn = random.choice([True, False])
            fraud_flag = (random.random() < fraud_baseline_prob)

            all_transactions.append({
                "user_id": user_id,
                "transaction_id": transaction_id,
                "timestamp": current_datetime,
                "amount": amount,
                "device_type": device_type,
                "location": location,
                "is_vpn": is_vpn,
                "fraud": fraud_flag
            })

            # Move current_datetime forward by at least 1 day for the next transaction
            # (random offset up to 30 days to simulate different intervals)
            offset_days = random.randint(1, 30)
            offset_seconds = random.randint(0, 24*60*60 - 1)
            current_datetime += timedelta(days=offset_days, seconds=offset_seconds)

            # Ensure we don't exceed the end_date
            if current_datetime > end_date:
                break

    # Sort transactions by timestamp so the entire dataset is in ascending order
    all_transactions.sort(key=lambda x: x["timestamp"])

    # Convert to a pandas DataFrame
    df = pd.DataFrame(all_transactions)

    # Convert timestamp to ISO format string
    df["timestamp"] = df["timestamp"].apply(lambda dt: dt.isoformat())

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Generated {len(df)} transactions (two user types) in '{output_file}'. "
          f"Approx. {100 * df['fraud'].mean():.2f}% labeled as fraud.")

if __name__ == "__main__":
    # Example usage
    generate_dummy_historic_data(
        total_users=100000,
        fraction_one_time=0.4,
        max_txn_regular=5000,
        fraud_baseline_prob=0.02,
        output_file="dummy_historic_data.csv"
    )
