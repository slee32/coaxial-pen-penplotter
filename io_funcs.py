''' 
@file io_funcs.py
@author Sam Lee

An input and output functions file with various functions for
getting input and also outputting data. Including a class for an InputError
Exception.

One future development would be to make the get_input function to also take in
limits that the input must be in and raise errors for inputs out of the 
specified range. Also, the custom input error needs to be developed more.
'''


def get_input(type_needed, message):
    ''' 
    This function is a general looping function that gets user input 
    for a particular type needed.
    @param type_needed The object type needed (e.g. str, list, dict)
    @param message The message you want to display to get input
    @return user_input The correct user input. If none,return None
    '''
    # List of types     
    list_of_types = [list, str, int, float]
    if type_needed in list_of_types:
        # If the type needed is in the list of types, get the correct index
        type_index = list_of_types.index(type_needed)
    else:
        # If the type is not in list of types
        print('Type not found')
        return
    
    # Input flow control boolean
    input_loop = True
    while input_loop == True:
        try:
            # Get user input and the message for the input
            user_input = input(str(message))
            if user_input == '' or None:
                # If the user input is nothing return none
                return None
            # Else, convert the type to the type needed using the correct index    
            user_input = list_of_types[type_index](user_input)
            # Break from loop
            input_loop = False
        except:
            # When user input is the wrong type
            print('Incorrect input type. The needed input type is: ' 
            +str(type_needed)+'. Please try again.')
    return user_input

def output_csv(data,file):
    '''
    This function is not yet made but was aiming to write a list into a txt.
    '''
    print('Outputting data')


class InputError(Exception):
    ''' 
    This is a custom exception error for incorrect user input.
    '''
    def __init__(self, message, errors):
        ''' 
        This method initializes the input error.
        @param message The message you want to display to get input
        @param errors The errors for a particular input error
        '''

        ## Call the base class constructor with the parameters it needs
        super(InputError, self).__init__(message)

        ## Errors for a particular InputError
        self.errors = errors

