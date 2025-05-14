# -*- coding: utf-8 -*-
# DESC: embedding client
# USAGE: python3 embedding_client.py

import requests
import json
import numpy as np


url = 'http://localhost:9523/generate'
data = {
    'text': '早上好呀' 
}
response = requests.post(url, data=json.dumps(data))
result = response.json()

print(f'type(result): {type(result)}')
print(f'np.array(result).shape: {np.array(result).shape}')
