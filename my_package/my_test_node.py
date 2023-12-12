#!/usr/bin/env python3
import rclpy 
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan # just like geometry we import laser

class PubSubNode(Node):
	def __init__(self):
	
		super().__init__("my_node")
		self.cmd_pub_ = self.create_publisher(Twist, '/cmd_vel', 10) ## twist is type of message data
		self.laser_sub_ = self.create_subscription(LaserScan,'/scan',self.listener_callback,10) ## laserscan is the type of message data
				
		
		
		self.start_Time = time.time()
		self.end_Time = self.start_Time + 00.01
		self.count = 0
		

		
  ## calll back function for laserscan topic ##
	def listener_callback(self, laser: LaserScan):   #laser is only a variable 
		
		msg = Twist()
		full_range = len(laser.ranges)
		max_Speed = 0.4
		stop = 0.0
		turn_Angle = 1.0
		special_Case_Angle = 1.1
		slow_Down = 0.35
		sensor_Threshold = 0.65
		special_Case_Threshold = 0.45
		special_Case_Threshold_side = 0.55
		self.count = self.count + 1
		
		forward_rpl = laser.ranges[full_range//4]
		left_rpl = laser.ranges[(full_range//4)//2] 
		mid_left = laser.ranges[((full_range//4)//2)+((full_range//4)//4)]
		right_rpl = laser.ranges[int((full_range//2)*(3/4))]
		mid_right = laser.ranges[int((full_range//2)*(3/4))-((full_range//4)//4)]
		far_right_rpl = laser.ranges[int((full_range // 4)*1.75)]
		far_left_rpl = laser.ranges [((full_range//4)//2)//2]
		
	
		## stuck? stop and rotate 1.2 radians. 
		if ((forward_rpl < sensor_Threshold)and(mid_left < sensor_Threshold)and(mid_right < sensor_Threshold)):
			
			msg.linear.x = stop						
			msg.angular.z = -special_Case_Angle
			
		## the only other case where speed is set to zero, if robot is too close to obstacle and rotaion angle while moving would not be ideal	
		elif ((forward_rpl < special_Case_Threshold)and(left_rpl < special_Case_Threshold_side)or(right_rpl < special_Case_Threshold_side)):
		
			msg.linear.x = stop
			msg.angular.z = -turn_Angle
		else:
			##Forward_Beam  ## Addition of right and left values help determine better rotational angle
			if ((forward_rpl < sensor_Threshold)and(left_rpl >= right_rpl)): 
					
					msg.linear.x = slow_Down								
					msg.angular.z = turn_Angle
					
			elif ((forward_rpl < sensor_Threshold)and(right_rpl > left_rpl)):
			
					msg.linear.x = slow_Down								
					msg.angular.z = -turn_Angle
					
			##   Left_Beam    ## Taking a right turn in this case should only happen when right side is not blocked
			elif ((left_rpl < sensor_Threshold)or(mid_left < sensor_Threshold)) and ((right_rpl > left_rpl)or(mid_right > mid_left)): 
					
					msg.linear.x = slow_Down
					msg.angular.z = turn_Angle
							
			##   Right_Beam  ## Taking a left turn in this case should only happen when left side is not blocked
			elif ((right_rpl < sensor_Threshold) or (mid_right < sensor_Threshold)) and((left_rpl > right_rpl)or(mid_left > mid_right)):
					
					msg.linear.x = slow_Down
					msg.angular.z = -turn_Angle
			
			else:	
					msg.linear.x = max_Speed
					msg.angular.z = stop	
			
	#	self.logger()info("publishing")
		self.cmd_pub_.publish(msg)
		
		#if (self.start_Time <= self.end_Time):
		if (self.count <= 60*10):              ## the value 60*10 is a little over 1 minute // change for better accuracy

			self.get_logger().info("publishing")        ## testing for if statemetn
		else:
			rclpy.shutdown("job done")
		
# we can add another subscriber into the same node here

		
		
def main(args=None):
    rclpy.init(args=args)
    node = PubSubNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
  


