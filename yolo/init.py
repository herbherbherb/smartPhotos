import os, sys, inspect
import random
import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import models
from resnet_yolo import resnet50
from yolo_loss import YoloLoss
from dataset import VocDetectorDataset
from eval_voc import evaluate
from predict import predict_image
from config import VOC_CLASSES, COLORS
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)

"""
Helper functinon that get called by server.py upon initilization
"""
# Source: https://github.com/xiongzihua/pytorch-YOLO-v1
def init_pred():
	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
	# YOLO network hyperparameters
	B = 2  # number of bounding box predictions per cell
	S = 14  # width/height of network output grid (larger than 7x7 from paper since we use a different network)
	# load_network_path = '/mnt/c/Users/herbe/CS242/fa18-cs242-final/yolo/best_detector.pth'
	load_network_path = '/home/herbertwangwrt/fa18-cs242-final/yolo/best_detector.pth'
	pretrained = True

	# use to load a previously trained network
	if load_network_path is not None:
	    # print('Loading saved network from {}'.format(load_network_path))
	    net = resnet50().to(device)
	    net.load_state_dict(torch.load(load_network_path, map_location=lambda storage, loc: storage))
	else:
	    # print('Load pre-trained model')
	    net = resnet50(pretrained=pretrained).to(device)
	batch_size = 24
	file_root_train = 'VOCdevkit_2007/VOC2007/JPEGImages/'
	annotation_file_train = currentdir + '/voc2007.txt'

	train_dataset = VocDetectorDataset(root_img_dir=file_root_train,dataset_file=annotation_file_train,train=True, S=S)
	train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True,num_workers=4)
	file_root_test = 'VOCdevkit_2007/VOC2007test/JPEGImages/'
	annotation_file_test = currentdir +  '/voc2007test.txt'

	test_dataset = VocDetectorDataset(root_img_dir=file_root_test,dataset_file=annotation_file_test,train=False, S=S)
	test_loader = DataLoader(test_dataset,batch_size=batch_size,shuffle=False,num_workers=4)

	net.eval()
	return net


"""
Helper function that name the processed images
"""
def insert_dash(string):
    index = string.find('.')
    return './processed/' + string[:index] + '_processed' + string[index:]

"""
Helper functinon that get called by server.py when an image need to be detected and cliassfied
"""
def classify(net, image, image_name):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	# height, width, channels = image.shape
	file_root_test = 'VOCdevkit_2007/VOC2007test/JPEGImages/'
	result = predict_image(net, image, root_img_directory=file_root_test)
	_labels = []
	for left_up, right_bottom, class_name, _, prob in result:
		_labels.append(class_name)
		color = COLORS[VOC_CLASSES.index(class_name)]
		cv2.rectangle(image, left_up, right_bottom, color, 2)
		label = class_name + str(round(prob, 2))
		text_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
		p1 = (left_up[0], left_up[1] - text_size[1])
		cv2.rectangle(image, (p1[0] - 2 // 2, p1[1] - 2 - baseline), (p1[0] + text_size[0], p1[1] + text_size[1]),
		              color, -1)
		cv2.putText(image, label, (p1[0], p1[1] + baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, 8)

	cv2.resize(image,(15,15))
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	cv2.imwrite(insert_dash(image_name), image)
	return _labels