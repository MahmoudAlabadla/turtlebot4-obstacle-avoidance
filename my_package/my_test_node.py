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
		
		forward_rpl = laser.ranges[full_range//4]
		left_rpl = laser.ranges[(full_range//4)//2] 
		mid_left = laser.ranges[((full_range//4)//2)+((full_range//4)//4)]
		right_rpl = laser.ranges[int((full_range//2)*(3/4))]
		mid_right = laser.ranges[int((full_range//2)*(3/4))-((full_range//4)//4)]
		far_right_rpl = laser.ranges[int((full_range // 4)*1.75)]
		far_left_rpl = laser.ranges [((full_range//4)//2)//2]
		
		max_Speed = 0.4
		stop = 0.0
		turn_Angle = 1.1
		special_Case_Angle = 1.2
		slow_Down = 0.35
		sensor_Threshold = 0.65
		special_Case_Threshold = 0.55
	
		## stuck? rotate 180 degrees. ## fix distance values after testing
		if ((forward_rpl < sensor_Threshold)and(mid_left < sensor_Threshold)and(mid_right < sensor_Threshold)):
			
			msg.linear.x = stop						
			msg.angular.z = -special_Case_Angle
			
		#elif ((forward_rpl < special_Case_Threshold)and(mid_left < sensor_Threshold)or(mid_right < sensor_Threshold)):
		
		#	msg.linear.x = stop
		#	msg.angular.z = -turn_Angle
			
		elif ((forward_rpl < special_Case_Threshold)and(left_rpl < sensor_Threshold)or(right_rpl < sensor_Threshold)):
		
			msg.linear.x = stop
			msg.angular.z = -turn_Angle
		else:
			##    Forward_Beam  ## Addition of right and left values help determine better rotational angle
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
  


