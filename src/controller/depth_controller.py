#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import UInt16
from std_msgs.msg import Bool
from bluerov_ros_playground.msg import Bar30
from bluerov_ros_playground.msg import Set_depth
from bluerov_ros_playground.msg import Set_target
#axis z goes up

g = 9.81  # m.s^-2 gravitationnal acceleration 
p0 = 990*100 #Pa surface pressure NEED to be cheked
rho = 1000 # kg.m^3  water density

class Depth_Control():
    def __init__(self, depth_desired=0, pwm_max=1550, pwm_neutral=1500, K=0, rosrate=4):
        #self.pub_arm = rospy.Publisher('/BlueRov2/arm', Bool, queue_size=10)
        #self.pub_rc3 = rospy.Publisher('/BlueRov2/rc_channel3/set_pwm', UInt16, queue_size=10)

        self.pub_pwm = rospy.Publisher('/Command/depth', UInt16, queue_size=10)
        rospy.Subscriber('/BlueRov2/bar30', Bar30, self._callback_bar30)

        self.rate = rospy.Rate(rosrate)
        self.depth_desired = depth_desired
        self.bar30_data = [0, 0, 0, 0] # [time_boot_ms, press_abs, press_diff, temperature]
        self.pwm_max = pwm_max
        self.pwm_neutral = pwm_neutral
        self.KI = 100
        self.KP = 600
        self.KD = 50

        self.time = 0
        self.depth = 0
        self.I_depth = 0
        
        rospy.Subscriber('/Settings/set_depth', Set_depth, self._callback_set_depth)
        rospy.Subscriber('/Settings/set_target', Set_target, self._callback_set_target)

    def _callback_bar30(self, msg):
	    self.bar30_data = [ msg.time_boot_ms,
        	                msg.press_abs,
        	                msg.press_diff,
        	                msg.temperature ]
        	                
    def _callback_set_depth(self, msg):
        if msg.pwm_max < 1500:
            self.pwm_max = 1500
        else:
            self.pwm_max = msg.pwm_max
        self.KI = msg.KI 
        self.KP = msg.KP 
        self.KD = msg.KD 

    def _callback_set_target(self, msg):
        self.depth_desired = msg.depth_desired

    def control_pid(self, p):
        depth  = -(p-p0)/(rho*g)
        delta_depth = depth - self.depth
        self.depth = depth
        delta_t = (self.bar30_data[0] - self.time)/1000.
        self.time = self.bar30_data[0]

        if delta_t == 0:
            D_depth = 0
        else:
            D_depth = delta_depth/delta_t

        self.I_depth = (self.depth_desired-depth)*delta_t
        u = self.KI*self.I_depth + self.KP*(self.depth_desired-depth) - self.KD*D_depth
        return u
	
    def saturation(self, pwm):
	    pwm_min = self.pwm_neutral - (self.pwm_max - self.pwm_neutral)
	    if pwm > self.pwm_max :
		    pwm = self.pwm_max
	    if pwm < pwm_min:
		    pwm = pwm_min
	    return int(pwm)

    def main(self):
        #pub_arm.publish(1)
        mesured_pressure = self.bar30_data[1]*100 #to convert pressure from hPa to Pa
        u = self.control_pid(mesured_pressure)
        pwm = 1500 + u
        pwm = self.saturation(pwm)
        #pub_rc3.publish(pwm)
        print("DESIRED_DEPTH : {}, PRESSURE_MESURED : {}, PWM : {}".format(self.depth_desired, mesured_pressure, pwm))
        self.pub_pwm.publish(pwm)

if __name__ == "__main__":
    rospy.init_node('depth_controller', anonymous=True)
    depth_control = Depth_Control()
    
    while not rospy.is_shutdown():
        depth_control.main()
        depth_control.rate.sleep()