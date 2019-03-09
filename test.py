import unittest
import requests
import jsonpickle
import json
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
sys.path.insert(0, os.path.join(currentdir, "yolo")) # Hardcoding the directory that contains the .yolo definition
from init import classify, init_pred
import cv2

net = None
"""
Test cases
"""
class TestInitMethods(unittest.TestCase):
	# Test case to init image classifer
	def test_a_net_eval(self):
		print(".Testing <test_a_net_eval>")
		net = init_pred()
		self.assertNotEqual(net, None)

	# Test case to classify images and check for returned labels
	def test_b_img_classify_1(self):
		print("Testing <test_b_img_classify_1>")
		net = init_pred()
		image_name = 'bike_2011.jpg'
		img = cv2.imread(image_name)
		labels = classify(net, img, image_name)
		self.assertEqual(len(labels), 4)
		self.assertFalse('car' in labels)
		self.assertTrue('bicycle' in labels)
		self.assertTrue('person' in labels)

	# Test case to classify images and check for returned labels
	def test_c_img_classify_2(self):
		print("Testing <test_c_img_classify_2>")
		net = init_pred()
		image_name = 'career_fair.jpg'
		img = cv2.imread(image_name)
		labels = classify(net, img, image_name)
		self.assertEqual(len(labels), 1)
		self.assertFalse('car' in labels)
		self.assertFalse('bicycle' in labels)
		self.assertTrue('person' in labels)

	# Test case to test API register function
	def test_d_API_register(self):
		print("Testing <test_d_API_register>")
		net = init_pred()
		username = "herb"
		password = "12345"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/register'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "yes")

		username = "herb"
		password = "098764321"
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "no")

		username = "Daniel"
		password = "098764321"
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "yes")

	# Test case to test API login function after registration
	def test_e_API_login(self):
		print("Testing <test_e_API_login>")
		net = init_pred()
		addr = 'http://localhost:5000'
		test_url = addr + '/api/login'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		username = "random_password"
		password = "12345"
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "username")

		# send http request with image and receive response
		username = "herb"
		password = "0987654321"
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "password")

		# send http request with image and receive response
		username = "herb"
		password = "12345"
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "yes")
		
	# Test case to test API upload function, to upload images correctly
	def test_f_API_upload(self):
		print("Testing <test_f_API_upload>")
		net = init_pred()
		image_name = 'bike_2011.jpg'
		img = cv2.imread(image_name)
		username = "herb"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/upload'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		img_str = cv2.imencode('.jpg', img)[1].tostring()
		# send http request with image and receive response
		data = json.dumps({'image': img_str.encode('base64'), 'user': username, 'name': image_name})
		r = requests.post(test_url, data=data, headers=headers)
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "Image received")
		self.assertTrue(response['name'] == image_name)
		self.assertTrue("person" in response['labels'])
		self.assertTrue("bicycle" in response['labels'])

		password = "12345"
		test_url = addr + '/api/login'
		PARAMS = {'username':username, 'password': password} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertEqual(len(response['result']), 1)

	# Test case to test API get_label function, check returned labels
	def test_g_API_get_label(self):
		print("Testing <test_g_API_get_label>")
		net = init_pred()
		image_name = 'bike_2011.jpg'
		
		addr = 'http://localhost:5000'
		test_url = addr + '/api/label'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'name':image_name} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['label'] == "person,bicycle")

	# Test case to test API get_image function, make sure the right image is returned
	def test_h_API_get_image(self):
		print("Testing <test_h_API_get_image>")
		net = init_pred()
		image_name = 'bike_2011.jpg'
		img = cv2.imread(image_name)
		img_str = cv2.imencode('.jpg', img)[1].tostring().encode('base64')
		addr = 'http://localhost:5000'
		test_url = addr + '/api/image'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'name':image_name} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['image']['py/b64'][0:10] == img_str[0:10])

	# Test case to test API change_label function, make sure the label is changed
	def test_i_API_change_label(self):
		print("Testing <test_i_API_change_label>")
		net = init_pred()
		image_name = 'bike_2011.jpg'
		new_name = 'bike.jpg'
		username = "herb"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/label_change'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'old_name':image_name, 'new_name': new_name, 'username': username} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "Label changed")

	# Test case to test API get_summary function, make sure returned format is right
	def test_j_API_get_summary(self):
		print("Testing <test_j_API_get_summary>")
		username = "herb"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/get_summary'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'login_name':username} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue("person" in response['result'])
		self.assertTrue("bicycle" in response['result'])
		self.assertEqual(response['result']['person'], 1)
		self.assertEqual(response['result']['bicycle'], 1)
		
	# Test case to test API share_image function, make sure right image is shared
	def test_k_API_share_image(self):
		print("Testing <test_k_API_share_image>")
		login_name = "herb"
		share_name = "Daniel"
		fake_share_name = "Wrong_Daniel"
		image_name = "bike.jpg"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/share_image'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'login_name':login_name, 'share_name': share_name, 'image_name': image_name} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == 'yes')

	# Test case to test API get_shared_image function, make sure right information is returned
	def test_l_API_get_shared_image(self):
		print("Testing <test_l_API_get_shared_image>")
		login_name = "Daniel"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/get_shared_image'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'login_name':login_name} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(len(response['result']) == 1)
		self.assertTrue(response['result'][0]['share_person'] == 'herb')
		self.assertTrue(response['result'][0]['title'] == 'bike.jpg')

	# Test case to test API delete_image function, make sure right image is deleted
	def test_m_API_get_delete_image(self):
		print("Testing <test_m_API_get_delete_image>")
		login_name = "herb"
		image_name = "bike.jpg"
		addr = 'http://localhost:5000'
		test_url = addr + '/api/delete_image'

		# prepare headers for http request
		headers = {'content-type': 'application/json'}

		# send http request with image and receive response
		PARAMS = {'login_name':login_name, 'image_name': image_name} 
		r = requests.get(url = test_url, params = PARAMS) 
		response = json.loads(r.content)
		self.assertTrue(response['message'] == "Image Deleted")

if __name__ == '__main__':
    unittest.main()