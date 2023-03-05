import requests
import json

import subprocess
import time

def start_server():
    # Start the server as a subprocess
    server_process = subprocess.Popen(['python3', 'ip_to_country_server.py', '--testing'])

    # Wait for the server to start up
    time.sleep(1)

    return server_process


def stop_server(server_process):
    # Stop the server subprocess
    server_process.terminate()


def test_ip_to_country(server_process):

    # Test requesting the country for a valid IP
    response = requests.get('http://localhost:8080/ip-to-country', params={'ip': '8.8.8.8'})
    assert response.status_code == 200
    assert response.json()['country_name'] == 'United States'

    # Test requesting the country for an invalid IP
    response = requests.get('http://localhost:8080/ip-to-country', params={'ip': 'invalid'})
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid IP address'

    # Test high load but same request, so cache is used, no throttling
    for i in range(10):
        response = requests.get('http://localhost:8080/ip-to-country', params={'ip': '8.8.8.8'})
        assert response.status_code == 200
        assert response.json()['country_name'] == 'United States'

    # Test exceeding the rate limit for one vendor and falling back to the other
    for i in range(2):
        ip = '8.8.8.' + str(i)
        response = requests.get('http://localhost:8080/ip-to-country', params={'ip': ip})

    assert response.status_code == 200
    assert response.json()['country_name'] == 'United States'
    assert response.json()['vendor'] == 'vendor_2'

    # Test exceeding the rate limit for all vendors and returning an error
    for i in range(10):
        ip = '8.8.8.' + str(i)
        response = requests.get('http://localhost:8080/ip-to-country', params={'ip': ip})
    assert response.status_code == 500
    assert response.json()['error'] == 'Failed to get country name for IP address'


if __name__ == '__main__':
    server_process = start_server()
    try:
        test_ip_to_country(server_process)
    finally:
        stop_server(server_process)