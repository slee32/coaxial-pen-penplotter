''' @file parse_hpgl.py
This program takes in hpgl file and parses it into a list of commands and 
parses it into a list of commands and positions. It takes only hpgl files with
paths in them. It returns a list with the commands and coordinates for relevant
commands. The more high resolution of the x,y coordinates the better.

There is also a command for writing all the commands to a txt file as well
as converting the coordinates into units to inches.

This python file can be run with the system args of the input file, output file
and the resolution of the hpgl file.

The file can be run like this:
@code
python parse_hpgl.py drawing.hpgl print.txt 1016

@endcode

where the first argument is the input file, second the output, and the last the
resolution. 

If the coordinates need to be parsed in encoder ticks. Use like this:

@code
python parse_hpgl.py a.hpgl a.txt 5 3200 8.11 10.08 0.5 14
@endcode

The arugments for this are the hpgl file to be parsed, the output text file,
the resolution, the CPR of the motors, the length of arm 1, length of arm 2
the x_0 of the paper space, and lastly the y_0 origin of the paper space.


There may be an error in the coord to ticks function

@author Samuel Lee
@copyright Samuel Lee 

'''

import sys
import math

def parse_file(file_name, res, state=0, CPR=0, L1=0, L2=0, x_0=0, y_0=0):
    ''' 
    Takes in a file name for a hpgl file and parses it into a list.
    A raw hpgl file has text that looks as follows:
    
    IN;SP1;PU0,0;PD0,90;PU487,751;PD492,749
    
    the first two letters determines the code command. 
    Each command has a certain amount of parameters thereafter that represent
    a particular setting or position.
    
    Each command is separated by a ';'
    
    For more information on hpgl code refer to
    @link http://www.isoplotec.co.jp/HPGL/eHPGL.htm @endlink
    
    It returns a list with elements that look like this:
    
    Units are in inches.
    
    MAKE SURE THE RESOLUTION IS THE CORRECT. Default resolution in most hpgl
    code is 1016.
    
    The first entry is tne command, second is the number of points for that
    command, and the rest are the position coordinates.
    
    ['IN;1; 0x0']
    ['SP;1; 0x0']
    ['PU;1;', '1183x327']
    ['PD;1;', '1183x710']
    ['PU;1;', '1175x701']
    ['PD;14;', '1175x709',...
    ['PU;1;', '1183x238']
    ['SP;1; 0x0']
    ['IN;1; 0x0']
    
    If state = 1 and all the correct arguments are supplied, it will convert
    the hpgl into encoder ticks needed to draw the picture.
    
    @param file_name The hpgl file name 'names.hpgl'
    @param resolution The resolution of the hpgl file in dpi.
    @param state 0 is for convert to inches, 1 to change to encoder ticks
    @param CPR Counts of ticks per one revolution of the output shaft
    @param L1 Length of arm 1 [in]
    @param L2 Length of arm 2 [in]
    @param x_0 x orign of the paper space in respect to global fram [in] 
    @note Origin is top left corner of paper
    @param y_0 y orign of the paper space in respect to global fram [in]
    @return parsed_list List of command, nested list with command & parameters
    '''
    pre_tick = 1000
    pre_angle = 90
    # Determining if the code is a file already or a str for the file name.
    if type(file_name) == str:
        file = open(file_name, 'r')
    else:
        file = file_name
    # Read the file text
    string_file = file.readline()
    # Close the file    
    file.close()
    # Split by every command
    all_list = string_file.split(';')
    # Delete the last split which is a newline character
    del all_list[-1]
    # Initialize the list for the parsed results
    parsed_list = []
    # For every command in the hpgl code
    for n in all_list:
        # The first two letters of the element determine the command
        cmd = n[:2]
        if len(n)>2:
            # Some commands do not have arguments (e.g. IN)
            # This makes the commands that do have arguments have numbers
            numbers = n[2:]
            
        if cmd == 'IN':
            # Initialize for go to home
            #IN_list = ['IN;'+str(1)+';']
            #if state == 1:
                #origin, pre_tick = coord_to_ticks([[0,0]],CPR,L1,L2,x_0,y_0,pre_tick)
                #IN_list.extend(origin)
            #parsed_list.append(IN_list)
            IN_list = ['IN;'+str(1)+'; 0x0']
            parsed_list.append(IN_list)
        elif cmd == 'SP':
            # Select Pen and a zero zero which does not have a purpose but 
            # placed just to have a consistent format
            SP_list = ['SP;'+str(1)+'; 0x0']
            parsed_list.append(SP_list)
        elif cmd == 'PU':
            # Pen Up and the coordinate at which to bring the pen up
            coordinates = numbers.split(',')
            print(coordinates)
            # List of the PU command and number of coordinates
            PU_list = ['PU;'+str(len(coordinates)/2)+';']
            # Converting into inches
            inch_coords = [float(point) / res for point in coordinates]
            # Pairing up the coordinates
            paired_coords = pair_split(inch_coords)
            if state == 1:
                # If the state is 1, set change to ticks
                coordinates,pre_tick, pre_angle = coord_to_ticks(paired_coords,CPR,L1,L2,x_0,y_0,pre_tick,pre_angle)
            else: 
                coordinates = paired_coords
            PU_list.extend(coordinates)
            # Adds the coordinates (x,y) in as lists
            parsed_list.append(PU_list)
        elif cmd == 'PD':
            # Pen Down and the coordinates to move the pen
            coordinates = numbers.split(',')
            print(coordinates)
            # PD command list and coordinates
            PD_list = ['PD;'+str(len(coordinates)/2)+';']
            # Convert into inches
            inch_coords = [float(point) / res for point in coordinates]
            # Split into pairs and list
            paired_coords = pair_split(inch_coords)
            if state == 1:
                coordinates, pre_tick, pre_angle = coord_to_ticks(paired_coords,CPR,L1,L2,x_0,y_0,pre_tick, pre_angle)
            else: 
                coordinates = paired_coords
            PD_list.extend(coordinates)
            # Adds the coordinates (x,y) in as lists
            parsed_list.append(PD_list)
        else:
            print('Error, unknown command')
    return parsed_list

def pair_split(iterable):
    ''' 
    A quick function to split a list and pair up elements in a list.
    This is particular to a list of floats and returns the coordinates
    as tuples
    @param iterable A list of floats of paired x,y coordinates (x1,y1,x2,y2)
    @return list_of_pairs Returns a list of list of the coordinates
    '''
    list_of_pairs = []
    i = 0
    # While loop to pair up list
    while i < len(iterable):
        list_of_pairs.append([float(iterable[i]),float(iterable[i+1])])
        i += 2 
    return list_of_pairs
    
def output_text(hpgl, file_name):
    ''' 
    A function to output to a text file
    @param hpgl A list of commands from parsed_list
    @param file_name The output file name, extension '.txt' file must be included.
    '''
    if type(file_name) == str:
        file = open(file_name, 'w')
    else:
        file = file_name
    # Write each command to the file with a newline at the end
    for n in hpgl:
        file.write(str(n)+'\n')
    file.close()
    
def coord_to_ticks(coords,CPR,L1,L2,x_0,y_0,pre_tick, pre_angle):
    '''
    Converts coordinates into ticks for an encoder, particularly for a
    coaxial 2DOF pen plotter.
    @param CPR Counts of ticks per one revolution of the output shaft
    @param L1 Length of arm 1 [in]
    @param L2 Length of arm 2 [in]
    @param x_0 x orign of the paper space in respect to global fram [in]
    @param y_0 y orign of the paper space in respect to global fram [in]
    @param pre_angle the inital angle the plotter begins [degrees]
    @return tick_list List of tick pairs, nested list with ticks
    '''
    tick_list = []
    # for every point in the coordinates list
    for point in coords:
        x = x_0+point[0]
        y = y_0-point[1]
        # Adjust to be in reference of global reference frame
        print('Global',x,y)
        L3 = math.sqrt(x**2+y**2)
        # Length from global origin to pen
        #print(pre_tick)
        theta_1 = math.degrees(math.atan2(y,x)+math.acos((L1**2-L2**2+L3**2)/(2*L1*L3)))
        
        delta_theta = (theta_1-pre_angle)
        
        theta_2 = math.degrees(math.pi-math.acos((L1**2+L2**2-L3**2)/(2*L1*L2)))
        
        if delta_theta>=0:
            theta_2 = theta_2-abs(delta_theta)
        elif delta_theta<0:
            theta_2 = theta_2+abs(delta_theta)
            
        ticks_1 = int(round(CPR*theta_1/360))
        delta = 0
        #delta = abs(ticks_1 - pre_tick)
        pre_angle = theta_1
        pre_tick = ticks_1
        #print(ticks_1)
        if delta>=0:
            ticks_2 = int(round(CPR*theta_2/360))-delta
        elif delta<0:
            ticks_2 = int(round(CPR*theta_2/360))+delta
        tick_list.append(str(ticks_1)+'x'+str(ticks_2))
    return tick_list,pre_tick, pre_angle
    

if __name__ == '__main__':
    file = sys.argv[1]
    output = sys.argv[2]
    res = int(sys.argv[3])
    
    if len(sys.argv)<=4:
        x = parse_file(file,res)
        output_text(x,output)
        print('hpgl code from '+file+' (res '+str(res)+') is parsed in '+output)
    elif len(sys.argv)==9:
        CPR = int(sys.argv[4])
        L1 = float(sys.argv[5])
        L2 = float(sys.argv[6])
        x_0 = float(sys.argv[7])
        y_0 = float(sys.argv[8])
        x = parse_file(file,res,state=1,CPR=CPR,L1=L1,L2=L2,x_0=x_0,y_0=y_0)
        output_text(x,output)
        print('hpgl code from '+file+' (res '+str(res)+') is parsed in '+output)
        print('\nConverted into ticks of for two arm')
    else:
        print('Incorrect amount of system arguments\n')
        print('Number of system arguments supplied = '+str(len(sys.argv)))
    
    
    