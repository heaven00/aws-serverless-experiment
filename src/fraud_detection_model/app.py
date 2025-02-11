import json
import random


def categorize_transaction(probability):
    """Categorize transactions based on fraud probability."""
    if probability >= 0.7:
        return "Rejected"
    elif probability >= 0.4:
        return "Flagged"
    else:
        return "Approved"


def classify_transaction(event, _):
    """AWS Lambda function to process transactions, predict fraud, and store results in S3."""
    prediction = {
        "classification": random.choice(['Approved', 'Flagged', 'Rejected']),
        "probability": round(random.uniform(0.1, 1), 2)
    }
    return {
        "statusCode": 200,
        "body": json.dumps({
            "prediction": prediction,
            "event": event
        }),
        
    }