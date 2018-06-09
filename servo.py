'''@file servo.py
Servo python file which consists of a Servo class that has methods to control
the position of a servo by calculating and setting the duty cycle
of the servo.
@authors Sam Lee & Dima Kyle
'''
import pyb
import math

class Servo:
    """
    A class for controlling the position of a servo. 
    This code was referenced from the following link below.
    
    Reference:  https://bitbucket.org/thesheep/micropython-servo/src
    
    Class methods are:
    write_us(us)  ==> sets the servo duty cycle
    write_angle(degrees) ==> solves for servo signal in microseconds from 
                             user input angle.
    
    To Properly initialize an instance of Servo, refer to the example below
    Ex:
    @code
    servo_1 = Servo('PA5')
    @endcode
    
    This makes an instance of Servo using Timer 2 on pin A5 of the white 
    Nucleo L476RG board that is pin connected on top of the Shoe of Brian
    purple MicroPython board. 
     

    Parameters:
    @param pin (machine.Pin): The pin where servo is connected. Must support PWM.
    @param prescaler: allow the timer to be clocked at the rate a user desires.
    @param freq (int): The frequency of the signal, in hertz.
    @param min_us (int): The minimum signal length supported by the servo.
    @param max_us (int): The maximum signal length supported by the servo.
    @param angle (int): The angle between the minimum and maximum positions.
        
    All of these parameters can be found on the servo's datasheet linked below.
    HS-65MG Servo Datasheet: https://www.servocity.com/hs-65mg-servo     
    """
    
    def __init__(self, pin, prescaler=4.5, freq=50, min_us=665, max_us=2360, angle=190):
        ## The Timer desired for the servo at a specified frequency
        self.tim = pyb.Timer(2, freq=freq) 
        ## Output pin used to control the servo
        self.pin = pyb.Pin(pin, pyb.Pin.OUT_PP)
        ## Channel used to initialize the servo for PWM 
        self.ch2 = self.tim.channel(1, pyb.Timer.PWM, pin=self.pin)
        # The minimum signal length supported by the servo
        self.min_us = min_us
        # The maximum signal length supported by the servo
        self.max_us = max_us
        # The signal length variable initialized to zero
        self.us = 0
        # The frequency of the signal, in hertz
        self.freq = freq
        # The angle between the minimum and maximum positions
        self.angle = angle
        # electronic counting circuit used to reduce a high frequency
        # electrical signal to a lower frequency 
        self.prescaler = prescaler
        self.t_freq = 0

    def write_us(self, us):
        ''' setting the duty cycle for the servo to control its position. 
        Returns the signal length of the servo in microseconds, frequency (Hz).
        period (Sec), and the percent duty cycle being sent
        
        @param us The current signal length of the servo.
        '''
        # print('Signal length: '+str(us)+' microseconds')
        # print('Signal Frequency: '+str(self.freq)+' Hz')
        # solve for period of signal in seconds
        self.t_freq = (1/(self.freq+self.prescaler))*10**6
        # print('Signal Period: '+str(t_freq)+' seconds')
        # solve for duty cycle to determine position of servo
        duty = 100*us/self.t_freq
        # print('Servo Duty Cycle: '+str(duty)+' %')
        # et the percent duty cycle for the servo to control its position
        self.ch2.pulse_width_percent(duty)

    def write_angle(self, degrees=None, radians=None):
        '''Move to the specified angle in ``degrees`` or ``radians``.
        Solves for and returns the signal length of the servo '''
        # Convert to radians if nothing selected for degrees
        if degrees is None:
            degrees = math.degrees(radians)
        # divide input angle by 360 deg with remainder
        degrees = degrees % 360
        # solve for total range of servo signal length 
        total_range = self.max_us - self.min_us
        # solve for signal length in microsec based on user input angle 
        us = self.min_us + total_range * degrees / self.angle
        self.write_us(us)
    
    def read_servo(self):
        '''
        This function is not yet developed but is aiming to be able to read the
        timer
        '''
        self.read = self.tim.counter()
        self.conversion = 90/500 #degrees per microsecond conversion
        self.servo_pos  = self.read*self.conversion #convert microseconds to degrees
        return self.servo_pos
        
        
def main():
    '''
    Test code for user input to try moving servo to various angles 
    between 0 and 180 degrees from the REPL.
    '''
    #Creating instance of Servo
    ## instance of Servo 1 created for pin A1 on white Nucleo L476RG board 
    servo = Servo('PA5')
    while True:
        angle = input('Angle: ')
        servo.write_angle(degrees = int(angle))
