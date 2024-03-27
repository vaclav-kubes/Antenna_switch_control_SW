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
            ser.write(bytes("!!\n", "ascii"))  #send "!!" to MCU via serial comm. - writing and reading from ser. line is blockng!
            #print(ser.in_waiting)
            ser.flush() #wait unitl everithing was written to ser. line
            #print(ser.in_waiting)
            ser.reset_input_buffer()#clean the input buffer !!!does not work for some reason
            #print(ser.in_waiting)
            ser.readline()
            msg = ser.read(2)   #read two bytes recieved from ser. line
            print("RX: ", msg)    

    except:     
        return False    #if there is problem (mainly with opening the serial port) return Flase
    try:
        if str(msg,"ascii") == "YE":    #if recieved string coressponds to "YE" return True
            return True
        else:
            return False  #else there is probbable error on the line and return False
    except:
        return False
    
def serial_start(com):
    """Opens serial communication at given COM port and returns instantion of serial class.
    
        Args:
            com (str): COM port where the MCU is connected
        Returns: 
            serial insatnce/bool: if connection estabilished then instance of serial class is returned otherwise false is returned
    """
    #serial comm. settings are: baudrate = 9600, no parity, 8 bit, one stopbit, reading timeout 2 sec
    try:
        ser = s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 5, dsrdtr = True)
        ser.dtr = False #stop reset after serial comm. initialization 
        time.sleep(0.05)
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
        print("TX: ", bytes(data, "ascii"))
        ser.write(bytes(data, "ascii")) #string must be converted to bytes and then are sent to ser. line
        ser.flush()
        #ser.reset_input_buffer()
        #print(ser.readline())
        time.sleep(0.09)
        
        #print(ser.in_waiting)
        
        #print(ser.in_waiting)
        #ser.flushInput()
        return True
    except:
        return False

def serial_read(ser):
    """Reads bytes recieved from serial line until end of line character has occured.
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            byte/bool: Returns recieved bytes if no exception has occured otherwise returns False
    """
    try:
        #print(ser.in_waiting)
        #print(ser.readline())
        ser.readline()
        #print(ser.in_waiting)
        msg = ser.readline()    #read bytes from serial input buffer untill "\n"
        print("RX: ", msg)
        return msg
    except:
        return None
    
def get_temp_A(ser):
    """Request temperature from A board through serial line (writes "TA" to ser. line and wait until line was received)
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "TAxx.x\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "TA\n"), serial_read(ser))

def get_temp_B(ser):
    """Request temperature from B board through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "TBxx.x\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "TB\n"), serial_read(ser))

def get_curr_A(ser):
    """Request measured current to LNAs from A board through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "IAxxx.x\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "IA\n"), serial_read(ser))

def get_curr_B(ser):
    """Request measured current to LNAs from B board through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "IBxxx.x\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "IB\n"), serial_read(ser))

def get_compass(ser):
    """Request measured antenna orintation through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "ECxxx.x\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "EC\n"), serial_read(ser))

def get_fant_U(ser):
    """Request measured phantom voltage through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "FUxx.xx\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "FU\n"), serial_read(ser))

def get_ant(ser):
    """Request currently switch on antennas through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "ANx...\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "AN\n"), serial_read(ser))

def get_b_pressence(ser):
    """Request B board presence indication through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "CBx\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "CB\n"), serial_read(ser))

def get_all(ser):
    """Request all measurements and data through serial line
    
        Args:
            ser (serial instance): Serial instance serial class representing estabilished serial comm. at given COM port.
        Returns:
            tuple: (True/False whether writing to ser. line was succesful, byte - recieved line "IA,IB,TA,TB,FU,EC,AN,CB\n"/bool - False if there was exception)
    """
    return (serial_write(ser, "AL\n"), serial_read(ser))

def extract_val(data):
    """Auxiliary function to extract values from string recieved from ser. line
        
        Args:
            data (byte): recieved data in byte format
        Returns: 
            float/list/None: if there is just one value to extract then it returns float,
                                if there is more than one value to extract then retut list of floats
                                if some exceptation has occured then return None
    """
    try:
        if len(data) > 10:  #if there is more values to extract then
            data_r = []
            for n in str(data, encoding = "ascii")[:-1].split(","): #parse given string at commas and create list
                data_r.append(float(n)) #for each item in list convert string to float number and add it to final list of values
            return data_r   #return list of float
        else:
            return float(str(data, encoding = "ascii")[2:-1]) #if there is just one value to extract then encode bytes to ascii and cut out first two and last characters and return float
    except:
        return None

def available_com():
    """Function to search for available COM ports.
        
        Args: 
            None
        Returns: 
            list: List of string names of available COM ports
    """
    ports = serial.tools.list_ports.comports()
    ports_list = []
    for port in sorted(ports):
        ports_list.append(port.device)
    return ports_list

def write_read(com, data):
    """Function to write data to ser. line and then read from ser. line

        Args: 
            com (str): COM port to estabilish ser. comm. and write data to
            data (str): String whitch will be written to ser. line
        Returns:
            string/bool: if there was no exceptation during writing and reading it returns read line from ser. line otherwise it returns False
    """
    try:
        ser = s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 3, dsrdtr=True)
        ser.dtr = False
        time.sleep(0.1)
        ser.write(bytes(data, encoding = "ascii"))
        ser.flush()
        msg = ser.readline()
        ser.close()
    except:
        msg = False
    return msg

