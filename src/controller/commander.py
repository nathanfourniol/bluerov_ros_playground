#!/usr/bin/env python

import rospy
from std_msgs.msg import UInt16
from std_msgs.msg import Bool
from sensor_msgs.msg import Joy
from bluerov_ros_playground.msg import Set_velocity 
from bluerov_ros_playground.msg import Set_heading 
from bluerov_ros_playground.msg import Set_depth
from time import sleep

class Commander():
    def __init__(self, arm=True, pwm_forward=1500, pwm_neutral=1500, rosrate=4):
        self.pub_rc3 = rospy.Publisher('/BlueRov2/rc_channel3/set_pwm', UInt16, queue_size=10) #THROTTLE
        self.pub_rc4 = rospy.Publisher('/BlueRov2/rc_channel4/set_pwm', UInt16, queue_size=10) #YAW
        self.pub_rc5 = rospy.Publisher('/BlueRov2/rc_channel5/set_pwm', UInt16, queue_size=10) #FORWARD
        self.pub_rc6 = rospy.Publisher('/BlueRov2/rc_channel6/set_pwm', UInt16, queue_size=10) #LATERAL
        self.pub_rc8 = rospy.Publisher('/BlueRov2/rc_channel8/set_pwm', UInt16, queue_size=10) #CAMERA TILT 
        #self.pub_rc9 = rospy.Publisher('/BlueRov2/rc_channel9/set_pwm', UInt16, queue_size=10) #LIGHTS 1
        #self.pub_rc10 = rospy.Publisher('/BlueRov2/rc_channel10/set_pwm', UInt16, queue_size=10) #LIGHTS 2
        #self.pub_manual_control = rospy.Publisher('/BlueRov2/manual_control', Joy, queue_size=10)

        rospy.Subscriber('/Command/depth', UInt16, self._callback_depth)
        rospy.Subscriber('/Command/heading', UInt16, self._callback_heading)
        rospy.Subscriber('/Command/velocity', UInt16, self._callback_velocity)
        rospy.Subscriber('/Command/joy', Joy, self._callback_joy)

        rospy.Subscriber('/Settings/set_depth', Set_depth, self._settings_depth_ctrl_callback)
        rospy.Subscriber('/Settings/set_heading', Set_heading, self._settings_heading_ctrl_callback)
        rospy.Subscriber('/Settings/set_velocity', Set_velocity, self._settings_velocity_ctrl_callback)

        self.pub_arm = rospy.Publisher('/BlueRov2/arm', Bool, queue_size=10)
        self.rate = rospy.Rate(rosrate)
        
        self.pwm_forward = pwm_forward
        self.pwm_neutral = 1500
        self.armed = arm
        self.pwm_depth = 0
        self.pwm_heading = 0
        
        self.enable_depth_ctrl = False
        self.enable_heading_ctrl = False
        self.enable_velocity_ctrl = False

        self.override_controller = 1 # 0:automatic control, 1:gamepad control
        self.gamepad_axes = [self.pwm_neutral, self.pwm_neutral, self.pwm_neutral, self.pwm_neutral] # THROTTLE,YAW,FORWARD, LATERAL
        self.gamepad_buttons = [0,0,0,0,0, 1100] # ARM, OVERRIDE_CONTROLLER, LIGHT_DEC, LIGHT_INC, PWM_LIGHT

    def _callback_depth(self,msg):
        self.pwm_depth = msg.data

    def _callback_heading(self,msg):
        self.pwm_heading = msg.data

    def _callback_velocity(self,msg):
        self.pwm_forward = msg.data

    def _callback_joy(self,msg):
        self.gamepad_axes = msg.axes
        self.gamepad_buttons = msg.buttons
        self.override_controller = self.gamepad_buttons[1]

    def _settings_depth_ctrl_callback(self,msg):
        #enable_depth_ctrl, pwm_max, KI, KP, KD
        self.enable_depth_ctrl= msg.enable_depth_ctrl

    def _settings_heading_ctrl_callback(self,msg):
        #enable_heading_ctrl, pwm_max, KP, KD
        self.enable_heading_ctrl= msg.enable_heading_ctrl

    def _settings_velocity_ctrl_callback(self,msg):
        #enable_velocity_ctrl, pwm_max, KP, KD
        self.enable_velocity_ctrl = msg.enable_velocity_ctrl
 
    def publish_controller_command(self):
        self.pub_arm.publish(self.armed)
        if self.enable_depth_ctrl:
            print('DEPTH CONTROLLER ENABLE')
            self.pub_rc3.publish(self.pwm_depth)
        if self.enable_heading_ctrl:
            print('HEADING CONTROLLER ENABLE')
            self.pub_rc4.publish(self.pwm_heading)
        if self.enable_velocity_ctrl:
            print('VELOCITY CONTROLLER ENABLE')
            self.pub_rc5.publish(self.pwm_forward)


#	    if abs(self.pwm_heading-self.pwm_neutral)>5:  # Correct the heading
#		    self.pub_rc4.publish(self.pwm_heading)
#	    else:
#		    self.pub_rc5.publish(self.pwm_forward) # Go forward

    def publish_gamepad_command(self):
        """gamepad_axes = [THROTTLE, YAW, FORWARD, LATERAL]
           gamepad_buttons = [ARM, OVERRIDE_CONTROLLER, PWM_CAMERA, LIGHT_DEC, LIGHT_INC]
        """
        self.pub_arm.publish(self.gamepad_buttons[0])
        self.pub_rc8.publish(self.gamepad_buttons[2]) #CAMERA
        #self.pub_rc9.publish(self.gamepad_buttons[5])
        #self.pub_rc10.publish(self.gamepad_buttons[5])
        
        self.pub_rc3.publish(self.gamepad_axes[0]) # THROTTLE
        self.pub_rc4.publish(self.gamepad_axes[1]) # YAW
        self.pub_rc5.publish(self.gamepad_axes[2]) # FORWARD
        self.pub_rc6.publish(self.gamepad_axes[3]) # LATERAL
        
        #msg = Joy()
        #msg.buttons = [0]*16
        #msg.buttons[14]=self.gamepad_buttons[4] # light increase gain
        #msg.buttons[13]=self.gamepad_buttons[3] # light decrease gain
        #self.pub_manual_control.publish(msg)

    def master_control(self):
        if self.override_controller == 1:
            self.publish_gamepad_command()
        else :
            self.publish_controller_command()


if __name__ == "__main__":
    rospy.init_node('Commander', anonymous=True)
    cmd = Commander(pwm_forward=1500)
    while not rospy.is_shutdown():
        cmd.master_control()
        cmd.rate.sleep()

