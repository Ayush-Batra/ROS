#!/usr/bin/env python

import rospy
import time
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu



class husky():

    def __init__(self):
        self.counter = 0
        self.target_x = 0.25
        self.kp = 1
        self.ki = 0.5
        self.kd = 0.002
        self.prop = 0
        self.integeral = 0
        self.diff = 0
        self.current_x = 0
        self.sum_error = 0
        self.change_error = 0
        self.last_error = 0
        self.current_time = rospy.get_time()
        self.previous_time = rospy.get_time()
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1) 
        self.sub_odom = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.sub_imu = rospy.Subscriber('imu', Imu, self.imu_callback)
        self.rate = rospy.Rate(1)
        self.move = Twist()
    def odom_callback(self, msg):
        self.loc = msg
        self.current_x = self.loc.pose.pose.position.x
        print ("pose x = " + str(self.loc.pose.pose.position.x))
        print ("pose y = " + str(self.loc.pose.pose.position.y))
        print ("orientacion x = " + str(self.loc.pose.pose.orientation.x))
        print ("orientacion y = " + str(self.loc.pose.pose.orientation.y))
        self.rate.sleep()
    def imu_callback(self,msg):
       self.speed  =  msg
       print ("imu data --->\n veloc angular z = " + str(self.speed.angular_velocity.z))
       print ("aceleracion linear x = " + str(self.speed.linear_acceleration.x))
       print ("aceleracion linear y = " + str(self.speed.linear_acceleration.y))
       self.rate.sleep()
    def controller(self):
        self.current_time = rospy.get_time()
        elapsed_time = (self.current_time - self.previous_time)/1000
        print("time",elapsed_time)
        error = self.target_x - self.current_x
        self.sum_error = self.sum_error + (error*elapsed_time)
        self.change_error = (error - self.last_error)/elapsed_time
        print("last_error", self.last_error)
        print("error", error)
        print("sum_error", self.sum_error)
        print("change", self.change_error)
        if(error < 0.01):
            self.move.linear.x = 0
            self.pub.publish(self.move)         
        else:  
            print("final position",self.target_x)
            print("current position",self.current_x)
            self.prop = (self.kp)*error
            self.integeral = ((self.ki)*self.sum_error)
            self.diff = ((self.kd)*self.change_error)
            total = self.prop + self.integeral + self.diff
            self.move.linear.x = total
            self.pub.publish(self.move)
            self.rate.sleep()
        self.previous_time = self.current_time
        self.last_error = error
if __name__ == '__main__':
    rospy.init_node('husky_dead_reck')
    try:
       a = husky()
       while not rospy.is_shutdown():
           a.controller()
    except rospy.ROSInterruptException: pass
    rospy.spin()
