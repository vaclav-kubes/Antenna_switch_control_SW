import serial as s
import serial.tools.list_ports
import time

def ping(com):
    try:
        with s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 3, dsrdtr = True) as ser: # open serial port
            ser.dtr = False
            time.sleep(0.1)
            msg = 0
            ser.write(bytes('!', "ascii"))
            ser.flush()
            #time.sleep(0.1)
            msg = ser.read(2) 
            ser.reset_input_buffer()
            #print(str(msg, "utf-8"))
            #print(msg)
    except:
        return False
    
    if str(msg,"ascii") == "YE":
        return True
    else:
        return False  


def serial_start(com):
    try:
        ser = s.Serial(port = com, baudrate = 9600, parity = s.PARITY_NONE, bytesize = s.EIGHTBITS, stopbits = 1, timeout = 2, dsrdtr = True)
        ser.dtr = False
        time.sleep(0.1)
        #ser.write(b"AL")
        #print(ser.readline())
        #print(ser)
        return ser
    except:
        return False


def serial_write(ser, data):
    try:
        ser.write(bytes(data, "ascii"))
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

