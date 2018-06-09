''' @file main.py
This is the main file that runs the pen plotter. 
@authors Sam Lee and Dima Kyle
'''

import pyb
import micropython
import gc
import cotask
import motor_task
import io_funcs
import servo


micropython.alloc_emergency_exception_buf (100)


# How much the pen will lift up
lift = 30
# Tolerance between setpoint and actual
tolerance = 20

def servo_func():
    '''
    Servo task function. This function has 2 (3 including a done state).
    The three states are Up, Down, and Done.
    servo_state is what causes the state to change
    This function receives a class instance of a servo and the angles that
    correspond with down and up.
    '''
    global pen_servo, servo_state, up_angle, down_angle
    # Initial state
    state = 0
    # How many time it iterates before moving to its next state
    time_reset = 100
    # Initializing time
    time = time_reset
    
    while True:
        # Setting to correct state
        if servo_state == 'UP':
            state = 1
        elif servo_state == 'DOWN':
            state = 2
        else:
            state = 0
        if state == 1:
            # Bring the pen up
            pen_servo.write_angle(degrees = up_angle)
            time -= 1
            if time == 0:
                servo_state = 'DONE'
                print('Done')
                state = 0
                time = time_reset
        if state == 2:
            # Bring the pen down
            pen_servo.write_angle(degrees = down_angle)
            time -= 1
            if time == 0:
                servo_state = 'DONE'
                print('Done')
                state = 0
                time = time_reset
        #print(servo_state)
        yield(state)

def command_func():
    '''
    This is the main command function. It takes in a two motor task instances
    and a file, a servo_state to trigger servo state changes, and an end 
    variable (not used).
    
    It takes in a file and reads it line by line. Parses it by the command.
    The commands are the main states of this task.
    There are 5 main states: NEXT, IN, PU, PD, SP. IN and SP are neglected.
    In NEXT, the next line of the file is read and parsed to get the next
    command and maybe points.
    PU brings the pen up after reaching a setpoint
    PD brings the motor to a point, brings the pen down, and then traces the 
    following points.
    '''
    global motor_1_task, motor_2_task, file, servo_state, end
    COM = 'NEXT'
    # A time reset variable. This would be the preferred way to control the 
    # system but since we did not have our controls down we chose to use a
    # tolerance instead
    time_reset = 25
    time = time_reset
    
    while True:
        if COM == 'NEXT':
            # Read line and parse the commands and points
            line = file.readline()
            if line == '':
                end = True
                yield(COM)
            # Getting rid of end extra quotes
            line = line[1:-1]
            # Split the COM, number of coordinates, and list of coordinates
            command_list = line.split(';')
            # The command is the first of the list
            COM = command_list[0]
            # Getting rid of extra quote
            COM = COM[1:]
            print(COM)
            # Second entry is the number of coordinates
            point_num = int(command_list[1])
            # Deleting the first two to only have the coordinates remain
            del command_list[0]
            del command_list[0]
            points = command_list[0]
            # Getting rid of extra end quotes and space
            points = points[4:-2]
        elif COM == 'IN':
            # Simply move to next command
            COM = 'NEXT'
            yield(COM)            
        elif COM == 'PU':
            point_one = points.split('x')
            # Setting ticks
            ticks_1 = int(point_one[0])
            ticks_2 = int(point_one[1])
            # Setting the motor task setpoints
            motor_1_task.control.set_setpoint(ticks_1)
            motor_2_task.control.set_setpoint(ticks_2)
            time -= 1 
            # booleans for whether the motors are here or not
            here_1 = ticks_1-tolerance<motor_1_task.position < ticks_1+tolerance
            here_2 = ticks_2-tolerance<motor_2_task.position < ticks_2+tolerance 
            if servo_state == 'DONE':
                # Checking if the servo is done then move
                COM = 'NEXT'
                servo_state = ''
                time = time_reset
            if here_1 and here_2:
                # If both points are there set the servo to go up
                servo_state = 'UP'
            yield(COM) 
            
        elif COM == 'PD':
            # Bring the pen to a point, pen down, then trace all other points
            points_list = points.replace("'","")
            # Getting rid of quotes
            if point_num>1:
                points_list = points_list.split(',')
                point_paired = [x.split('x')for x in points_list]
            else:
                # If there is only one pair of points
                point_paired = [points.split('x')]
            point_one = point_paired[0]
            ticks_1 = int(point_one[0])
            ticks_2 = int(point_one[1])
            # Setting the motor ticks 
            motor_1_task.control.set_setpoint(ticks_1)
            motor_2_task.control.set_setpoint(ticks_2)
            time -= 1
            here_1 = ticks_1-tolerance<motor_1_task.position < ticks_1+tolerance
            here_2 = ticks_2-tolerance<motor_2_task.position < ticks_2+tolerance
            
            if servo_state == 'DONE':
                # When the servo is down
                time = time_reset
                if point_num > 1:
                    # Delete the first point since we are already there
                    del point_paired[0]
                    n = 0
                    while n < len(point_paired)-1:
                        # For every other point, trace
                        point = point_paired[n]
                        ticks_1 = int(point[0])
                        ticks_2 = int(point[1])
                        motor_1_task.control.set_setpoint(ticks_1)
                        motor_2_task.control.set_setpoint(ticks_2)
                        here_1 = ticks_1-tolerance<motor_1_task.position < ticks_1+tolerance
                        here_2 = ticks_2-tolerance<motor_2_task.position < ticks_2+tolerance
                        #print(point)
                        #print(motor_1_task.position,motor_2_task.position)
                        #print(here_1,here_2)
                        if here_1 and here_2:
                            n += 1
                        yield(COM)
                #gc.collect()
                COM = 'NEXT'
                servo_state = ''
                time = time_reset
            if here_1 and here_2:
                # Setting the servo down
                servo_state = 'DOWN'
            yield(COM)
        elif COM == 'SP':
            # Ignore
            COM = 'NEXT'
        else:
            print('uh oh')
        #gc.collect()
        yield(COM)
    
    
if __name__ == "__main__":
    # Pen initialization and calibration
    pen_servo = servo.Servo('PA5',prescaler=4.5, freq=25, min_us=665, max_us=2360, angle=190)
    pen_servo.write_angle(90)
    pen_cal = True
    n = 0
    # Loop to get correct pen down angle
    while pen_cal == True:
        answer = io_funcs.get_input(str,'Calibrated? [y/n] ')
        if answer == 'n':
            angle = io_funcs.get_input(int,'Angle? [degrees] ')
            if 190>angle>0:
                pen_angle = angle
                n = 1
            else:
                print('Invalid angle')
            pen_servo.write_angle(pen_angle)
        elif answer == 'y':
            if n == 0:
                print('First angle not entered')
                continue
            print('Calibrated')
            pen_cal = False
            down_angle = angle
            up_angle = down_angle+lift
        else:
            print('Incorrect input')
        print('Pen is at '+str(angle)+' degrees now')
    pen_servo.write_angle(up_angle)
            
    # Filename for hpgl text file
    file_search = True
    while file_search == True:
        file_name = io_funcs.get_input(str,'File name? [file.txt] ')
        try:
            file = open(file_name,'r')
            file_search = False
        except:
            print('Not a valid file name or type. Please try again')
    
    # Initializing motors and encoders with a task
    motor_1_task = motor_task.Motor_control_task(0)
    mname1 = 'Motor_' + str (motor_1_task.motor_number)
    cotask.task_list.append(cotask.Task(motor_1_task.run_motor, name = mname1,
        priority = 3, period = 8, profile = True))
    
    motor_2_task = motor_task.Motor_control_task(1)
    mname2 = 'Motor_' + str (motor_2_task.motor_number)
    cotask.task_list.append(cotask.Task(motor_2_task.run_motor, name = mname2,
        priority = 3, period = 8, profile = True))
    
    # Zero calibration
    print('Bring the motors to calibration point, aka x = 0 and y = L1 + L2')
    cal = True
    while cal == True:
        answer = io_funcs.get_input(str,'At position? [y/n] ')
        if answer == 'n':
            print('Bring the motors to calibration point, aka x = 0 and y = L1 + L2')
        elif answer == 'y':
            print('At calibration point. Setting position to calibration point')
            # Setting the motors to the initial position
            motor_1_task.position = 800
            motor_1_task.encoder.position = 800
            motor_1_task.control.actual = 800
            motor_1_task.control.setpoint = 800
            motor_2_task.position = 0
            motor_2_task.encoder.position = 0
            motor_2_task.control.actual = 0
            motor_2_task.control.setpoint = 0
            cal = False
        else:
            print('Incorrect input')
    
    run_wait = True
    while run_wait == True:
        answer = io_funcs.get_input(str,'Run? [y/n] ')
        if answer == 'n':
            print('Let me know when you want to run.')
        elif answer == 'y':
            print('Starting printing')
            run_wait = False
        else:
            print('Incorrect input')
    
    # Initializing a servo task and a command task
    servo_task = cotask.Task(servo_func, name = 'Servo Task', priority=1,
                             period = 50, profile = True)
    command_task = cotask.Task(command_func, name = 'Command Task', priority=2,
                             period = 50, profile = True)
    cotask.task_list.append(servo_task)
    cotask.task_list.append(command_task)
    servo_state = ''

    # Running Main Printing
    vcp = pyb.USB_VCP ()    
    end = False
    gc.collect()
    # gc.enable()
    while not vcp.any () or end == False:
        # Run until key press
        try:
            cotask.task_list.pri_sched ()
        except:
            motor_1_task.motor.set_duty_cycle(0)
            motor_2_task.motor.set_duty_cycle(0)
            end = True
    # Turning off the motors before ending
    motor_1_task.motor.set_duty_cycle(0)
    motor_2_task.motor.set_duty_cycle(0)
    print('Ending program')
    # Always close the file!
    file.close()
