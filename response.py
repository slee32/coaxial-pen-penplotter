''' 
@file response.py
response file for which runs step response tests by sending a signal through 
the USB serial port to the MicroPython board, reading the resulting data,
and plotting the step response. 
'''

from matplotlib import pyplot 
import serial
import time


time_out = []
actual_out = []
    
with serial.Serial('/dev/ttyACM0', 115200, timeout=5) as ser_port:
    # Setting up a serial port
    # Flushing the port to start fresh
    ser_port.flush()
    time.sleep(0.1)
    ser_port.write(b'\r') 
    # Write a return carriage
    lines = ser_port.readlines()
    ser_port.close()
    # Close the port since it is no longer needed.
for line in lines:
    line = line.decode('UTF-8')
    line_string = ''
    if line == '' or (not any(char.isdigit() for char in line)):
        # If the line is blank or there are no numbers in the line
        # https://stackoverflow.com/questions/19859282/
        # NOTE: The code actually works without this if statement,
        # but I thought it was an interesting and cool line anyway.
        continue
        # Simply go to the next line    
    for c in line:
        # For every character in the line
        if c.isdigit() or c == ',' or c == '.':
            # If the character is a number, comma, or period, += line_string
            line_string += c
        else:
            # Else, ignore that character
            continue
    # Get all the data points by splitting by the comma
    points = line_string.split(',')
    if len(points)<2:
        # If there are less than 2 data points ignore the line
        continue
    # Temporary list of points
    list_of_points = []

    for point in points:
        # For every point in points
        try:
            # Try to append as a float
            list_of_points.append(float(point))
        except:
            continue
            
    if len(list_of_points)<2:
        # If there is not a pair of data points, skip the line
        continue
    # The first point is the x point
    time_out.append(list_of_points[0])
    # The second point is the y point
    actual_out.append(list_of_points[1])

print(time_out)
print(actual_out)


pyplot.plot(time_out,actual_out,'k')
pyplot.xlabel('Time [ms]')
pyplot.ylabel("Encoder Ticks [Ticks]")
pyplot.show()
