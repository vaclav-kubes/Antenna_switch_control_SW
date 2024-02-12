"""Module for serial communication with MCU
"""

import serial as s  #importing serial module
import serial.tools.list_ports  #importing tool to scan COM ports from serial module 
import time #importing time module

def ping(com):
    """Ping function to try if MCU is connected to the comport and if it responds.
        Args: 
            com: Serial communication object.
        Returnns:
            bool: True if MCU is responding/ False if MCU is not responding
    """
    #try to open serial port at given COM with bd = 9600
    #timeout reading is set to 3 sec, prepare for turn off reset after starting serial comm.  
    try: 
        with s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 3, dsrdtr = True) as ser: # open serial port
            ser.dtr = False #reset after initiation of ser. comm. is turned off
            time.sleep(0.1) #give the MCU some time 
            msg = 0
            ser.write(bytes('!', "ascii"))  #send '!' to MCU via serial comm.
            ser.flush() #wait unitl everithing was written to ser. line
            #time.sleep(0.1)
            msg = ser.read(2)   #read two bytes recieved from ser. line
            ser.reset_input_buffer()    #clean the input buffer
            #print(str(msg, "utf-8"))
            #print(msg)
    except:     
        return False    #if there is problem (mainly with opening the serial port) return Flase
    
    if str(msg,"ascii") == "YE":    #if recieved string coressponds to "YE" return True
        return True
    else:
        return False  #else there is probbable error on the line and return False


def serial_start(com):
    """Opens serial communication at given COM port and returns instantion of serial class.
    Args:
        com (str): COM port where the MCU is connected
    Returns: 
        serial insatnce/bool: if connection estabilished then instance of serial class is returned otherwise false is returned
    """
    #serial comm. settings are: baudrate = 9600, no parity, 8 bit, one stopbit, reading timeout 2 sec
    try:
        ser = s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 2, dsrdtr = True)
        ser.dtr = False #stop reset after serial comm. initialization 
        time.sleep(0.1)
        #ser.write(b"AL")
        #print(ser.readline())
        #print(ser)
        return ser #return serial class insatnce of created ser. comm.
    except:
        return False    #if there was problem with estabilishing connection. then return false


def serial_write(ser, data):
    """Writes given string to goven serial comm. port.
    Args:
        ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
    Returns:
        bool: True if data was written without exceptation otherwise returns False
    """
    try:
        ser.write(bytes(data, "ascii")) #string must be converted to bytes and then are sent to ser. line
        #print(a)
        ser.flush()
        time.sleep(0.07)
        #ser.flushOutput()
        return True
    except:
        return False



def serial_read(ser):
    try:
        msg = ser.readline()
        #ser.flushInput()
        #print(msg)
        return msg
    except:
        return None
    
def get_temp_A(ser):
   return (serial_write(ser, "TA"), serial_read(ser))

def get_temp_B(ser):
   return (serial_write(ser, "TB"), serial_read(ser))

def get_curr_A(ser):
   return (serial_write(ser, "IA"), serial_read(ser))

def get_curr_B(ser):
   return (serial_write(ser, "IB"), serial_read(ser))

def get_compass(ser):
   return (serial_write(ser, "EC"), serial_read(ser))

def get_fant_U(ser):
   return (serial_write(ser, "FU"), serial_read(ser))

def get_ant(ser):
   return (serial_write(ser, "AN"), serial_read(ser))

def get_all(ser):
   return (serial_write(ser, "AL"), serial_read(ser))

def get_b_pressence(ser):
   return (serial_write(ser, "CB"), serial_read(ser))

def extract_val(data):
    print(data)
    try:
        if len(data) > 10:
            data_r = []
            for n in str(data, encoding = "ascii")[:-1].split(","): 
                data_r.append(float(n))
            return data_r    
        else:
            return float(str(data, encoding = "ascii")[2:-1])
    except:
        return None

def available_com():
    ports = serial.tools.list_ports.comports()
    ports_list = []
    for port in sorted(ports):
        ports_list.append(port.device)
    return ports_list

def write_read(com, data):
    try:
        ser = s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 3, dsrdtr=True)
        ser.dtr = False
        time.sleep(0.1)
        ser.write(bytes(data, encoding = "ascii"))
        ser.flush()
        #print(bytes(data, encoding = "ascii"))
        #time.sleep(0.5)
        msg = ser.readline()
        #print(msg)
        ser.close()
    
    except:
        msg = False
    return msg

