import time
import sys
import requests
import yaml
import os
import logging
from datetime import date
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import chromadb

client = chromadb.Client()
#client = chromadb.PersistentClient(path="./Chroma")