def hash_user_to_group(user_id: str) -> int:
    # Calculate the hash of the user ID
    user_hash = hash(user_id)
    # Map the hash to a group between 1-10 using modulo arithmetic
    group = (user_hash % 10) + 1
    return group
