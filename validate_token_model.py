from fastapi import Header, HTTPException, Depends
from token_model import Token

# Define a dependency to validate the authorization token
def validate_token(authorization: str = Header(None)):
    # Check if the Authorization header is provided
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract the token from the Authorization header
    token = authorization.split("Bearer ")[-1]
    
    # Validate the token format
    if not token.startswith("USER") or not token[4:].isdigit() or len(token) != 7:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # You can perform additional validation logic here if needed
    
    # Return the valid token
    return token
