#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Print message 'Hello, world!'.

:author LAL npacxx <npacxx@lal.in2p3.fr>
:date   March 2015
"""

import sys

# By convention, a function name must contain only lowercase characters and _.
# string=None defines a default value for string and makes it optional.
def print_msg(string=None):
    """Print a message received as an argument or a default message
    if none is passed.

    :param string: a string to print (optional)
    :return: status value (always success, 0)
    """

    if string is None:
        # Define a default message
        string = 'Hello, world!'

    print("%s" % string)
    return 0


# Implement the main code as a function to avoid PyLint complaints about
# global variables
def main():
    """
    Main part of the application: ask the user a message to print as a succession
    of lines and print it.

    :return: always success (0)
    """

    messages = []
    read_more = True
    while read_more:
        line = input('Enter a line or RETURN to complete input: ')
        if line == '':
            read_more = False
            messages.append(line)
        else:
            messages.append(line)

    for line in messages:
        print_msg(line)

    # Always return success
    return 0


# The following test is considered as a best practice: this way a module
# can be used both as a standalone application or as a module called by another
# module.
if __name__ == "__main__":

    # The main program is implement mainly as a function: this avoids having
    # all the variables used in this context (e.g. string in print_msg) to
    # become global variables.
    # Always return success
    sys.exit(main())
