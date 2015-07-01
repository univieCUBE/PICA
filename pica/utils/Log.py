"""
Module for printing status messages.

@author: Norman MacDonald
@date: 2010-02-16
"""
import sys
import datetime

def log(message,blnQuiet = False):
    """Log a message to a file, and optionly to the screen if blnQuiet is False."""
    return
    message = str(datetime.datetime.now()) + "\t" + str(message)
    i = sys.argv[0].rfind("\\")
    scriptname = sys.argv[0][i+1:]
    logfile = open("logfile-%s.txt"%(scriptname),"a")
    if not blnQuiet:
        print message
    logfile.write(message + "\n")
    logfile.close()
