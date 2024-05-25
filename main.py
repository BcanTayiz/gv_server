from fastapi import FastAPI
from typing import Optional
from token_model import Token
from fastapi import Header, HTTPException, Depends,Request
from validate_token_model import validate_token
from fastapi.responses import JSONResponse
from typing import Annotated
from hash_group import hash_user_to_group
from rate_limit import rate_limit_check,request_counts,rate_limits,client_ip,rate_limit
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime, timedelta
import json
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware
import time

# Dictionary to store user visit counts per stream instance
user_visits = defaultdict(lambda: defaultdict(int))



app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific domain if needed
    allow_credentials=True,
    allow_methods=["*"],  # This will allow all methods including OPTIONS
    allow_headers=["*"],
)

# for security the origins and headers could be changed



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
    return {'message':'hello world'}

@app.post('/')
async def post():
    return {"message":"hello from post route"}

@app.get("/stream/")
async def read_items(request: Request, stream: bool, limit: Optional[int] = 10, offset: Optional[int] = 0, token: str = Depends(validate_token)):
    # Extract user ID from the token
    user_id = token.split("USER")[-1]
    client_ip = request.client.host
    stream_id = id(request)  # Unique identifier for this stream instance
    
    if stream is True:
        rate_limit_check(client_ip)
        return StreamingResponse(stream_response(user_id, stream_id), media_type="application/json")
    elif stream is False:
        return {"stream_seq": 0}
    
@app.post("/reset_rate_limit/")
async def reset_rate_limit( request: Request,token: str = Depends(validate_token)):
    client_ip = request.client.host
    if client_ip in rate_limits:
        rate_limits[client_ip]['count'] = 0
        rate_limits[client_ip]['reset_time'] = time.time() + 60  # Reset the rate limit window
        print(rate_limits)
    return {"message": "Rate limit has been reset"}  
   


# Optional: Global error handling for rate limit exceeded
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})