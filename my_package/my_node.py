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
		self.stop_Time = self.start_Time + 60.0
		self.time_Remaining = 0 
		
		self.max_Speed = 0.4
		self.stop = 0.0
		self.turn_Angle = 0.7
		self.special_forward_turn_Angle = 0.8
		self.special_Case_Angle = 1.1	
		self.slow_Down = 0.35
		self.slow_Down_2 = 0.15
		self.extra_sensor_Threshold = 0.65
		self.sensor_Threshold = 0.65
		self.special_Case_Threshold = 0.55        
		self.special_Case_Threshold_side = 0.45
		
		
		
  						## calll back function for laserscan topic ##
  						
	def listener_callback(self, laser: LaserScan):   #laser is only a variable 
		
		msg = Twist()
		full_range = len(laser.ranges)
		
		self.start_Time = time.time()   # variable start time needs to update every loop to keep up with current time from import time library
		
		forward_rpl = laser.ranges[full_range//4]
		left_rpl = laser.ranges[(full_range//4)//2] 
		mid_left = laser.ranges[((full_range//4)//2)+((full_range//4)//4)]
		right_rpl = laser.ranges[int((full_range//2)*(3/4))]
		mid_right = laser.ranges[int((full_range//2)*(3/4))-((full_range//4)//4)]
		far_right_rpl = laser.ranges[int((full_range // 4)*1.75)]
		far_left_rpl = laser.ranges [((full_range//4)//2)//2]
		
	
									## stuck? stop and rotate 1.2 radians. 
		if ((forward_rpl < self.sensor_Threshold)and(mid_left < self.sensor_Threshold)and(mid_right < self.sensor_Threshold)and(left_rpl < self.special_Case_Threshold_side)and(right_rpl < self.special_Case_Threshold_side)):
			
			msg.linear.x = self.stop						
			msg.angular.z = -self.special_Case_Angle
			
						##   The only other case where speed is set to zero, if robot is too close to obstacle and rotaion angle while moving would not be ideal	
		elif ((forward_rpl < self.special_Case_Threshold)and(mid_left < self.special_Case_Threshold_side)or(mid_right < self.special_Case_Threshold_side)):
		
			
			msg.linear.x = self.stop
			msg.angular.z = -self.turn_Angle
		else:
						##   Forward_Beam  ## Addition of right and left values help determine better rotational angle
			if ((forward_rpl < self.extra_sensor_Threshold)and(left_rpl >= right_rpl)): 
					
					msg.linear.x = self.slow_Down								
					msg.angular.z = self.special_forward_turn_Angle
					
			elif ((forward_rpl < self.extra_sensor_Threshold)and(right_rpl >= left_rpl)):
			
					msg.linear.x = self.slow_Down								
					msg.angular.z = -self.special_forward_turn_Angle
					
						##   Left_Beam    ## Taking a right turn in this case should only happen when right side is not blocked
			elif ((left_rpl < self.sensor_Threshold)or(mid_left < self.special_Case_Threshold)) and ((right_rpl > left_rpl)or(mid_right > mid_left)): 				
				
					msg.linear.x = self.slow_Down
					msg.angular.z = self.turn_Angle
							
						##   Right_Beam  ## Taking a left turn in this case should only happen when left side is not blocked
			elif ((right_rpl < self.sensor_Threshold) or (mid_right < self.special_Case_Threshold)) and((left_rpl > right_rpl)or(mid_left > mid_right)):
				
					msg.linear.x = self.slow_Down
					msg.angular.z = -self.turn_Angle
			
			else:	
					msg.linear.x = self.max_Speed
					msg.angular.z = self.stop	
			
		self.cmd_pub_.publish(msg)
		
		if (self.start_Time <= self.stop_Time):             
			
			self.time_Remaining = self.stop_Time - self.start_Time
			self.get_logger().info(f"Time Remaining: { round (self.time_Remaining) }")
			#self.get_logger().info(f"Time Remaining: {}",format.round(self.time_Remaining))
			#self.get_logger().info("Working")
		else:
			self.get_logger().info("Job Done, Time Constraint achieved")
			rclpy.shutdown()
		
	
		
def main(args=None):
    rclpy.init(args=args)
    node = PubSubNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
  

		

