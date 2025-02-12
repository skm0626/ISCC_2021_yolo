#!/usr/bin/python
#-*- encoding: utf-8 -*-

# video : /home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/9-2/origin_2021-9-2-13-41.avi
import cv2, rospy, time
import numpy as np
import math
import copy
from darknet_ros_msgs.msg import BoundingBox, BoundingBoxes
from sensor_msgs.msg import Image
from vision_distance.msg import Colorcone, ColorconeArray
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
from datetime import datetime
from SlidingWindow import SlidingWindow

bridge = CvBridge()
slidingwindow = SlidingWindow()
img = np.empty(shape=[0])

now = datetime.now()

center = np.array([288,480,1], np.float32)

up_left = [253,315]
up_right = [323,315]
down_left = [247,383]
down_right = [328,383]
corner_points_array = np.float32([up_left,up_right,down_left,down_right])

box_class = None
box_xmin = None
box_xmax = None
box_ymin = None
box_ymax = None

matrix_path = '/home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/matrix'
matrix = None
cone_pub = rospy.Publisher('color_cone', ColorconeArray, queue_size=10)

data_list = []

def image_callback(img_data):
	global bridge
	global img
	img = bridge.imgmsg_to_cv2(img_data, "bgr8")

# boundig_box callback
def bounding_callback(msg):
	global box_class, box_xmin, box_xmax, box_ymin, box_ymax
	global data_list
	global bounding_list
	global matrix
	bbox_num = len(msg.bounding_boxes)
	bbox = msg.bounding_boxes
	# yellow_lst = []
	# blue_lst = []
	# bounding_list = []
	if np.any(matrix) == None: return
	
	data_list = []

	for idx, box in enumerate(bbox):
		box_class = box.Class
		box_xmin = box.xmin
		box_xmax = box.xmax
		box_ymin = box.ymin
		box_ymax = box.ymax

		# blue(1), yellow(0)		
		cone_flag = 1
		if box_class == "yellow cone": cone_flag = 0

		'''
		cv2.circle(img,(box_xmin,box_ymin),5,(122,0,0),-1)
		cv2.circle(img,(box_xmax,box_ymin),5,(122,0,0),-1)
		cv2.circle(img,(box_xmin,box_ymax),5,(122,0,0),-1)
		cv2.circle(img,(box_xmax,box_ymax),5,(122,0,0),-1)		
		'''

		cone_x = (box_xmin+box_xmax)/2
		cone_y = box_ymax
		warp_cone = np.array([cone_x,cone_y,1], np.float32)
		warp_cone = np.matmul(np_matrix, warp_cone)
		warp_cone /= warp_cone[2]

		cone = Colorcone()
		cone.flag = cone_flag
		cone.x = warp_cone[0]
		cone.y = warp_cone[1]
		#cone.dist_x = distance[0]
		#cone.dist_y = distance[1]

		data_list.append(cone)
		#bounding_list.append([box_class])
		#print("Data_list", data_list)
		#print("data_list len", len(data_list))

	cone_array = ColorconeArray()
	cone_array.visions = data_list
	cone_pub.publish(cone_array)
	
# center_visualization
def check_center(image):
	cv2.circle(image,(288,240),5, (122,0,255),-1)
	return image
	



if __name__ == '__main__':
	global matrix
	#global data_list
	#global img
	rospy.init_node('warp')
	# Video 용 Subscriber
	image_sub = rospy.Subscriber("/videofile/image_raw/", Image, image_callback)
	# USB CAMERA 용 Subscriber	
	# image_sub = rospy.Subscriber("/usb_cam/image_raw/", Image, image_callback)
	
	#cap = cv2.VideoCapture("/home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/8-31/origin_2021-8-31-19-42.avi")
	bbox_sub = rospy.Subscriber("/darknet_ros/bounding_boxes/", BoundingBoxes, bounding_callback)
	
	#out = cv2.VideoWriter('/home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/9-2/origin_{}-{}-{}-{}-{}.avi'.format(now.year,now.month, now.day, now.hour, now.minute), cv2.VideoWriter_fourcc(*'MJPG'),30,(640,480))
	#out2 = cv2.VideoWriter('/home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/9-2/dot_origin_{}-{}-{}-{}-{}.avi'.format(now.year,now.month, now.day, now.hour, now.minute), cv2.VideoWriter_fourcc(*'MJPG'),30,(640,480))
	#out3 = cv2.VideoWriter('/home/foscar/ISCC_2021/src/vision_distance/src/ISCC_2021_Vision/yesun/9-2/warp_{}-{}-{}-{}-{}.avi'.format(now.year,now.month, now.day, now.hour, now.minute), cv2.VideoWriter_fourcc(*'MJPG'),30,(1000,850))
	rate = rospy.Rate(10)
	while not rospy.is_shutdown(): #cap.isOpened()
		#ret, img = cap.read()
		#img = cv2.resize(img, (640,480))
		#print(img.shape)
		#print(ret)
		if img.size != (640*480*3):
                    continue

		try:
			out.write(img)
		except:
			pass
		
		width = 1000
	    	height = 850
		
		new_data_list = []
		
		if len(data_list)>0:
			new_data_list = copy.deepcopy(data_list)
			#new_data_list = data_list.copy()
			print("new_data_list %%%%%%%%%%%%%% ", new_data_list)
		#else:
		#	continue
				
		
		# min sister's mapping points --> good
		#img_up_left = [450,650]#[220,150] #[400,600]
		#img_up_right = [550,650]#[420,150] #[600,600]
		#img_down_left = [450,750]#[220,350] #[600,800]
		#img_down_right = [550,750]#[420,350] #[400,800]
		
		# new mapping points --> test
		# img_up_left = [450,650]#[220,150] #[400,600]
		# img_up_right = [550,650]#[420,150] #[600,600]
		# img_down_left = [450,750]#[220,350] #[600,800]
		# img_down_right = [550,750]#[420,350] #[400,800]
		
		# new mapping points --> test2
		img_up_left = [475,675]#[220,150] #[400,600]
		img_up_right = [525,675]#[420,150] #[600,600]
		img_down_left = [475,725]#[220,350] #[600,800]
		img_down_right = [525,725]#[420,350] #[400,800]

		img_params = np.float32([img_up_left, img_up_right, img_down_left, img_down_right])

	    	# Compute and return the transformation matrix
	    	matrix = cv2.getPerspectiveTransform(corner_points_array, img_params)
		np_matrix = np.array(matrix)
		np.save(matrix_path, np_matrix)	
		# print(np_matrix)
	    	img_transformed = cv2.warpPerspective(img, matrix, (width, height))

		black_img = np.zeros((height, width, 3), np.uint8)
		#black_img_roi = black_img[200:850, 0:1000]

		if box_xmin==None or box_ymin==None or box_xmax==None or box_ymax==None: continue 

		xmin = float(box_xmin)
		ymin = float(box_ymin)
		xmax = float(box_xmax)
		ymax = float(box_ymax)

		warp_xymin = np.array([xmin,ymin,1], np.float32)
		warp_xymax = np.array([xmax,ymax,1], np.float32)

		warp_xymin = np.matmul(np_matrix,warp_xymin)
		warp_xymax = np.matmul(np_matrix,warp_xymax)
		warp_xymin /= warp_xymin[2]
		warp_xymax /= warp_xymax[2]

		img = check_center(img)
		# print('class name', box_class)

		cv2.circle(img,(up_left[0],up_left[1]),5,(255,0,0),-1)
		cv2.circle(img,(up_right[0],up_right[1]),5,(0,255,0),-1)
		cv2.circle(img,(down_left[0],down_left[1]),5,(0,0,255),-1)
		cv2.circle(img,(down_right[0],down_right[1]),5,(0,0,0),-1)

		cv2.circle(img, (box_xmin,box_ymin),5,(122,0,0),-1)
		cv2.circle(img,(box_xmax,box_ymin),5,(122,0,0),-1)
		cv2.circle(img,(box_xmin,box_ymax),5,(122,0,0),-1)
		cv2.circle(img,(box_xmax,box_ymax),5,(122,0,0),-1)

		cv2.circle(img, (288,480), 5, (255,0,0),-1 ) #center

		cv2.circle(img_transformed,(int(warp_xymin[0]),int(warp_xymin[1])),5,(122,122,0),-1)
		cv2.circle(img_transformed,(int(warp_xymin[0]),int(warp_xymax[1])),5,(122,122,0),-1)
		cv2.circle(img_transformed,(int(warp_xymax[0]),int(warp_xymin[1])),5,(122,122,0),-1)
		cv2.circle(img_transformed,(int(warp_xymax[0]),int(warp_xymax[1])),5,(122,122,0),-1)

		print("warp_xymin",warp_xymin)
		
		#yolo center visualization
		if (len(new_data_list) > 0):
			print("data_list**************", data_list)
			yellow_arr = []
			blue_arr = []
			print("len(new_data_list) :", len(new_data_list))
			
			yello_cnt = 0
			blue_cnt = 0
			
			for i in range (0,len(new_data_list)):
				print("i",i)
				print("data list i", new_data_list[i])
 
				if (new_data_list[i].flag == 0):
					yello_cnt+=1
					print("yello_cnt : ", yello_cnt)
					yellow_arr.append([new_data_list[i].flag, new_data_list[i].x, new_data_list[i].y])
					#print("yellow_arr", yellow_arr)
					cv2.circle(img_transformed,(int(new_data_list[i].x),int(new_data_list[i].y)),5,(0,122,122),-1)
				elif (new_data_list[i].flag == 1):
					blue_cnt+=1
					print("blue_cnt : ", blue_cnt)
					blue_arr.append([new_data_list[i].flag, new_data_list[i].x, new_data_list[i].y])	
					#print("blue_arr", blue_arr)
					cv2.circle(img_transformed,(int(new_data_list[i].x),int(new_data_list[i].y)),5,(0,122,122),-1)
				#print("cone_center", cone_center_x, cone_center_y)
			
			yellow_arr = sorted(yellow_arr, key=lambda x:(x[2],x[1],x[0]))
			print("sort_yellow", yellow_arr)
			blue_arr = sorted(blue_arr, key=lambda x:(x[2],x[1],x[0]))	
			print("sort_blue", blue_arr)
			
			
			# Default First Point
			left_point = np.array([70.18,520,1], np.float32) #[184.18,520,1]
			right_point = np.array([570.4,520,1], np.float32) #[389.4,520,1]
			warp_left_point = np.matmul(np_matrix, left_point)
			warp_left_point /= warp_left_point[2]
			warp_right_point = np.matmul(np_matrix, right_point)
			warp_right_point /= warp_right_point[2]

			if (len(yellow_arr) == 1):
				cv2.line(img_transformed,(int(warp_left_point[0]),int(warp_left_point[1])),(int(yellow_arr[len(yellow_arr)-1][1]),int(yellow_arr[len(yellow_arr)-1][2])),(255,0,0),15)
				cv2.line(black_img,(int(warp_left_point[0]),int(warp_left_point[1])),(int(yellow_arr[len(yellow_arr)-1][1]),int(yellow_arr[len(yellow_arr)-1][2])),(255,255,255),15)
			if (len(blue_arr) == 1):
				cv2.line(img_transformed,(int(warp_right_point[0]),int(warp_right_point[1])),(int(blue_arr[len(blue_arr)-1][1]),int(blue_arr[len(blue_arr)-1][2])),(255,0,0),15)
				cv2.line(black_img,(int(warp_right_point[0]),int(warp_right_point[1])),(int(blue_arr[len(blue_arr)-1][1]),int(blue_arr[len(blue_arr)-1][2])),(255,255,255),15)
			if (len(yellow_arr) >= 2):
				for j in range(0,len(yellow_arr)-1):
					cv2.line(img_transformed,(int(warp_left_point[0]),int(warp_left_point[1])),(int(yellow_arr[len(yellow_arr)-1][1]),int(yellow_arr[len(yellow_arr)-1][2])),(255,0,0),15)
					cv2.line(img_transformed,(int(yellow_arr[j][1]),int(yellow_arr[j][2])),(int(yellow_arr[j+1][1]),int(yellow_arr[j+1][2])),(255,0,0),15)
					cv2.line(black_img,(int(warp_left_point[0]),int(warp_left_point[1])),(int(yellow_arr[len(yellow_arr)-1][1]),int(yellow_arr[len(yellow_arr)-1][2])),(255,255,255),15)
					cv2.line(black_img,(int(yellow_arr[j][1]),int(yellow_arr[j][2])),(int(yellow_arr[j+1][1]),int(yellow_arr[j+1][2])),(255,255,255),15)
			if (len(blue_arr) >= 2):
				for j in range(0,len(blue_arr)-1):
					cv2.line(img_transformed,(int(warp_right_point[0]),int(warp_right_point[1])),(int(blue_arr[len(blue_arr)-1][1]),int(blue_arr[len(blue_arr)-1][2])),(0,255,0),15)
					cv2.line(img_transformed,(int(blue_arr[j][1]),int(blue_arr[j][2])),(int(blue_arr[j+1][1]),int(blue_arr[j+1][2])),(0,255,0),15)
					cv2.line(black_img,(int(warp_right_point[0]),int(warp_right_point[1])),(int(blue_arr[len(blue_arr)-1][1]),int(blue_arr[len(blue_arr)-1][2])),(255,255,255),15)
					cv2.line(black_img,(int(blue_arr[j][1]),int(blue_arr[j][2])),(int(blue_arr[j+1][1]),int(blue_arr[j+1][2])),(255,255,255),15)
			
			#print("warp_left_point:", warp_left_point)
			#print("warp_right_point:", warp_right_point)
			#('warp_left_point:', array([ 290.31703522,  886.70705631,    1.        ]))
			#('warp_right_point:', array([ 775.20601084,  886.70705631,    1.        ]))

			# left range
			cv2.circle(black_img,(200, 850),8,(255,0,255),-1)
			cv2.circle(black_img,(400, 850),8,(255,0,255),-1)
			cv2.circle(black_img,(200, 600),8,(255,0,255),-1)
			cv2.circle(black_img,(400, 650),8,(255,0,255),-1)
			# right range
			cv2.circle(black_img,(650, 850),8,(255,0,255),-1)
			cv2.circle(black_img,(850, 850),8,(255,0,255),-1)
			cv2.circle(black_img,(850, 600),8,(255,0,255),-1)
			cv2.circle(black_img,(650, 650),8,(255,0,255),-1)

		#out_img, left_roi, right_roi, x_location = slidingwindow.slidingwindow(black_img)

		#try:
		#	out2.write(img)
		#	out3.write(img_transformed)
		#except:
		#	pass
		
		# Draw Heading Arrow to warp image
		cv2.arrowedLine(img_transformed, (width//2, height),(width//2, 0), (0,255,235), thickness=1, tipLength=0.1)


    		#cv2.imshow("display", img)
		cv2.imshow("black_img : ", black_img)
    		cv2.imshow("warp", img_transformed)
       		#cv2.imshow('out_img', out_img)
       		#cv2.imshow('left_roi', left_roi)
       		#cv2.imshow('right_roi', right_roi)

		#if cv2.waitKey(1) & 0xFF == ord('q'):
		#	break    		
		cv2.waitKey(33)
		rate.sleep()

	cv2.destroyAllWindows()
