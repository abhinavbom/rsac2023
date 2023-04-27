import boto3
from datetime import datetime, timezone, timedelta

# Connect to RDS client
rds = boto3.client('rds')

# Define the time threshold for identifying abandoned snapshots (default is 7 days ago)
cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)

# Get all RDS instances in the account
response = rds.describe_db_instances()

# Create a set of RDS instance identifiers
rds_instances = set(instance['DBInstanceIdentifier'] for instance in response['DBInstances'])

# Get all snapshots in the account
response = rds.describe_db_snapshots()

# Check each snapshot to see if it's abandoned and delete it if it is
for snapshot in response['DBSnapshots']:
    snapshot_time = snapshot['SnapshotCreateTime'].replace(tzinfo=timezone.utc)
    snapshot_age = datetime.now(timezone.utc) - snapshot_time
    if snapshot_age > cutoff_time and snapshot['Status'] == 'available' and snapshot['DBInstanceIdentifier'] not in rds_instances:
        print('Deleting abandoned snapshot:', snapshot['DBSnapshotIdentifier'])
        rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
