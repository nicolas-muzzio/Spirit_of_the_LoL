#Import needed packages
import pandas as pd
import requests

#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/

