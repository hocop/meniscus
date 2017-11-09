##########################################################################
####			Meniscus processing tool
####			Made by Ruslan Baynazarov in 2017
####			hocop@yandex.ru, vk.com/ruslanbain
##########################################################################

import numpy as np
import cv2
from math import *
import time
from os import listdir
from os.path import isfile, join
from appJar import gui

path = 'input/'

onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
onlyfiles.sort()

# get info
f0 = onlyfiles[0]
time0 = int(f0[6:8])*3600 + int(f0[8:10])*60 + int(f0[10:12])
img = cv2.imread(path+f0)
imgHeight, imgWidth, c = img.shape

# init arrays
times = []
heights = []

# apriori values
top = 0
bottom = imgHeight
left = 0
right = imgWidth
maxBlack = 50
rot = 0

def process(f):
	# get time from filename
	time = 0
	try:
		time = int(f[6:8])*3600 + int(f[8:10])*60 + int(f[10:12]) - time0
	except:
		global curFileNum
		time = curFileNum
	
	# read image
	img = cv2.imread(path+f)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	# rotate
	rows,cols = img.shape
	ROTM = cv2.getRotationMatrix2D((cols/2,rows/2),rot,1)
	img = cv2.warpAffine(img,ROTM,(cols,rows))
	
	# remove not interesting domains
	img[:top,:] = maxBlack + 1 + img[:top,:] * 0
	img[bottom:,:] = maxBlack + 1 + img[bottom:,:] * 0
	img[:,:left] = maxBlack + 1 + img[:,:left] * 0
	img[:,right:] = maxBlack + 1 + img[:,right:] * 0
	
	# make mask
	mask = cv2.inRange(img, 0, maxBlack)
	mask = cv2.erode(mask,None,iterations=4)
	mask = cv2.dilate(mask,None,iterations=8)
	mask = cv2.erode(mask,None,iterations=4)
	
	# find contours
	v2,cont,h=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	# extract coordinate
	height = -1
	if len(cont) == 1:
		M = cv2.moments(cont[0])
		height = M['m10'] / M['m00']
	
	# draw
	img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		# green if ok, else red
	cv2.drawContours(img, cont, -1, (0,255,0)if len(cont)==1 else (0,0,255), 2)
	return img, time, height


# variables
curFileNum = 0
t, h = time0, -1

# button functions
def compAndShowLast():
	global t
	global h
	global curFileNum
	global top
	global bottom
	global left
	global right
	global maxBlack
	global rot
	top = app.getScale('Top')
	bottom = app.getScale('Bottom')
	left = app.getScale('Left')
	right = app.getScale('Right')
	maxBlack = app.getScale('Thresh')
	rot = app.getScale('Rot')
	
	img, t, h = process(onlyfiles[curFileNum])
	
	cv2.imshow('image', img)
	cv2.waitKey(30)

def press(button):
	global t
	global h
	global curFileNum
	global outfile
	if button == 'Submit':
		if h > 0:
			outfile.write('%f\t%f\n' % (t, h))
		else:
			outfile.write('%f\tnan\n' % t)
		curFileNum += 1
		if curFileNum == len(onlyfiles):
			exit()
	if button == 'Submit all':
		while True:
			press('Submit')
	if button == 'Skip':
		curFileNum += 1
	compAndShowLast()

# create window
app = gui('Meniscus processing', '400x400')

app.addLabel('title1','Set brightness threshold:')
app.addLabelScale("Thresh")
app.setScaleRange('Thresh', 0, 254, curr=None)
app.setScale('Thresh', maxBlack, callFunction=True)
app.setScaleChangeFunction('Thresh', press)
app.showScaleValue('Thresh',show=True)

app.addLabel('title2','Set rotation:')
app.addLabelScale("Rot")
app.setScaleRange('Rot', -90, 90, curr=None)
app.setScale('Rot', rot, callFunction=True)
app.setScaleChangeFunction('Rot', press)
app.showScaleValue('Rot',show=True)

app.addLabel('title3','Set margins:')

app.addLabelScale("Top")
app.setScaleRange('Top', 0, imgHeight, curr=None)
app.setScale('Top', top, callFunction=True)
app.setScaleChangeFunction('Top', press)

app.addLabelScale("Bottom")
app.setScaleRange('Bottom', 0, imgHeight, curr=None)
app.setScale('Bottom', bottom, callFunction=True)
app.setScaleChangeFunction('Bottom', press)

app.addLabelScale("Left")
app.setScaleRange('Left', 0, imgWidth, curr=None)
app.setScale('Left', left, callFunction=True)
app.setScaleChangeFunction('Left', press)

app.addLabelScale("Right")
app.setScaleRange('Right', 0, imgWidth, curr=None)
app.setScale('Right', right, callFunction=True)
app.setScaleChangeFunction('Right', press)

app.addButtons(['Skip','Submit','Submit all'], press)

# run
compAndShowLast()
outfile = open('output.txt','w')
outfile.write('time(sec)\theight(pixel)\n')
app.go()












