from flask import Flask, request, Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
import jsonpickle
import numpy as np
import cv2
import sys
import json
import base64
from flask_cors import CORS
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
sys.path.insert(0, os.path.join(currentdir, "yolo")) # Hardcoding the directory that contains the .yolo definition
from init import classify, init_pred

"""
Python Flask server
For week 1, it only supports 1 POST method which allows users to upload the image and run object detection.
For week 2, it supports up to 4 API requests which allow user to upload images, get processed images, labels 
            make update to the existing labels.
For week 3, it supports gallery, query capabilities, login, register.
For week 4, it support delete image, image summary visualization, image sharing and the application is hosted on the cloud.
"""

# Initialize the Flask application
net = None
title_label = {}
app = Flask(__name__)
CORS(app)


client = MongoClient("mongodb://cs242:q123456@ds249583.mlab.com:49583/cs242")
db = client['cs242']
query = db.query
query.remove({})

# https://stackoverflow.com/questions/28776013/google-cloud-platform-cant-connect-to-mongodb
# https://stackoverflow.com/questions/31905966/gcloud-compute-list-networks-error-some-requests-did-not-succeed-insufficie

"""
Helper function that name the processed images
"""
def insert_dash(string):
    index = string.find('.')
    return './processed/' + string[:index] + '_processed' + string[index:]


# route http get to this method
# http://localhost:5000/api/label
# to get the stored labels given image name
@app.route('/api/label', methods=['GET'])
def get_label():
    global title_label
    image_name = request.args['name']
    label = ""
    if image_name in title_label:
        label = title_label[image_name]
    response = {'message': 'Image received', 'label': label}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/image
# to get the stored-processed image given image name
@app.route('/api/image', methods=['GET'])
def get_image():
    image_name = insert_dash(request.args['name'])
    img = cv2.imread(image_name)
    # encode image as jpeg
    _, img_encoded = cv2.imencode('.jpg', img)
    response = {'image': img_encoded.tostring()}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http put to this method
# http://localhost:5000/api/delete_image
# to delete an image if the user does not like it anymore
@app.route('/api/delete_image', methods=['GET']) 
def delete_image():
    global title_label
    login_name = request.args['login_name']
    image_name = request.args['image_name']
    myquery = { "origin": image_name }
    query.delete_one(myquery)

    response = {'message': 'Image Deleted'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# route http put to this method
# http://localhost:5000/api/label_change
# to change a stored labels given old label name
@app.route('/api/label_change', methods=['GET']) 
def change_label():
    global title_label
    old_name = request.args['old_name']
    new_name = request.args['new_name']
    username = request.args['username']

    if old_name in title_label:
        title_label.update({new_name: title_label[old_name]})

    os.rename('./processed/'+old_name, './processed/'+new_name) 
    os.rename(insert_dash(old_name), insert_dash(new_name))

    query.update(
            { "origin" : old_name },
            {'$set': { "origin": new_name}}
        )

    response = {'message': 'Label changed'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/init_image
# to get the stored origin image and its label given username
# post = {"username_image": username, "origin": filename}
@app.route('/api/init_image', methods=['GET'])
def init_image():
    global title_label
    username = request.args['username']

    cursor = query.find({'username_image': username})
    output = []
    ret = []
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    for cur in output:
        cur_res = {}
        filename = cur['origin'].encode('utf-8')
        image_name = './processed/'+filename[: filename.index(".")] + '.jpg'
        label = ""
        if filename in title_label:
            label = title_label[filename]
        img = cv2.imread(image_name)
        _, img_encoded = cv2.imencode('.jpg', img)
        cur_res['image'] = img_encoded.tostring()
        cur_res['label'] = label
        ret.append(cur_res)
    response = {'result': ret}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/get_summary
# to get labels summary to generate summary pie charts
# post = {login_name}
@app.route('/api/get_summary', methods=['GET'])
def get_summary():
    global title_label
    login_name = request.args['login_name']

    cursor = query.find({'username_image': login_name})
    output = []
    ret = {}
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    for cur in output:
        cur_res = {}
        filename = cur['origin'].encode('utf-8')
        label = []
        if filename in title_label:
            for label in title_label[filename].split(","):
                if label not in ret:
                    ret.update({label: 1})
                else:
                    ret[label] = ret[label] + 1
    response = {'result': ret}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/login
# to login an existing user account
@app.route('/api/login', methods=['GET'])
def login():
    global title_label
    username = request.args['username']
    password = request.args['password']

    cursor = query.find({'username': username})
    output = []
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    if len(output) == 0:
        response = {'message': "username"}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")

    if output[0]['password'] != password:
        response = {'message': "password"}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    

    cursor = query.find({'username_image': username})
    output_image = []
    ret = []
    while 1:
        try:
            record = cursor.next()
            output_image.append(record)
        except StopIteration:
            break
    for cur in output_image:
        cur_res = {}
        filename = cur['origin'].encode('utf-8')
        image_name = './processed/'+filename[: filename.index(".")] + '.jpg'
        img = cv2.imread(image_name)
        _, img_encoded = cv2.imencode('.jpg', img)
        cur_res['image'] = img_encoded.tostring()
        cur_res['title'] = filename[: filename.index(".")] + '.jpg'
        cur_res['label'] = title_label[filename]
        ret.append(cur_res)
    response = {'message': "yes", 'result': ret}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# route http get to this method
# http://localhost:5000/api/share_image
# to share images with other users
# post = {login_name, share_name, image_name}
@app.route('/api/share_image', methods=['GET'])
def share_image():
    global title_label
    login_name = request.args['login_name']
    share_name = request.args['share_name']
    image_name = request.args['image_name']
    
    cursor = query.find({'username': share_name})
    output = []
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    if len(output) == 0:
        response = {'message': "no"}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")

    post = {"login_name": login_name, "share_name": share_name, "image_name": image_name}
    query.insert_one(post)
    response = {'message': "yes"}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/get_shared_image
# get images that shared with me
# post = {login_name}
@app.route('/api/get_shared_image', methods=['GET'])
def get_shared_image():
    global title_label
    login_name = request.args['login_name']

    cursor = query.find({'share_name': login_name})
    output = []
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    if len(output) == 0:
        response = {'message': "no"}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    ret = []
    for cur in output:
        cur_res = {}
        filename = cur['image_name'].encode('utf-8')
        image_name = './processed/'+filename[: filename.index(".")] + '.jpg'
        img = cv2.imread(image_name)
        _, img_encoded = cv2.imencode('.jpg', img)
        cur_res['image'] = img_encoded.tostring()
        cur_res['title'] = filename[: filename.index(".")] + '.jpg'
        # myprint(cur_res['title'])
        cur_res['share_person'] = cur['login_name']
        ret.append(cur_res)
    response = {'message': "yes", 'result': ret}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http get to this method
# http://localhost:5000/api/register
# to register a new user account
@app.route('/api/register', methods=['GET'])
def register():
    username = request.args['username']
    password = request.args['password']

    cursor = query.find({'username': username})
    output = []
    while 1:
        try:
            record = cursor.next()
            output.append(record)
        except StopIteration:
            break
    if len(output) != 0:
        response = {'message': "no"}
        response_pickled = jsonpickle.encode(response)
        return Response(response=response_pickled, status=200, mimetype="application/json")


    post = {"username": username, "password": password}
    query.insert_one(post)
    
    response = {'message': "yes"}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# route http posts to this method
# http://localhost:5000/api/upload
@app.route('/api/upload', methods=['POST'])
def upload():
    global net
    global title_label    
    # reconstruct image as an numpy array
    rdata = json.loads(request.data)
    imgdata = base64.b64decode(rdata['image'])
    username = rdata['user']
    filename = rdata['name']
    # convert string of image data to uint8
    nparr = np.fromstring(imgdata, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    with open('./processed/' + filename, 'wb') as f:
        f.write(imgdata)

    labels_dup = classify(net, img, filename)
    label_set = set()
    for i in labels_dup:
        label_set.add(i)
    labels = list(label_set)
    title_label.update({filename: ','.join(labels)})
    post = {"username_image": username, "origin": filename}
    query.insert_one(post)
    # build a response dict to send back to client
    response = {'message': 'Image received', 'labels': labels, 'name': filename}
    # response = {'message': 'Image received'}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


# Dummy function for testing
@app.route('/')
def hello_world():
    return 'MyPhoto Application'

def myprint(target):
    divider = "========================================================"
    print(divider)
    print(target)
    print(divider)
# Initialize the classifier
def setup_app(app):
    global net
    net = init_pred()

setup_app(app)
    
if __name__ == '__main__':
    # start flask app
    # app.run(host="127.0.0.1", port=5000)
    app.run(host="0.0.0.0", port=5000)