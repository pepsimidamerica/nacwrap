import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from nacwrap import connections_list, datasource_connectors_list, datasources_list

res = connections_list()
res2 = datasources_list()
res3 = datasource_connectors_list()

pass
