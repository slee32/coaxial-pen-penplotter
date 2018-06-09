''' 
@file motor_task.py
@authors Sam Lee and Dima Kyle
This file has a class which runs motors under closed-loop motor control
at the same time so that motors act indepedndently of each other.
'''

import encoder
import motor_sam_dima
import controller


class Motor_control_task:
    '''
    Class which contains a motor task function. This task initializes two 
    instances of DC motors and quadruture encoders to be used and has two
    states to run the motor with the necessary data for finding the motor's
    position for one state, and another state to run the motor without any
    data. In the main.py file, a for loop is run for each motor number, where 
    the period is set for each motor. From this for loop, both motors have an 
    instance of the same motor controller task.
    
    There is a method run_motor() to run the motor's in a scheduler.
    '''
    
    def __init__(self, motor_num): 
        ''' This constructor method initializes two instances of DC motors
        and two quadruture encoders. Additionally, the optimal proportional 
        gain of Kp is set for each motor. Both encoder positions 
        are then zeroed, and the setpoint is set for the encoder ticks. 
        Lastly, all variables used for the motor task function run_motor are 
        initialized, including motor_num, state, position, iterate, and limit.
        
        @param motor_number Motor number parmater that specifies which motor and 
        encoder is being initialized for each task. 
        
        These are values that can be changed in the code itself.
        @param state The state for which the motor control task is in.
        @param position Initializing the motor position to start at 0.
        @param iterate Initializing the iterate variable to start at 0.
        @param limit Limit on the amount of iterations the motor is 
        running position data for.
        
        The KP, KI, and KD can be changed for the situation  required.
        '''
        self.control = controller.Controller()
        if motor_num == 0:
            self.motor = motor_sam_dima.MotorDriver(3,'PA10','PB4','PB5')
            # A +/- on top board
            self.encoder = encoder.Encoder(8,'PC6','PC7')
            # Left goes to C6, right to PC7, rotates counterclockwise positive
            self.control.set_gain(0.1)
            # Setting the KI
            self.control.set_KI(0.001)
            # Setting the KD
            self.control.set_KD(0.00001)
            # Setting the KD
            self.control.set_KW(0)

        elif motor_num == 1:
            self.motor = motor_sam_dima.MotorDriver(5,'PC1','PA0','PA1')
            # B +/- on top board
            self.encoder = encoder.Encoder(4,'PB6','PB7')
            # Left goes to B6, right to PB7, rotates counterclockwise positive
            self.control.set_gain(0.1)
            # Setting the KI
            self.control.set_KI(0.001)
            # Setting the KD
            self.control.set_KD(0.00001)
            # Setting the KD
            self.control.set_KW(0)
            
        else:
            print('Invalid Motor Number')

        ## Motor number which specifies which motor task is being run    
        self.motor_number = motor_num
        self.encoder.zero()
        ## Motor control task to start in state 0 to run the motors with data
        self.state = 0
        ## Position of the motor initially
        self.position = 0
        ## Initial setpoint
        self.control.setpoint = 3200 
        ## Iteration limit for outputting data
        self.iterate = 0
        ## Limit on the amount of iterations the motor is outputting position 
        ## data for.
        self.limit = 50
        # print('Initialized Motor '+str(self.motor_number))
    
    
    def run_motor(self):
        '''
        Motor task function consisting of two states. The first state 
        runs the motors with data for a specific amount of iterations. Once 
        the amount of iterations have reached a specific limit, then the 
        task will go into the next state 1 which runs the motors without 
        any data. The motor_number, position and actuation values are then 
        printed before the state is yielded. 
        
        '''
        n = 0
        while True:
            # State to run with data
            if self.state == 0:
                self.position = self.encoder.read()
                self.actuation = self.control.algorithm(self.position)
                self.motor.set_duty_cycle(self.actuation)
                #self.iterate += 1
                
                #print_task.put(str (self.motor_number))  
                if self.iterate>self.limit:
                    self.state = 1
                    
            # State to run without data        
            elif self.state == 1:
                self.position = self.encoder.read()
                self.actuation = self.control.algorithm(self.position)
                self.motor.set_duty_cycle(self.actuation)
                
            if n == 500:    
                print(str(self.motor_number),str(self.position),str(self.control.setpoint))
                n = 0
            n += 1
            
            yield(self.state)
            
            
                
                
            
            