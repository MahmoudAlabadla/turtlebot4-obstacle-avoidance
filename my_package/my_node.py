#!/usr/bin/env python3
import rclpy 
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan # just like geometry we import laser

class PubSubNode(Node):
	def __init__(self):
		super().__init__("my_node")
		self.cmd_pub_ = self.create_publisher(Twist, '/cmd_vel', 10)
		self.laser_sub_ = self.create_subscription(LaserScan,'/scan',self.listener_callback,10)
		
	def listener_callback(self, laser: LaserScan):   #laser is only a variable 
		msg = Twist()	
		full_range = len(laser.ranges)
		if (laser.ranges[full_range//4] > 0.85):
				msg.linear.x = 0.5
				#msg.angular.z = 0.0
			else:
				msg.linear.x = 0.5
				msg.angular.z = 1		
		
		#msg.angular.z = 0.0
		self.cmd_pub_.publish(msg)
		
		# Next step is to get 1 value in the direction directly forward to the robot and then 
		# move right or left to not hit any obstacles.

def main(args=None):
    rclpy.init(args=args)
    node = PubSubNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
  

