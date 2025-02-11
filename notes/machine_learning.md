# The problem statement
We want to build a ML model that can detect fraudulent transactions in real-time, and the data we have for this is historical transaction data .i.e. past transactions that are known to be fruandulent or not.

Also, there are multiple kinds of fraudulent transactions possible such as credit card fraud, account theft, etc. Thus there wouldn't be a single model to fit all these scenarios, we would need multiple approaches to detect each type of fraud.

## Data Characteristics
- The data we have will be an imballanced set .i.e. there will be more non-fraudulent transactions than fraudulent ones.
```json
{
"transaction_id": "T12345",
"user_id": "U56789",
"timestamp": "2025-01-01T12:00:00Z",
"amount": 254.67,
"device_type": "mobile",
"location": "California, USA",
"is_vpn": false,
"card_type": "credit",
"status": "approved"
}
```

- Or create a cost function that penalizes wrongly predicted non-fraudulent transactions, not completely sure about it because then the users will have a hard time dealing with false positives.

## Key challenges
- Imbalanced data: Requires careful attention to sampling and evaluation metrics.
- Model inference must be efficient, with a minimal delay for the user.

## Validation Strategy
- Temporal Split of the data into train, test and validation set.
    - Train set: Oldest transactions
    - Validation set: Transaction right after the train set
    - Test set: Most recent transactions 

### Offline metrics
- Precision: out of all the predicted transactions how many were actually fraudulent?
- Recall: out of the actual fruadulent transactions how many did we catch?
- F1 Score: A good indicator of the balance between precision and recall.
- Cost based metric: we can create a custom metric that takes into account the amount of the missed fraud because that is direct loss to the business

### Online metrics
- Amount of money lost to fraud
- Number of calls made to customers who were called because they were flagged as fraudulent.
- Delay caused in transaction for the user due to the system
 

## Continuous Improvement & Deployment
- Its important to measure the model performance overtime and update it regularly, since there are new kind of frauds always coming in and might require new rules / models to be built.
- Retraining pipelines and performance comparison to older model to have a baseline to compare against and build a decomissioning strategy for the models.
- Performance monitoring and alerting system
- Monitoring segmented by location or another dimension that makes sense for better decision making. 

### Measuring the drift (how do you know the model needs retraining or innovation)
- Monitoring data change over time, if the underlying data distribution changes the model will become less useful. 
    - Distrubution metrics and anomaly detection over the distribution
- Performance metrics overtime
 

## Machine learning approaches

### 1. User transactions based anomaly Detection
Since the data is tied to a user, we can create a finger print of user based on spending amounts distribution, device types, locations, vpn usage, card type, etc.

Pros:
- Handles the data imbalance well and can cover multiple fraudulent scenarios.
- Is user centric which makes it easier to understand the fraud or provide reasoning

Cons:
- Will not work well for new users who have never made any transactions before.
- A lot of manual feature engineering
