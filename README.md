The program requires Python3 to run.

Design
The program makes use of an LRU cache for the caching portion and leaky bucket algorithm to implement rate-limitting.

You can update the global throttling limit in ip_to_country_server.py

Before running, please run:
- pip3 install flask

To run the server locally:
- python3 ip_to_country_server.py

To test out the API, make a HTTP GET request to http://localhost:8080/ip-to-country?ip=<IP>
For example: http://localhost:8080/ip-to-country?ip=8.8.8.8 will return 
{
	country_name: "United States"
}


To run e2e tests:
- python3 test/e2e_test.py

To run unit tests:
- python3 -m unittest
