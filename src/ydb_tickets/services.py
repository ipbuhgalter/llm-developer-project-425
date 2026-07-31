import uuid
import time

def get_uuid():
    return str(uuid.uuid4())

def get_time():
    return int(time.time())
