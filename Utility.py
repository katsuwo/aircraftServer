import datetime

def getTimeStamp():
    return datetime.datetime.now().timestamp()

def clearScreen():
    print('\x1b[2', end="")

def setCursor(x,y):
    print('\x1b[{0};{1}H'.format(str(x),str(y)), end="")
