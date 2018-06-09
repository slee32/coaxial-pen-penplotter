''' 
@file motor_sam_dima.py 
@authors Sam Lee and Dima Kyle
Motor driver python file. It has the class MotorDriver that has methods to
output the current duty cycle of a motor and set the duty cycle of the motor.
'''

import pyb
import io_funcs

class MotorDriver:
    ''' 
    This implements a DC motor at a frequency of 2000 Hz for the Shoe of Brian 
    purple MicroPython board that is pin-connected on top with a 
    white Nucleo L476RG board.
  
    Class methods are:
    set_duty_cycle(level)
    get_duty_cycle() ==> returns the duty_cycle of the motor
    
    Limited to Timers 3 and 5
    '''
    def __init__ (self, timer, pin_1, pin_2, pin_3):
        ''' 
        Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. We will be using DC motors
        that will be powered with 12 volts and a 0.5 amp current limit by 
        connecting power from a benchtop supply to the motor driver board 
        with the Gnd and Vin screw terminals. To program a MotorDriver 
        class, a USB cable is connected to the bottom MicroPython board
        and a DC motor is connected to the Motor A or B screw terminals 
        in the driver board.  The ST Microelectronics L6206 dual H-bridge
        motor driver chip datasheet was referenced. The link to the data
        sheet can be found on page 2, Figure 2 from the following link.
        
        L6206 Datasheet: https://www.google.com/search?q=ST+Microelectronics+
        L6206+dual+H-bridge+motor+driver+chip&oq=st+micro&aqs=chrome.1.
        69i57j69i59j0l4.3671j0j7&sourceid=chrome&ie=UTF-8
        
        From the diagram, the motor is connected to pins OUT1A and OUT2A. The 
        microcontroller controls pins ENA, IN1A, and IN2A        
    
        To properly initialize an instance of MotorDriver, refer to the 
        example below.
        EX:
        
        @code
        motor_1 = MotorDriver(3,'PA10','PB4','PB5')
        @endcode
        
        This makes an instance of MotorDriver using Timer 3,
        PA10 enables the motor and PB4 and PB5 are used control the motor
        in one particular direction.
        
        @param timer Timer to be used for the motor
        @param pin_1 First pin to enable the motor. PinEn is to be the output 
        pin at pin_1.
        @param pin_2 Second pin for IN1 direction 1. PinIN1 is to be the output 
        pin at pin_1.
        @param pin_3 Third pin for IN2 direction 2. PinIN2 is to be the output 
        pin at pin_2.
        '''
        ## Open-drain output pin set high to enable the DC motor
        self.pinEN = pyb.Pin(pin_1, pyb.Pin.OUT_PP)
        ## Regular push-pull output pin set to low and configured with af=2 to 
        ## control the direction of PWM signal sent to the motor.
        self.pinIN1 = pyb.Pin(pin_2, pyb.Pin.OUT_PP)
        ## Regular push-pull output pin set to high and configured with af=2 to 
        ## power the motor in one direction
        self.pinIN2 = pyb.Pin(pin_3, pyb.Pin.OUT_PP)
        ## The desired frequency of the pulse in the pulse width modulation
        self.Hz = 20000
        ## The Timer wanted for the motor at a specified frequency
        self.tim = pyb.Timer(timer, freq=self.Hz)
        # Setting ch1 to channel 1
        self.ch1 = self.tim.channel(1, pyb.Timer.PWM, pin=self.pinIN1)
        # Setting ch2 to channel 2
        self.ch2 = self.tim.channel(2, pyb.Timer.PWM, pin=self.pinIN2)
        # Initial duty cycle is set 0        
        self.duty_cycle = 0
        
        # Enabling the motor
        self.pinEN.high()
        self.pinIN1.low()
        self.pinIN2.high()
        
        # The motor to be initialized in a stopped state
        self.ch1.pulse_width_percent(0)
        self.ch2.pulse_width_percent(0)
        
        #print ('Creating a motor driver')

    
    def get_duty_cycle(self):
        '''
        This function simply returns the duty cycle of the motor
        @return duty_cycle The duty cycle of the motor as a percentage
        '''
        return self.duty_cycle

    def set_duty_cycle (self, level):
        ''' 
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty cycle of the motor (%) 
        '''
        try:
            ''' Test for int '''
            # Try setting the duty cycle to the level
            self.duty_cycle = int(level)
            
            if self.duty_cycle > 100 or self.duty_cycle<-100:
                # If not in the valid range, raise an InputError
                raise io_funcs.InputError("Invalid Input",io_funcs.InputError)
        except io_funcs.InputError:
            print("Please don't be an asshole. Number -100 to 100 only")        
        except (TypeError, ValueError):
            print("Please don't be an asshole. Type integers only")
        
        if level<0:
            # Forward
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(abs(level))
        elif level>0:
            # Backward
            self.ch1.pulse_width_percent(abs(level))
            self.ch2.pulse_width_percent(0)
        elif level == 0:
            # Stop
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(0)
        #print ('Setting duty cycle to ' + str (level))
      

def main():
    ''' 
    Main code if this code is the main executed code.
    This is used to test the motors with user input to choose an
    arbitrary duty cycle for the motors.
    
    @code    
    ## instance of a Motor 1 created for screw terminal A on Blue IHM04A1 board
    motor_1 = MotorDriver(3,'PA10','PB4','PB5')
    ## instance of a Motor 2 created for screw terminal B on Blue IHM04A1 board
    motor_2 = MotorDriver(5,'PC1','PA0','PA1')
    @endcode
    '''
    # Creating an instances of a MotorDriver    
    ## instance of a Motor 1 created for screw terminal A on Blue IHM04A1 board
    motor_1 = MotorDriver(3,'PA10','PB4','PB5')
    ## instance of a Motor 2 created for screw terminal B on Blue IHM04A1 board
    motor_2 = MotorDriver(5,'PC1','PA0','PA1')
    
    ## List of class instances of all motors
    motors = [motor_1, motor_2]
    
    # Booleans for loop
    main_loop = True
    motor_loop = True
    state = 0
    while main_loop == True:
        ''' Main loop of program. Obtains input from user to set duty cycle '''
        # Note the use of states and loops is probably redundant.
        for n in motors:
            # For every motor, print the current duty cycle
            print('Motor '+ str(motors.index(n)+1)+
            '\nMotor Duty Cycle: '+str(n.get_duty_cycle()))
        if state == 0:
            # Motor input and main exit
            while motor_loop == True:
                # Message to display for motor input                
                motor_message = 'Motor 1 or 2; 0 to quit program: '
                # Getting which motor is needed
                motor_num = io_funcs.get_input(int,motor_message)
                if motor_num == 0:
                    # Break from loop, zero motors, and exit
                    main_loop = False
                    motor_loop = False
                    for n in motors:
                        n.set_duty_cycle(0)
                    print('Goodbye')
                    break
                elif motor_num == None:
                    # If nothing is entered
                    print('Nothing entered')
                    continue
                
                if motor_num<=len(motors):
                    # Setting the motor to be controlled to the right motor
                    motor = motors[motor_num-1]
                    state = 1
                    duty_loop = True
                    motor_loop = False
                    # Change to Duty Cycle Change loop
                else:
                    # Incorrect input
                    print('Uh oh... Incorrect input?')
                    continue  
        elif state == 1:
            # Changing motor duty_cycle state
            while duty_loop == True:
                # Message to display while getting duty cycle
                duty_message = 'Duty Cycle (-100 to 100; Enter to exit): '
                # Getting the duty cycle desired
                duty_cycle = io_funcs.get_input(int, duty_message)
                if duty_cycle == '' or duty_cycle == None:
                    # If None, exit back to Choosing Motor State
                    state = 0
                    motor_loop = True
                    duty_loop = False
                    break
                # After correct input, convert and set the motor's duty cycle
                duty_cycle = int(duty_cycle)
                motor.set_duty_cycle(duty_cycle)

if __name__ == '__main__':
    main()
