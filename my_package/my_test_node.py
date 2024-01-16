
#!/usr/bin/env python3
import rclpy 
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan # just like geometry we import laser
from enum import Enum



class PubSubNode(Node):
	def __init__(self):
	
		super().__init__("my_node")
		self.cmd_pub_ = self.create_publisher(Twist, '/cmd_vel', 10) ## twist is type of message data
		self.laser_sub_ = self.create_subscription(LaserScan,'/scan',self.listener_callback,10) ## laserscan is the type of message data
			
		
		self.msg = Twist()
		
		
		self.start_Time = time.time()
		self.stop_Time = self.start_Time + 60.0  #according to the time function format, 00.0 refers to seconds
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
		
		self.operation_Mode = 0
		
		
		## adding a level off abstraction ~~ two functions that would take an input argument such as direction and would set the appropriate values of x and z for twist message ~~
		
	class Speed_Direction_State(self, Enum):  # The seven modes refer to seven possible conditions or actions
		speed_Mode_One = 1
		speed_Mode_Two = 2
		speed_Mode_Three = 3 
		speed_Mode_Four = 4
		speed_Mode_Five = 5 
		speed_Mode_Six = 6
		speed_Mode_Seven = 7 
		
	def motion_Control(self,operation_Mode):	## Unfortinatily, match case (switch statement) is not in this version of python. 
	
		if self.operation_Mode == Speed_Direction_State.speed_Mode_One:
			
			self.msg.linear.x = self.stop
			self.msg.angular.z = -self.special_case_Angle
		
		elif self.operation_Mode == Speed_Direction_State.speed_Mode_Two:
		
			self.msg.linear.x = self.stop
			self.msg.angular.z = -self.turn_Angle
		
		elif self.operation_Mode == Speed_Direction_State.speed_Mode_Three:

			self.msg.linear.x = self.slow_Down								
			self.msg.angular.z = self.special_forward_turn_Angle
			
		elif self.operation_Mode == Speed_Direction_State.speed_Mode_Four:
		
			self.msg.linear.x = self.slow_Down								
			self.msg.angular.z = -self.special_forward_turn_Angle
		
		elif self.operation_Mode == Speed_Direction_State.speed_Mode_Five:
		
			self.msg.linear.x = self.slow_Downs
			self.msg.angular.z = self.turn_Angle
		
		elif self.operation_Mode == Speed_Direction_State.speed_Mode_Six:
		
			self.msg.linear.x = self.slow_Down
			self.msg.angular.z = -self.turn_Angle	
		
		else:
			
			self.msg.linear.x = self.max_Speed
			self.msg.angular.z = self.stop 
		
  						## calll back function for laserscan topic ##
  						
	def listener_callback(self, laser: LaserScan):   #laser is only a variable 
		
		
		full_range = len(laser.ranges)
		
		self.start_Time = time.time()   # variable start time needs to update every loop to keep up with current time from import time library
		
		forward_rpl = laser.ranges[full_range//4]
		left_rpl = laser.ranges[(full_range//4)//2] 
		mid_left = laser.ranges[((full_range//4)//2)+((full_range//4)//4)]
		right_rpl = laser.ranges[int((full_range//2)*(3/4))]
		mid_right = laser.ranges[int((full_range//2)*(3/4))-((full_range//4)//4)]
		far_right_rpl = laser.ranges[int((full_range // 4)*1.75)]
		far_left_rpl = laser.ranges [((full_range//4)//2)//2]
		
	
									## Stuck? stop and make a U-turn
		if ((forward_rpl < self.sensor_Threshold)and(mid_left < self.sensor_Threshold)and(mid_right < self.sensor_Threshold)and(left_rpl < self.special_Case_Threshold_side)and(right_rpl < self.special_Case_Threshold_side)):
			
			self.motion_Control(self.Speed_Direction_State.speed_Mode_One)
			
						##   The only other case where speed is set to zero, if robot is too close to obstacle and rotaion angle while moving would not be ideal	
		elif ((forward_rpl < self.special_Case_Threshold)and(mid_left < self.special_Case_Threshold_side)or(mid_right < self.special_Case_Threshold_side)):
		
			self.motion_Control(self.Speed_Direction_State.speed_Mode_Two)
			
		else:
						##   Forward_Beam  ## Addition of right and left values help determine better rotational angle
			if ((forward_rpl < self.extra_sensor_Threshold)and(left_rpl >= right_rpl)): 
					
					self.motion_Control(self.Speed_Direction_State.speed_Mode_Three)
					
					
			elif ((forward_rpl < self.extra_sensor_Threshold)and(right_rpl >= left_rpl)):
					
					self.motion_Control(self.Speed_Direction_State.speed_Mode_Four)
							
						##   Left_Beam    ## Taking a right turn in this case should only happen when right side is not blocked
			elif ((left_rpl < self.sensor_Threshold)or(mid_left < self.special_Case_Threshold)) and ((right_rpl > left_rpl)or(mid_right > mid_left)): 				
				
					self.motion_Control(self.Speed_Direction_State.speed_Mode_Five)
							
						##   Right_Beam  ## Taking a left turn in this case should only happen when left side is not blocked
			elif ((right_rpl < self.sensor_Threshold) or (mid_right < self.special_Case_Threshold)) and((left_rpl > right_rpl)or(mid_left > mid_right)):
				
					self.motion_Control(self.Speed_Direction_State.speed_Mode_Six)
								
			
			else:	
					self.motion_Control(self.Speed_Direction_State.speed_Mode_Seven)
							
		self.cmd_pub_.publish(self.msg)
		
		if (self.start_Time <= self.stop_Time):             
			
			self.time_Remaining = self.stop_Time - self.start_Time
			self.get_logger().info(f"Time Remaining: { round (self.time_Remaining) }")
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
  


