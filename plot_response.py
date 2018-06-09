'''
@file plot_response.py 
This file takes in a csv file.
It will take only the two first columns of data and plot it. 
Other things will be ignored or deleted.

The order it works is:
1. Open file
2. Read all the lines
3. Close the file
4. For every line
    If the line has no numbers, ignore
    For character in line
        If it is a digit, comma, or period, it stays, else skip
    Split the left over string with the commas
    If there are less than 2 points skip
    If each element is a number, add to data points temp list
    Another check to make sure there are more than two data points
    If less than two, skip
    Else, add the first two numbers to the x and y data list

The file can be changed for the correct file name.
This file is setup for a step respone and finding the time constant of the 
step response.
'''

from matplotlib import pyplot
# Importing pyplot from matplotlib

# File name
file_name = 'response_2.csv'

# Open the file as eric_file in read mode
file = open(file_name,'r')

'''
A list for another possible way to eliminate unnecessary things:
The idea is to:

if c is in eliminate then ignore
'''
eliminate = ['', ' ','\t']

# Empty x data list
x = []

# Empty y data list
y = []

# Reading the file to get all the lines. Returns a list
lines = file.readlines()

# Close the file since it is no longer needed
file.close()

# Making a list of all the final points
final_points = []

for line in lines:
    # For ever line in all the lines (which are actually elements of a list)    
    
    # Making a string with all the characters needed 
    line_string = ''
    # for every line in all the lines
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
    x.append(list_of_points[0])
    # The second point is the y point
    y.append(list_of_points[1])

# Plotting
x.pop(-1)
y.pop(0)

delta_v = (max(y)-min(y))
delta_v_tau = delta_v*0.632
# https://stackoverflow.com/questions/9706041
# Finding the index of the value closest to delta_v in the voltage array
index = min(range(len(y)), key=lambda i: abs(y[i]-delta_v_tau))
tau = x[index]

string = '$\\tau$ = {:.4f} [s]\n$\\Delta$V = {:.4f} [V]\n0.632*$\\Delta$V = {:.4f} [V]'.format(tau,delta_v,delta_v_tau)
pyplot.text(tau,delta_v_tau,string,horizontalalignment='left',verticalalignment='top')
pyplot.plot(x,y, '-k', [0, tau], [delta_v_tau, delta_v_tau], 'k:',[tau, tau], [0, delta_v_tau], 'k:')
pyplot.xlabel('Time [s]')
pyplot.ylabel("Voltage [V]")
pyplot.show()

