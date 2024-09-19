import requests
import time
import random

BASE_URL = "http://127.0.0.1:5000"
ENDPOINTS = ['/', '/fast', '/slow', '/error']

def generate_traffic():
    while True:
        endpoint = random.choice(ENDPOINTS)
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"Request to {endpoint}: Status {response.status_code}")
        except requests.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
        time.sleep(random.uniform(0.1, 1))  # Random delay between requests

if __name__ == "__main__":
    print("Starting to generate traffic...")
    generate_traffic()