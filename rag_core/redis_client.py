import redis
import os
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.environ.get("REDIS_URL", "redis://:D6giPDZMb0wh6SWL5UtvwzD4pXTNUnRz@redis-11757.c263.us-east-1-2.ec2.cloud.redislabs.com:11757")
redis_client = redis.from_url(REDIS_URL)

keys = redis_client.keys("*")
print("Redis keys:", keys)

for k in keys:
    try:
        # Try to get the value as a list first
        values = redis_client.lrange(k, 0, -1)
        print(f"{k} (list): {values}")
    except redis.exceptions.ResponseError:
        try:
            # If it's not a list, try to get as a string
            value = redis_client.get(k)
            print(f"{k} (string): {value}")
        except redis.exceptions.ResponseError:
            # If it's neither list nor string, try other data types
            try:
                value = redis_client.hgetall(k)
                print(f"{k} (hash): {value}")
            except redis.exceptions.ResponseError:
                print(f"{k}: Could not determine data type or unsupported type")
