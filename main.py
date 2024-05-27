from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio
import json
from collections import defaultdict
import time
import uvicorn

# Import your custom modules
from token_model import Token
from validate_token_model import validate_token
from hash_group import hash_user_to_group
from rate_limit import rate_limit_check, request_counts, rate_limits, rate_limit

app = FastAPI()

# Dictionary to store user visit counts per stream instance
user_visits = defaultdict(lambda: defaultdict(int))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific domain if needed
    allow_credentials=True,
    allow_methods=["*"],  # This will allow all methods including OPTIONS
    allow_headers=["*"],
)

async def stream_response(user_id, stream_id):
    hashed_integer = hash_user_to_group(user_id)
    for i in range(1, 5):  # Stream 5 responses
        # Increment visit count and stream sequence number for this stream instance
        user_visits[user_id][stream_id] += 1
        stream_seq = user_visits[user_id][stream_id]
        first_element = next(iter(rate_limits.values()))
        remaining_element = rate_limit - first_element['count']
        welcome_message = f"Welcome USER_{user_id}, this is your visit #{stream_seq}"
        response_data = {
            "message": welcome_message,
            "group": hashed_integer,
            "rate_limit": remaining_element,
            "stream_seq": stream_seq
        }
        yield f"data: {json.dumps(response_data)}\n\n"
        await asyncio.sleep(1)

@app.get('/')
async def root():
    return {'message': 'hello world'}

@app.post('/')
async def post():
    return {"message": "hello from post route"}

@app.get("/stream/")
async def read_items(request: Request, stream: bool, limit: Optional[int] = 10, offset: Optional[int] = 0, token: str = Depends(validate_token)):
    # Extract user ID from the token
    user_id = token.split("USER")[-1]
    client_ip_addr = request.client.host
    stream_id = id(request)  # Unique identifier for this stream instance
    
    if stream:
        rate_limit_check(client_ip_addr)
        return StreamingResponse(stream_response(user_id, stream_id), media_type="text/event-stream")
    else:
        return {"stream_seq": 0}

@app.post("/reset_rate_limit/")
async def reset_rate_limit(request: Request, token: str = Depends(validate_token)):
    client_ip_addr = request.client.host
    if client_ip_addr in rate_limits:
        rate_limits[client_ip_addr]['count'] = 0
        rate_limits[client_ip_addr]['reset_time'] = time.time() + 60  # Reset the rate limit window
        print(rate_limits)
    return {"message": "Rate limit has been reset"}

# Optional: Global error handling for rate limit exceeded
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)