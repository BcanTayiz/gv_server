from fastapi import FastAPI, Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
# Define a dictionary to store request counts and timestamps
request_counts = {}
rate_limit = 4  # Requests per minute
client_ip = ''

# Shared rate limit tracking
rate_limits = defaultdict(lambda: {'count': 0, 'timestamp': datetime.now()})

def rate_limit_check(client_ip: str):
    global rate_limits

    current_time = datetime.now()
    client_rate_limit = rate_limits[client_ip]

    # Reset the rate limit count if the time window has passed
    if client_rate_limit['timestamp'] < current_time - timedelta(minutes=1):
        client_rate_limit['count'] = 0
        client_rate_limit['timestamp'] = current_time

    # Increment the count and check the rate limit
    client_rate_limit['count'] += 1
    if client_rate_limit['count'] > rate_limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")