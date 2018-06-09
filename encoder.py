''' 
@file main.py
This is the main file for the Lab 1 that contains the code to create a
class Encoder. The class Encoder can read the current position and also
zero the position.
'''

import pyb
import io_funcs

class Encoder:
    ''' 
    This class implements a quadrature encoder for a Shoe of Brian 
    purple MicroPython board that is pin connected on top with a 
    white Nucleo L476RG board. To create an instance of class Encoder, 
    see the following example.
    Class methods are:
        read(self) Returns the motors current position
        zero(self) Zeros the motor's position
        
    Limited to Channel 1 and 2.     
    '''
    def __init__ (self, timer, pin_1, pin_2):
        '''
        Creates a motor driver by initializing GPIO
        pins and gets first initial position. Ensure that the timer
        and pins used correspond to 1, Where the encoder is connected
        to the board and 2. Timer works for those pins. See Table 17
        To create an instance of class Encoder. See the following example.
    
        EX:
        
        @code
        Encoder_1 = Encoder(8,'PC6','PC7')
        @endcode
        
        Creating an instance of Encoder called Encoder_1 on Timer 8 and 
        connected to the board in pins C6 and C7.
        
        @param timer The timer wanted to be used.
        @param pin_1 The first pin on the board for encoder Ch A.
        @param pin_2 The second pin on the board for encoder Ch B.
        '''
        ## The Timer desired for the encoder with period=0xFFF, prescalar=0
        self.tim = pyb.Timer(timer,period=0xFFFF,prescaler=0)
        
        # self.alternate = 0, may need to decide alternate function
        
        # Setting the first encoder pin to the chosen pin_1
        ## Pin object to work with Channel 1 of quadrature encoder
        self.pinENa = pyb.Pin(pin_1, pyb.Pin.IN) 
        
        # Setting the second encoder pin to the chosen pin_2
        ## Pin object to work with Channel 2 of quadrature encoder
        self.pinENb = pyb.Pin(pin_2, pyb.Pin.IN)
        
        # First channel for pin_1
        self.ch1 = self.tim.channel(1, pyb.Timer.ENC_AB, pin=self.pinENa)
        
        # Second channel for pin_2
        self.ch2 = self.tim.channel(2, pyb.Timer.ENC_AB, pin=self.pinENb)
        
        ## A class attribute for the encoder's current position
        self.position = 0
        
        ## A class attribute for the encoder's last position
        self.last_pos = 0
        
        ## A class attribute for encoder's change in position
        self.delta = 0
        
        ## A read attribute to hold the current value of encoder's position
        self.read_value = 0


    def read(self):
        '''
        Method for returning the correct current position of the encoder
        @return position The current position of the encoder        
        '''
        # Read first defined with the current position of the motor
        self.read_value = self.tim.counter()
        # Delta defined as difference between the current and last position
        self.delta = self.read_value - self.last_pos
        if self.delta >= 32768:
            # If delta is greater than half the range, subtract the range
            self.delta -= 65536
        elif self.delta < -32768:
            # If delta is less than half the negative range, add the range
            self.delta += 65536
        # Adjust the position by delta
        self.position += self.delta
        # Save most recent read value from the encoder to be the last position
        self.last_pos = self.read_value
        
        #print('Encoder Position: %15i '%self.position)

        return self.position
 
   
    def zero(self):
        '''
        Method for reseting the position of the ecoder to zero. Zeros position
        '''
        self.last_pos = self.tim.counter()
        self.position = 0
        self.delta = 0
        
        #print('Zeroing position: %15i'%self.position)

                  
def main():
    '''
    Main file that creates instances of the encoders to test the reading and 
    zeroing of encoders.
    
    The encoders are initialized as follows:
    @code
    Encoder_1 = Encoder(8,'PC6','PC7')
    Encoder_2 = Encoder(4,'PB6','PB7')
    @endcode
    '''
    # Two different encoders
    Encoder_1 = Encoder(8,'PC6','PC7')
    Encoder_2 = Encoder(4,'PB6','PB7')
    
    Encoders = [Encoder_1, Encoder_2]
    
    
    '''
    tim4 = pyb.Timer(4,period=0xFFFF,prescaler=0)
    
    pinENa = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.IN, af=2)
    pinENb = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN, af=2)
    
    ch1 = tim4.channel(1, pyb.Timer.ENC_AB, pin=pinENa)
    ch2 = tim4.channel(2, pyb.Timer.ENC_AB, pin=pinENb)
    '''
    
    # Boolean for loops
    main_loop = True
    encoder_loop = True
    state = 0
    
    while main_loop == True:
        ''' Main loop of program. '''
        # Note the use of states and loops is probably redundant.
        if state == 0:
            # encoder input and main exit
            while encoder_loop == True:
                encoder_message = '1 to read encoders, 2 to zero, 0 to quit: '
                encoder_num = io_funcs.get_input(int,encoder_message)
                if encoder_num == 0:
                    main_loop = False
                    encoder_loop = False
                    print('Goodbye')
                    break
                elif encoder_num == None:
                    print('Nothing entered')
                elif encoder_num == 1:
                    state = 1
                    encoder_loop = False
                elif encoder_num == 2:
                    state = 2
                    encoder_loop = False
                elif encoder_num>2:
                    print('Please enter a right number 0-2')
                else:
                    print('Uh oh... Incorrect input?')    
        elif state == 1:
            # Reading current encoder position
            i = 1
            for n in Encoders:
                print('Encoder '+str(i))
                pos = n.read()
                print(str(pos))
                i+=1
            state = 0
            encoder_loop = True
        elif state == 2:
            # Zeroing the encoders
            print('Zeroing encoders')
            i = 1            
            for n in Encoders:
                print('Encoder '+str(i))
                n.zero()
                n.read()
                i+=1
            state = 0
            encoder_loop = True


if __name__ == '__main__':
    main()
