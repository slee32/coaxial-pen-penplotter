''' 
@file controller.py
@authors Sam Lee and Dima Kyle
Controller python file. It has the class Controller that has methods to
perform closed-loop proportional, integral, and derivative control 
and repeatedly output an actuation value that is sent to the motor for this 
lab, but generally could be sent to any device as a generic controller.
'''

import utime

class Controller:
    '''
    This class implements closed-loop proportional control 
    to run as a generic controller for a Shoe of Brian 
    purple MicroPython board that is pin connected on top with a 
    white Nucleo L476RG board. 
    
    This class has the following methods:
    _init_(), algorithm(), set_gain(), set_KI(),set_KD(),set_KW(),
    set_setpoint(), print_response(), get_response().
    The constructor first sets all the necessary parameters for the controller
    to work. Algorithm returns an actuation value that can be generally set
    to anything as a generic controller. The algorithm method takes the 
    subtraction of the setpoint parameter (motor position input for this 
    project) and the actual measured parameter (measured motor position for 
    this project). Set_setpoint creates arrays for specific parameters and 
    sets the setpoint, which is the desired position for the DC motor in our
    case. Set_gain sets the proportional control gain for the device.
    Get_response and print_response are methods which run step response 
    tests each time the enter key is pressed by the user, which reads the 
    resulting data and prints a list of time, actual position, and error 
    values in the serial port terminal.
    
    This controller is setup for proportional, integral, derivative control.
    The anti-windup features are not completely developed.
    
    The only anti-windup code simply puts a saturation limit of the error_sum
    to the duty cycle divided by the K_I.
    
        
    The following are not actual parameters specific to the code, but are meant
    to describe important attributes for the Controller class.
    @param K_P User input proportional gain of the device
    @param setpoint Input parameter to device (desired position of motor)
    @param error Error signal or the difference in setpoint from the
    measured setpoint.This will be the measured motor location subtracted 
    from the initial setpoint location.
    @param actuation Actuation signal to device as a result from the error
    signal multiplied by control gain. This will be a signal sent
    to the motor to control magnitude and direction of motor torque.
    @param actual Measured parameter of device (motor position)
    @param act_value List of measured motor positions 
    @param time List for how long motor has run for 
    @param error_list List of error values between each controller run
    @param delta_time Total time elapsed for motor run at one revolution
    @param delta Last actual motor position measured at the end of each 
    test conducted.
    @param accuracy Percent difference from the setpoint and actual 
    values at the last motor position measured.
    @param K_I Integral control constant
    '''
    def __init__ (self):
        '''
        Constructor method which sets the proportional gain, inital setpoint, 
        actual setpoint, error signal, actuation signal with a saturation limit. 
        Lists are initialized to extract actuation signal, time, and error data 
        along with setting a change in time paramter for generating
        response plots of the motor over the period of time it is run for.
        '''
        
        ## Input for proportional gain of the motor 
        self.K_P = 0
        ## Desired position of the motor 
        self.setpoint = 0
        ## Difference in the setpoint of the motor from its measured position
        self.error = 0
        ## Signal sent to the motor to control the magnitude and direction of
        ## its torque
        self.actuation = 0
        ## Measured position of the motor after the setpoint desired is inputed
        self.actual = 0
        # List of measured motor positions
        self.act_value = []
        # List of time values for when motor is running
        self.time = []
        # List of calculated error signal values
        self.error_list = []
        ## Response time of motor run for one revolution (setpoint=4000) for 
        ## the step response test
        self.delta_time = 0
        ## Last motor position measured from step response test 
        self.delta = 0 
        ## Percent difference from setpoint position and actual motor position
        self.accuracy = 0
        ## Error sum for integral control
        self.error_sum = 0
        ## Integral control constant
        self.K_I = 0
        ## Previous error used for derivative control
        self.prev_error = 0
        ## Delta err for derivative control
        self.d_error = 0
        ## Time of control
        self.t = 0
        ## Previous t of control
        self.prev_t = 0
        ## Delta time for derivative control
        self.dt = 0
        ## Derivative control constant
        self.K_D = 0
        ## A* for K anti-windup
        self.act_star = 0
        ## Anti-windup control constant
        self.K_W = 0
        
    
    def algorithm(self, actual):
        '''
        Algorithm is a function that subtracts the measured parameter of the 
        device from the desired setpoint to return an error signal, which 
        is then multiplied by the proportional gain input value to solve
        for an actuation value. This actuation signal which controls the 
        magnitude and direction of the device torque is limited to be 
        within -100 and 100 before getting returned.
        @param actual The actual position of the object of interest
        @return actuation The level to set the actuation for control.
        '''
        # For timing in order to calculate derivative control
        self.t = utime.ticks_us()
        # Delta time, converted into seconds
        self.dt = (self.t - self.prev_t)*10**-6
        # The actual position on the         
        self.actual = actual
        # Calculating in the error from the setpoint and the actual
        self.error = self.setpoint-self.actual
        # Change in error from the previous instance
        self.d_error = self.error-self.prev_error
        # Accumulated error
        self.error_sum = self.error_sum + self.error
        
        # Proportional control
        self.proportional = self.error*self.K_P
        
        # Integral control
        self.integral = (self.error_sum)*self.K_I
        
        #integral = (self.error_sum-self.K_W*(self.actuation-self.act_star))*self.K_I
        
        # Limit of error sum
        limit = abs((100)/self.K_I)
        # Error sum saturation
        if self.error_sum>limit:
            self.error_sum = limit
        elif self.error_sum < -limit:
            self.error_sum = -limit
        
        # Derivative control
        self.derivative = self.K_D*self.d_error/self.dt
        
        # Total actuation
        self.actuation = self.proportional + self.integral + self.derivative
        
        # Setting error and time for next iteration        
        self.prev_err = self.error
        self.prev_t = self.t
        
        # Saturation for a*
        if self.actuation > 100:
            self.actuation = 100
        elif self.actuation <-100:
            self.actuation = -100
        return self.actuation


    def set_gain(self, gain):
        '''
        This function sets the user inputed Kp value of the device 
        to a variable named gain which represents the proportional gain 
        of the device.
        @param gain The gain for the proportional control.
        '''
        self.K_P = gain
        
    def set_KI(self, K_I):
        '''
        This function sets the user inputed K_I value of the device 
        to a variable named gain which represents the integral gain 
        of the device.
        @param K_I The gain for the integral control.
        '''
        self.K_I = K_I
    
    def set_KD(self, K_D):
        '''
        This function sets the user inputed K_D value of the device 
        to a variable named gain which represents the derivative gain 
        of the device.
        @param K_D The gain for the derivative control.
        '''
        self.K_D = K_D
    
    def set_KW(self, K_W):
        '''
        This function sets the user inputed K_W value of the device 
        to a variable named gain which represents the anti_windup gain 
        of the device.
        @param K_w The gain for the anti_windup control.
        '''
        self.K_W = K_W


    def set_setpoint(self, point):
        '''
        Method which creates lists for the actual value being measured, 
        time, and error values to be used for plotting a step response of 
        the device.
        
        Commented lists to hold time, error, and actual position for response
        These are commented out for now to save memory.
        
        @param point Point to set as the setpoint.
        '''
        
        #self.act_value = []
        #self.time = []
        #self.error_list = []
        self.setpoint = point


    def print_response(self):
        '''
        Method which runs step response tests by sending a signal through
        the USB serial port to the MicroPython board, reading the resulting 
        actual and time data, and plotting the step response.
        '''
        #start collecting the time data at time 0
        t_o = self.time[0]
        for n in self.act_value:
            index = self.act_value.index(n)
            print(bytes("{:10.6f} , {:15.6f} , {:15.6f}".format(self.time[index]-t_o,n,self.error_list[index]),'UTF-8'))
            #print('%15.10f, %15.10f,%15.15f'%(self.time[index],n,self.error_list[index]))
        self.accuracy = abs(self.setpoint-self.actual)*200/abs(self.setpoint+self.actual)
        self.delta_time = (self.time[-1]-self.time[0])/1000
        self.delta = (self.act_value[-1]-0)
        print('Response Delta: %10.10f'%(self.delta))
        print('Percent Diff:   %10.10f'%(self.accuracy))
        print('Response Time:  %10.10f'%(self.delta_time))
        print('K_P Value:      %7.5f'%(self.K_P))


    def get_response(self):
        '''
        Method that takes the time values and actual measured
        motor position values, and puts them into a list 
        for getting time and position response of the motor.
        @return [time, act_value] Returns a list of a time and position
        '''
        return [self.time,self.act_value]
            
        
        