import numpy
import base64
import uuid
from mxnet import nd, gluon, init, autograd
from mxnet.gluon import nn
from mxnet.gluon.data.vision import datasets, transforms
import matplotlib.pyplot as plt
from time import time
from mxnet.gluon.model_zoo import vision as models
from mxnet.gluon.utils import download
from mxnet import image
import time
import sys
import datetime
import subprocess
import sys
import os
import datetime
import traceback
import math
import random, string
import base64
import json
from time import gmtime, strftime
import mxnet as mx
import inception_predict
import numpy as np
import cv2
import math
import random, string
import time
import numpy
import random, string
import time
import psutil
import paho.mqtt.client as mqtt
from time import gmtime, strftime
start = time.time()
cap = cv2.VideoCapture(1)   # 0 - laptop   #1 - monitor

# http://gluon-crash-course.mxnet.io/predict.html
def transform(data):
    data = data.transpose((2,0,1)).expand_dims(axis=0)
    rgb_mean = nd.array([0.485, 0.456, 0.406]).reshape((1,3,1,1))
    rgb_std = nd.array([0.229, 0.224, 0.225]).reshape((1,3,1,1))
    return (data.astype('float32') / 255 - rgb_mean) / rgb_std


net = models.resnet50_v2(pretrained=True)


url = 'http://data.mxnet.io/models/imagenet/synset.txt'
fname = download(url)
with open(fname, 'r') as f:
    text_labels = [' '.join(l.split()[1:]) for l in f]

ret, frame = cap.read()
uuid = '{0}_{1}'.format(strftime("%Y%m%d%H%M%S",gmtime()),uuid.uuid4())
filename = 'images/gluon_image_{0}.jpg'.format(uuid)
cv2.imwrite(filename, frame)

x = image.imread(filename)
x = image.resize_short(x, 256)
x, _ = image.center_crop(x, (224,224))

prob = net(transform(x)).softmax()
idx = prob.topk(k=5)[0]
row = { }

#for i in idx:
#    i = int(i.asscalar())
#    print(i)
#    print('prob=%.5f, %s' % ( prob[0,i].asscalar() * 100, text_labels[i]))
try:
    end = time.time()
    row['top1pct'] = '{:.1f}'.format(prob[0,int(idx[0].asscalar())].asscalar()*100)
    row['top2pct'] = '{:.1f}'.format(prob[0,int(idx[1].asscalar())].asscalar()*100)
    row['top3pct'] = '{:.1f}'.format(prob[0,int(idx[2].asscalar())].asscalar()*100)
    row['top4pct'] = '{:.1f}'.format(prob[0,int(idx[3].asscalar())].asscalar()*100)
    row['top5pct'] = '{:.1f}'.format(prob[0,int(idx[4].asscalar())].asscalar()*100)
    row['top1'] = str(text_labels[int(idx[0].asscalar())])
    row['top2'] = str(text_labels[int(idx[1].asscalar())])
    row['top3'] = str(text_labels[int(idx[2].asscalar())])
    row['top4'] = str(text_labels[int(idx[3].asscalar())])
    row['top5'] = str(text_labels[int(idx[4].asscalar())])
    row['imgname'] = filename
    row['host'] = os.uname()[1]
    row['end'] = '{0}'.format( str(end ))
    row['te'] = '{0}'.format(str(end-start))
    row['battery'] = psutil.sensors_battery()[0]
    row['systemtime'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    row['cpu'] = psutil.cpu_percent(interval=1)
    usage = psutil.disk_usage("/")
    row['diskusage'] = "{:.1f} MB".format(float(usage.free) / 1024 / 1024)
    row['memory'] = psutil.virtual_memory().percent
    row['id'] = str(uuid)
    json_string = json.dumps(row)
    #print(json_string)
    # MQTT
    client = mqtt.Client()
    client.username_pw_set("user","pass")
    client.connect("server", 17769, 60)
    client.publish("gluon", payload=json_string, qos=0, retain=True)
except:
    print("{\"message\": \"Failed to run\"}")
