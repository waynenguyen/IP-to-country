import threading
import time
from functools import wraps

from flask import Flask, jsonify, request
import requests
from lru_cache import LRUCache
from leaky_bucket import LeakyBucket
import socket
import argparse


app = Flask(__name__)

# Configure rate limit values (requests per hour) for each vendor
RATE_LIMITS = {
    "vendor_1": 1,
    "vendor_2": 2,
}

# Configure cache size limit
CACHE_SIZE_LIMIT = 10000

# ipstack acccess key
IPSTACK_ACCESS_KEY = "84e5292c775ca89da9527c60a178ad43"

TESTING_ENABLED = False

cache = LRUCache(CACHE_SIZE_LIMIT)


# Define rate limit buckets for each vendor
rate_limit_buckets = {
    vendor: LeakyBucket(rate_limit) for vendor, rate_limit in RATE_LIMITS.items()
}

# Define rate limiting decorator
def rate_limit(vendor):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bucket = rate_limit_buckets[vendor]
            if not bucket.acquire():
                raise RateLimitError(f"Rate limit exceeded for {vendor}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Define custom exception for rate limit errors
class RateLimitError(Exception):
    pass



@rate_limit("vendor_1")
def get_country_name_vendor_1(ip_address):
    response = requests.get(f"https://ipapi.co/{ip_address}/country_name/")
    if response.status_code != 200:
        raise ValueError(f"Failed to get country name for {ip_address} from vendor 1")
    return response.text.strip()

# Define vendors for IP location lookup
@rate_limit("vendor_2")
def get_country_name_vendor_2(ip_address):
    response = requests.get(f"http://api.ipstack.com/{ip_address}?access_key={IPSTACK_ACCESS_KEY}")
    if response.status_code != 200:
        raise ValueError(f"Failed to get country name for {ip_address} from vendor 2")
    data = response.json()
    if "country_name" not in data:
        raise ValueError(f"Failed to get country name for {ip_address} from vendor 2")
    return data["country_name"]


def is_valid_ip_address(ip_address: str) -> bool:
    try:
        socket.inet_pton(socket.AF_INET, ip_address)
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip_address)
        except socket.error:
            return False
        return True
    return True

@app.route("/ip-to-country")
def ip_to_country():
    ip_address = request.args.get("ip")
    if ip_address is None:
        return jsonify(error="IP address not provided"), 400

    if not is_valid_ip_address(ip_address):
        return jsonify(error="Invalid IP address"), 400
    # Check cache first
    country_name = cache.get(ip_address)
    if country_name is not None:
        return jsonify(country_name=country_name)

    error_msg = ""
    # Try vendors in order until a successful response is received
    for vendor in ["vendor_1", "vendor_2"]:
        try:
            country_name = globals()[f"get_country_name_{vendor}"](ip_address)
            cache.put(ip_address, country_name)
            if TESTING_ENABLED:
                return jsonify(country_name=country_name,vendor=vendor)
            return jsonify(country_name=country_name)
        except RateLimitError as e:
            # Rate limit exceeded for this vendor, try the next one
            print(e)

        except Exception as e:
            # Error occurred, log and try the next vendor
            print(e)

    # If all vendors failed, return error
    return jsonify(error="Failed to get country name for IP address"), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--testing', action='store_true')
    args = parser.parse_args()

    TESTING_ENABLED = args.testing
    app.run(host='0.0.0.0', port=8080, debug=True)