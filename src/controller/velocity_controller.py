#!/usr/bin/env python

import rospy
import time
import scipy.integrate
import matplotlib.pyplot as plt
from std_msgs.msg import String
from std_msgs.msg import UInt16
from std_msgs.msg import Bool
from sensor_msgs.msg import Imu
from bluerov_ros_playground.msg import Set_velocity
from bluerov_ros_playground.msg import Set_target

class Velocity_Control():
    def __init__(self, velocity_desired=1, pwm_max=1500, pwm_neutral=1500, KP=100, KD=25, rosrate=10):
        self.pub_pwm = rospy.Publisher('/Command/velocity', UInt16, queue_size=10)
        rospy.Subscriber('/imu/data_raw', Imu, self._callback_imu_data)
        self.rate = rospy.Rate(rosrate)

        self.velocity_desired = velocity_desired
        self.imu_data = [0, 0, 0] 
        self.pwm_max = pwm_max
        self.pwm_neutral = pwm_neutral
        self.KP = KP
        self.KD = KD
        self.speedX = 0
        self.accX = [0, 0]
        self.t0 = rospy.get_time()
    
        plt.ion()
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)
        rospy.Subscriber('/Settings/set_velocity', Set_velocity, self._callback_set_vel)
        rospy.Subscriber('/Settings/set_target', Set_target, self._callback_set_target)
        
    def _callback_imu_data(self, msg):
        self.imu_data = [msg.linear_acceleration.x,
                         msg.linear_acceleration.y,
                         msg.linear_acceleration.z]
        self.accX[0] = self.accX[1]
        self.accX[1] = self.imu_data[0]

    def _callback_set_vel(self, msg):
        if msg.pwm_max < 1500:
            self.pwm_max = 1500
        else:
            self.pwm_max = msg.pwm_max
        self.KP = msg.KP 
        self.KD = msg.KD 

    def _callback_set_target(self, msg):
        self.velocity_desired = msg.velocity_desired

    def velocity(self):
        self.speedX = self.speedX + scipy.integrate.trapz(self.accX, dx=0.02)
        print("SPEED : {}".format(self.speedX))
        self.ax.plot(rospy.get_time()-self.t0, self.accX[1], "+b")
        self.ax.plot(rospy.get_time()-self.t0, self.speedX, "+g")
        plt.pause(0.01)

    def control(self):
        #u = self.KP*(self.velocity_desired-self.speedX) - self.KD*self.accX[1]
        u = self.pwm_max-50
        print(u)

        return u

    def saturation(self, pwm):
        pwm_min = self.pwm_neutral - (self.pwm_max - self.pwm_neutral)
        if pwm > self.pwm_max :
            pwm = self.pwm_max
        if pwm < pwm_min:
            pwm = pwm_min
        return int(pwm)

    def main(self):
        self.velocity() #estimation of the seed along X axis
        u = self.control()
        pwm = 1500 + u 
        pwm = self.saturation(pwm)
        self.pub_pwm.publish(pwm)
        print("VELOCITY_DESIRED : {}, VELOCITY_MESURED : {}, PWM : {} ".format(self.velocity_desired,'Not_implemented_yet', pwm))

if __name__ == "__main__":
    rospy.init_node('velocity_controller', anonymous=True)
    velocity_control = Velocity_Control()
    
    while not rospy.is_shutdown():
        velocity_control.main()
        time.sleep(0.01)
        #velocity_control.rate.sleep()