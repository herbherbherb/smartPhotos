import requests
import json
import cv2

"""
Temporary client.py for week 1 of final assignment, this will be changed for following week
This is no longer used for week 2, it is here for testing purpose
"""

addr = 'http://localhost:5000'
test_url = addr + '/api/upload'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

img = cv2.imread('bike.jpg')
# encode image as jpeg
_, img_encoded = cv2.imencode('.jpg', img)
# send http request with image and receive response
response = requests.post(test_url, data=img_encoded.tostring(), headers=headers)
# decode response
print json.loads(response.text)

# expected output: {u'message': u'image received. size=124x124'}