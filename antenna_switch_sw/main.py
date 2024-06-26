"""
Control program for five chanell antenna switch with diagnostics.

Version 1.5

Author: Václav Kubeš

"""

#==================== Modules import ====================
from tkinter import *
import CTkMessagebox as msg
import customtkinter as cstk
import win32ui
import dde
from serial_com import *
import time
import threading
import queue
import datetime
import webbrowser
import sys
import os
#==================== Functions definitions ====================
def log_error():
    """Write down diagnostic data to error_logs CSV file.
    """
    try:
        now = datetime.datetime.now()
        t = now.strftime("%d/%m/%Y %H:%M:%S")   #get current date and time
        with open("error_logs.csv", "r", encoding = "utf-8") as file:   #does the file error_logd exist?
            pass
        with open("error_logs.csv", "a", encoding = "utf-8") as file:   #open the file and append date and time and diag. data there
            file.write(t + ',' + cur_A_TK.get() + ',' + cur_B_TK.get() + ',' + temp_A_TK.get() + ',' + temp_B_TK.get() + ',' + fant_volt_TK.get() + ',' + orientation_TK.get() + ','+ ant_TK.get() + '\n')
    except: #if the file doesnt exist then create new and append the heather and  diag. data
      with open("error_logs.csv", "a", encoding = "utf-8") as file:
            file.write("Time,Curr. to A, Curr. to B,Temp. of A,Temp. of B,Voltage,Ant. azimuth,Switched ant.\n")
            file.write(t + ',' + cur_A_TK.get() + ',' + cur_B_TK.get() + ',' + temp_A_TK.get() + ',' + temp_B_TK.get() + ',' + fant_volt_TK.get() + ',' + orientation_TK.get() + ','+ ant_TK.get() + '\n')
              

def switch_ant():
    """Send the command to switch antennas to the switch via ser. line."""
    global ant_old
    
    ant_new = ant_TK.get().strip()
    
    if ant_old != ant_new:  #switch only if there is change
        threading.Thread(target = ant_set, args = [ant_new], daemon = True).start() #call the ant_set fun in new thread
        ant_old = ant_new


def ant_set(antenna):
    """Writes the command to switch ant. to ser. line.
        arg: (string) antenna
    """
    while not q_done.get(): #wait until other serial writings are done
        q_done.task_done()
        time.sleep(0.3)

    q_done.put(False) #block other serial writings until writing is done

    serial_write(ser_com, "AN"+ antenna.strip().replace(" ", "") + '\n')
    try:
        if str(int(extract_val(serial_read(ser_com)))) != antenna:    #if switch respond with different antenna then there is error
            log_error()
    except:
        log_error()

    q_done.put(True) #writing to ser. line is done
    q_done.task_done()


def evaluate_state(type_of_data, data):
    """Auxiliary function to check if diag. data are in given range.
        
        Args:
            type_of_data (str): "IA" for current to LNAs at A board,
                                "IB" for current to LNAs at B board,
                                "TA" for temp. on A board,
                                "TB" for temp. on B board,
                                "U" for phantom voltage,
                                "C" for antenna azimuth,
            data (float): evaluated data
        Returns:
            bool: True - data are out of range /False - data are in range
    """
    global config_or
    try:
        if type_of_data == "IA":
            if data >= float(max_cur_A.get()): #the range is given by the values from config file, can be set in app settings
                return True
            else:
                return False
        elif type_of_data == "IB":
            if data >= float(max_cur_B.get()):
                return True
            else:
                return False
        elif type_of_data == "U":
            if data > float(max_u_fant.get()) or data < float(min_u_fant.get()):
                return True
            else:
                return False
        elif type_of_data == "TA":
            if data > float(max_temp_p_A.get()) or data < float(max_temp_n_A.get()):
                return True
            else:
                return False
        elif type_of_data == "TB":
            if data > float(max_temp_p_B.get()) or data < float(max_temp_n_B.get()):
                return True
            else:
                return False
        elif type_of_data == "C":
            if data > float(config_or[:-2]) + float(max_az_dev.get()) or data < float(config_or[:-2]) - float(max_az_dev.get()):
                return True
            else:
                return False
    except:
        return True


def on_closing():
    """Auxiliary function which is called after clicking on X"""
    try:
        
        ant_set("0")
        ser_com.close() #end ser. comm. properly
        s.Shutdown()    #end dde server properly
        app.destroy()   #close main window and end the app
    except:
        app.destroy()   #close main window and end the app


def read_U_I():
    """Request for current values of currnet to LNAs at the A and B board and phantom voltage via ser. line."""
    global ser_com
    while not q_done.get(): #wait until other writings to ser. line are done
        q_done.task_done()
        time.sleep(0.3)

    q_done.put(False)   #block other writings until these are done

    IA = extract_val(get_curr_A(ser_com)[1])    #request IA IB and UF and extract float values
    IB = extract_val(get_curr_B(ser_com)[1])
    UF = extract_val(get_fant_U(ser_com)[1])
    
    q_done.put(True)    #writing to ser line is done
    q_done.task_done()

    q_UI.put(IA)    #save the values to queues
    q_UI.put(IB)
    q_UI.put(UF)
    q_UI.task_done()
    
    error_state = q_state.get() #get list of error states of all values
    error_state[0] = evaluate_state("IA", IA)   #write evaluation of the data to error state list
    if B_connected.get():
        error_state[1] = evaluate_state("IB", IB)
    else:
        error_state[1] = False
    error_state[2] = evaluate_state("U", UF)
    q_state.put(error_state)
    q_state.task_done()
    
    update_current_voltage()

    if True in error_state: #if there is an error in list of error states
        state.set("Warning!")   #then warning is diplayed
        entry_11.configure(text_color = "red")
        log_error() #error is logged to csv file
    else:
        state.set("Normal state") #else normal state is displayed
        entry_11.configure(text_color = "green")

    #highlight error values by turning them red or unhighlight them if values are ok
    if error_state[0]:
        entry_5.configure(text_color = "red")       
    elif entry_5.cget("text_color") == "red":
        entry_5.configure(text_color = "black")

    if error_state[1]:
        entry_8.configure(text_color = "red")  
    elif entry_8.cget("text_color") == "red":
        entry_8.configure(text_color = "black") 
    
    if error_state[2]:
        entry_4.configure(text_color = "red") 
    elif entry_4.cget("text_color") == "red":
        entry_4.configure(text_color = "black") 


    t = threading.Timer(function = read_U_I, interval = delay_read_UI)  #this function calls itself after given time 
    t.daemon = True
    t.start()
    

def read_temp():
    """Request for current values of temperature of A and B board via ser. line."""
    while not q_done.get():
        q_done.task_done()
        time.sleep(0.3)
  
    q_done.put(False)
    TA = extract_val(get_temp_A(ser_com)[1])
    TB = extract_val(get_temp_B(ser_com)[1])
    q_done.put(True)
    
    q_temp.put(TA)
    q_temp.put(TB)
    q_temp.task_done()    

    error_state = q_state.get()
    error_state[3] = evaluate_state("TA", TA)
    error_state[4] = evaluate_state("TB", TB)
    q_state.put(error_state)
    q_state.task_done()

    if True in error_state:
        log_error()
        state.set("Warning!")
        entry_11.configure(text_color = "red")
    else:
        state.set("Normal state")
        entry_11.configure(text_color = "green")

    update_temp()

    if error_state[3]:
        entry_6.configure(text_color = "red")
    elif entry_6.cget("text_color") == "red":
        entry_6.configure(text_color = "black")

    if error_state[4]:
        entry_9.configure(text_color = "red")
    elif entry_9.cget("text_color") == "red":
        entry_9.configure(text_color = "black")


    t = threading.Timer(function = read_temp, interval = delay_read_T + 0.2)
    t.daemon = True
    t.start()


def read_orient():
    """Request for current value of azimuth of antennas via ser. line."""
    while not q_done.get():
        q_done.task_done()
        time.sleep(0.3)
    q_done.put(False)
    
    EC = extract_val(get_compass(ser_com)[1])
    q_done.put(True)
    q_done.task_done()
    
    q_orient.put(EC)
    q_orient.task_done()
    
    error_state = q_state.get()
    error_state[5] = evaluate_state("C", EC)
    q_state.put(error_state)
    q_state.task_done()

    if True in error_state:
        log_error()
        state.set("Warning!")
        entry_11.configure(text_color = "red")
    else:
        state.set("Normal state")
        entry_11.configure(text_color = "green")

    update_orintation()

    if error_state[5]:
        entry_7.configure(text_color = "red") 
    elif entry_7.cget("text_color") == "red":
        entry_7.configure(text_color = "black") 

    t = threading.Timer(function = read_orient, interval = delay_read_C + 0.3)
    t.daemon = True
    t.start()


def update_current_voltage():
    """Function to display new values of current and phantom voltage."""
    try:
        data_A = q_UI.get() #retrieve data from qeue
        data_B = q_UI.get()
        data_V = q_UI.get()
        q_UI.task_done()

        if data_A != None and data_B != None and data_V != None:    #if there are some data 
            cur_A_TK.set("{:.1f}".format(data_A))   #display the data
            cur_B_TK.set("{:.1f}".format(data_B))
            fant_volt_TK.set("{:.1f}".format(data_V))
            if switch_com_TK.get() == "Switch: Disconnected":
                switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")
    
    except:
        pass    #if queue is empty then do nothing
    
    #app.after(delay_read_UI * 1000 + 3500, update_current_voltage)  #this fun is called every given time


def update_temp(): 
    """Function to display new values of temperature."""
    try:
        data_A = q_temp.get()
        data_B = q_temp.get()
        q_temp.task_done()

        if data_A != None and data_B != None:
            temp_A_TK.set("{:.1f}".format(data_A))
            temp_B_TK.set("{:.1f}".format(data_B))
            if switch_com_TK.get() == "Switch: Disconnected":
                switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")
    except:
        pass

    #app.after(delay_read_T * 1000 + 3000, update_temp)


def update_orintation(): 
    """Function to display new values of ant. orientation."""
    try:
        data = q_orient.get()
        q_orient.task_done()

        if data != None:
            orientation_TK.set("{:.1f}".format(data) + " °")
            if switch_com_TK.get() == "Switch: Disconnected":
                switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")
    
    except:
        pass

    #app.after(delay_read_C * 1000 + 3000, update_orintation)


def update_data_from_switch(): 
    """Request all diagnostic data from swtich via ser. line. Data includes: [IA, IB, TA, TB, UF, EC, AN, CB]."""
    global ant_old
    global ser_com
    if ser_com: #if serial comm. exists
        while not q_done.get():
            q_done.task_done()
            time.sleep(0.3)
        q_done.put(False)

        data = extract_val(get_all(ser_com)[1])
        q_done.put(True)
        try:
            cur_A_TK.set("{:.1f}".format(data[0]))
            cur_B_TK.set("{:.1f}".format(data[1]))
            temp_A_TK.set("{:.1f}".format(data[2]))
            temp_B_TK.set("{:.1f}".format(data[3]))
            fant_volt_TK.set("{:.1f}".format(data[4]))
            orientation_TK.set("{:.1f}".format(data[5]) + " °")
            ant_TK.set("{:n}".format(data[6]))  #get the currently switched on anntena 
            ant_old = "{:n}".format(data[6])
            B_connected.set(bool(data[7]))
            if not data[7]:
                entry_8.configure(fg_color= "#dedede")  
                entry_9.configure(fg_color= "#dedede")


        except:
            pass

        switch_ant()    #if there is need then switch the antenna

        try:
            error_state = q_state.get()
            error_state[0] = evaluate_state("IA", data[0])
            if not data[7]:
                error_state[1] = False
            else:
                error_state[1] = evaluate_state("IB", data[1])
            error_state[2] = evaluate_state("U", data[4])
            error_state[3] = evaluate_state("TA", data[2])
            error_state[4] = evaluate_state("TB", data[3])
            error_state[5] = evaluate_state("C", data[5])
            q_state.put(error_state)
            q_state.task_done()
        
            if True in error_state:
                state.set("Warning!")
                entry_11.configure(text_color = "red")
            else:
                state.set("Normal state")
                entry_11.configure(text_color = "green")
            
            if error_state[0]:
                entry_5.configure(text_color = "red")

            elif entry_5.cget("text_color") == "red":
                entry_5.configure(text_color = "black")

            if error_state[1]:
                entry_8.configure(text_color = "red")  

            elif entry_8.cget("text_color") == "red":
                entry_8.configure(text_color = "black") 

            if error_state[2]:
                entry_4.configure(text_color = "red") 

            elif entry_4.cget("text_color") == "red":
                entry_4.configure(text_color = "black") 

            if error_state[3]:
                entry_6.configure(text_color = "red")

            elif entry_6.cget("text_color") == "red":
                entry_6.configure(text_color = "black")

            if error_state[4]:
                entry_9.configure(text_color = "red")

            elif entry_9.cget("text_color") == "red":
                entry_9.configure(text_color = "black")

            if error_state[5]:
                entry_7.configure(text_color = "red") 

            elif entry_7.cget("text_color") == "red":
                entry_7.configure(text_color = "black") 
        except:
            pass


        if switch_com_TK.get() == "Switch: Disconnected":
            switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")

    return


def B_conn_set():
    """Gray out the label boxes with diag. data IA and TB if selected tha B unit is not connected if yes then evaluate the data."""
    if B_connected.get():
        entry_8.configure(fg_color= "white")  
        entry_9.configure(fg_color= "white")
        try:
            IB = float(cur_B_TK.get())
            TB = float(temp_B_TK.get())
            values_exist = True
        except:
            values_exist = False
        
        if values_exist:
            error_state = q_state.get()
            error_state[1] = evaluate_state("IB", IB)
            error_state[4] = evaluate_state("TB", TB)
            q_state.put(error_state)
            q_state.task_done()
            if True in error_state:
                state.set("Warning!")
                entry_11.configure(text_color = "red")
            else:
                state.set("Normal state")
                entry_11.configure(text_color = "green")
            if error_state[1]:
                entry_8.configure(text_color = "red")  

            elif entry_8.cget("text_color") == "red":
                entry_8.configure(text_color = "black") 
            
            if error_state[4]:
                entry_9.configure(text_color = "red")

            elif entry_9.cget("text_color") == "red":
                entry_9.configure(text_color = "black")
    else:
        entry_8.configure(fg_color= "#dedede", text_color = "black")  
        entry_9.configure(fg_color= "#dedede", text_color = "black")
        error_state = q_state.get()
        error_state[1] = False
        error_state[4] = False
        q_state.put(error_state)
        q_state.task_done()
    

def switch_set_off():
    """To switch off all antennas and current to LNAs."""
    checkbtn_1.configure(state = "disabled")
    checkbtn_2.configure(state = "disabled")
    checkbtn_3.configure(state = "disabled")
    checkbtn_4.configure(state = "disabled")
    checkbtn_5.configure(state = "disabled")
    deselect_manal_chckbtn()
    ant_TK.set('0')
    switch_ant()


def auto_on():
    """Auxiliary function to disable checkbuttons if auto switching is on."""
    deselect_manal_chckbtn()
    checkbtn_1.configure(state = "disabled")
    checkbtn_2.configure(state = "disabled")
    checkbtn_3.configure(state = "disabled")
    checkbtn_4.configure(state = "disabled")
    checkbtn_5.configure(state = "disabled") 
    ant_TK.set(str(auto_select_ant()))
    switch_ant()


def manual_on():
    """Auxiliary function to enable checkbuttons if manual switching is on."""
    checkbtn_1.configure(state = "normal") 
    checkbtn_2.configure(state = "normal")
    checkbtn_3.configure(state = "normal")
    checkbtn_4.configure(state = "normal")
    checkbtn_5.configure(state = "normal")
    deselect_manal_chckbtn()


def deselect_manal_chckbtn():
    """Reset check buttons for manual antennas selection"""
    ant1_on.set(False)  #reset previous settings
    ant2_on.set(False)
    ant3_on.set(False)
    ant4_on.set(False)
    ant5_on.set(False)


def checkbtn_fun():
    """Auxiliary function to enable only three checkbuttons to be on."""
    i = 0
    ant_str = ""
    if(checkbtn_1.get()): 
        i = i + 1
        ant_str += " 1"
    if(checkbtn_2.get()):
        i = i + 1   
        ant_str += " 2" 
    if(checkbtn_3.get()):
        i = i + 1
        ant_str += " 3"
    if(checkbtn_4.get()):
        i = i + 1
        ant_str += " 4"
    if(checkbtn_5.get()):
        i = i + 1  
        ant_str += " 5"    
    if i == 0:
        ant_str = "0"

    if(i >= 3):
        if(not checkbtn_1.get()): checkbtn_1.configure(state = 'disabled')
        if(not checkbtn_2.get()): checkbtn_2.configure(state = 'disabled')
        if(not checkbtn_3.get()): checkbtn_3.configure(state = 'disabled')
        if(not checkbtn_4.get()): checkbtn_4.configure(state = 'disabled')
        if(not checkbtn_5.get()): checkbtn_5.configure(state = 'disabled')
    else:
        checkbtn_1.configure(state = 'normal')
        checkbtn_2.configure(state = 'normal')
        checkbtn_3.configure(state = 'normal')
        checkbtn_4.configure(state = 'normal')
        checkbtn_5.configure(state = 'normal')
    ant_TK.set(ant_str)
    switch_ant()    #according to antennas picked by checkbuttons switch the antennas


def update_data_from_orbitron():
    """Request data from Orbitron DDE server and process them. Choose and swtich the antenna according to them."""
    dde_data.set(c.Request("TrackingData")) #request tracking data from Orbitron
    data = dde_data.get()   #and save them to variable

    az = get_AZ_EZ("AZ", data)  #extracting the azimuth from the tracking data
    el = get_AZ_EZ("EL", data)  #extracting the elevation from the tracking data

    if len(data) > 2:   #if received data are valid
        azimut_TK.set(az)   #display them
        elevation_TK.set(el)
        if orbitron_conn_TK.get() == "Orbitron: No data":
            orbitron_conn_TK.set("Orbitron: Connected")
        if auto_switch.get() == 1:
            ant_TK.set(str(auto_select_ant()))
            switch_ant()    #switch the antenna
    else:
        if orbitron_conn_TK.get() == "Orbitron: Connected":
            orbitron_conn_TK.set("Orbitron: No data")

    app.after(500, update_data_from_orbitron)   #this fun is called every 500 ms
    

def check_conn_orbitron():
    """Check if Orbitron app is runing and try to connect to it."""
    try:
        c.ConnectTo("Orbitron", "Tracking")
        if c.Connected() == 1:  #if connection was created
            orbitron_conn_TK.set("Orbitron: Connected")
            update_data_from_orbitron() #get tracking data from Orbitron
        else:
            orbitron_conn_TK.set("Orbitron: Not running")
            s.Shutdown()
            app.after(2500, check_conn_orbitron)    #if Orbitron is ton running then check it after 2.5 sec
    except:
        orbitron_conn_TK.set("Orbitron: Not running")
        app.after(2500, check_conn_orbitron)


def get_AZ_EZ(select, data):
    """Auxiliary function to extract data from Orbitron tracking data string.
    
        Args:
            select (str): "AZ if azimuth should be extracted,
                            "EL" if elevation should be extracted
            data (str): String from Orbitron
        Returns:
            string: Azimuth in string format ended by " °"/ Elevation in string format " °"
    """
            
    if select == "AZ":
        pos = data.find("AZ")
        azimut = data[pos + 2 : pos + 7]
        if "  " in azimut:
            azimut = azimut[:-2] + " °"
        elif " " in azimut:
            azimut = azimut[:-1] + " °"
        else:
            azimut += " °"
        azimut = azimut.replace(',', '.')
        
        return azimut
    
    elif select == "EL":
        pos = data.find("EL")
        if data[pos + 2] == "-":
            elevation = data[pos + 2 : pos + 7]
            if " " in elevation:
                elevation = elevation[:-1] + " °"
            else:
                elevation += " °"
        else:
             elevation = data[pos + 2 : pos + 6]
             if " " in elevation:
                elevation = elevation[:-1] + " °"
             else:
                elevation += " °"
        elevation = elevation.replace(',', '.')        
        return elevation


def auto_select_ant():
    """Auxiliary function to decide whitch antenna should be switched on according to tracking data.
        
        Returns:
            int: number corresponding to selected antenna"""
    try:
        ant_orientation = float(orientation_manual_TK.get()[:-2])
        az = float(azimut_TK.get()[:-1])
        el = float(elevation_TK.get()[:-1])
        el_treshold = elevation_treshold_TK.get()
        #360° is divided to 4 quadrants according to antenna orientation
        #according to currnet tracking data the antenna is selected
        ant = 0
        if el_treshold == 91:   #if el. treshold is set to "still ON" then only ant 5 is on
            ant = 5
        elif el_treshold != 0:
            if el < el_treshold and el > 0:   #if el is under the el treshold for ant 5 then use other antennas according to azimuth
                ant = az_to_ant_eval(ant_orientation, az)
            elif el <= 0: 
                ant = 0
            else:
                ant = 5
        elif el_treshold == 0:
            if el > 0:   #if el is under the el treshold for ant 5 then use other antennas according to azimuth
                ant = az_to_ant_eval(ant_orientation, az)
            elif el <= 0:
                ant = 0
        else:
            ant = 0

        return ant
    except:
        return 0


def az_to_ant_eval(ant_orientation:float, az:float):
    """To assign the correct antenna to satellite position according to its azimuth and ant. orientation
        Args: 
            ant_orientation (float): azimuth og antenna 1
            az (float): azimuth of satellite 
        Return: 
            (string) selected antenna(s)"""
    
    ant = 0
    if not coupling.get():  #if coupling is not in use
        pos = divmod(divmod(az - ant_orientation, 360)[1] + 45, 90)[0]  #enumerate which antenna should be, used modulo used to "rotate the antena" and then to devide 360 to 4 parts
        ant = (int(pos) % 4) + 1
    else: #if coupling is in use
        pos = divmod(divmod(az - ant_orientation, 360)[1] + 45/2, 45)[0]
        ant_list = [1, 12, 2, 23, 3, 34, 4, 41]
        ant = ant_list[int(pos) % 8]
    return ant


def ant_orientation_set_a():
    """Set the antenna orientation to current orientation read from switch and save it to config file."""
    if switch_com_TK.get() == "Switch: Connected":  #if the switch is connected
        global config_or
        val = entry_7.get() #retrieve the currnetly displlayed orientation
        if val == None: #if it is empty, end
            return
        
        orientation_manual_TK.set(val)  #set the display the value
        config_or = val
        error_state = q_state.get()
        error_state[5] = evaluate_state("C", float(val[:-2]))   #check for error if the orinetation is out of given range
        q_state.put(error_state)
        q_state.task_done()

        if True in error_state:
            state.set("Warning!")
            entry_11.configure(text_color = "red")
        else:
            state.set("Normal state")
            entry_11.configure(text_color = "green")

        if error_state[5]:
            entry_7.configure(text_color = "red") 
        elif entry_7.cget("text_color") == "red":
            entry_7.configure(text_color = "black") 

        try:    #write new value of antenna or. to config file
            with open("config.txt", "r", encoding = "utf-8") as config:
                content = config.readlines()
                config.close()
                content[0] = val + "\n"    
            with open("config.txt", "w", encoding = "utf-8") as config:
                config.writelines(content)
                config.close()
        except:
            config = open("config.txt", "x", encoding = "utf-8")    #if config file dosnt exist then create new
            config.write("\n")
            config.write(val + "\n")
            config.close()

        msg.CTkMessagebox(message = "Antenna azimuth was set!", title = "Antenna azimuth set")  #pop up message that seting was succesful
    else:
        msg.CTkMessagebox(message = "No data", title = "No data from switch!")  #pop up message that seting was not succesful


def ant_orientation_set_m():
    """Function to set antenna orinetation. Set value is saved to confgi file."""
    global config_or
    dialog = cstk.CTkInputDialog(text="Type in an azimuth of antenna:", title="Manual antenna orientation setting") #pop up dialog with manual entry of antenna orientation
    val = dialog.get_input()    #retrieve the value from the dialog
    if val == None: #if no data from dialog then end this func
        return
    text = ''
    for i in val:   #extract only numbers from the dialog input 
        if ord(i) >= 48 and ord(i) <= 57 or ord(i) == 46:
            text += i
        elif ord(i) == 44:
            text += '.' #change "," to "."
    try:
        dev = float(text)   #try to convert string value to float
        if dev > 360.0 or dev < 0.0:    #check if given value is in the range
            msg.CTkMessagebox(title="Invalid range", message="Azimuth should be in range from 0° to 360°.", icon = "warning")
        else:
            orientation_manual_TK.set(text + " °")  #display newly set value of antenna or.
            config_or = text + " °"

            error_state = q_state.get() #check the error state
            cur_az = orientation_TK.get()
            if cur_az:
                error_state[5] = evaluate_state("C", float(cur_az[:-2]))
                q_state.put(error_state)
                q_state.task_done()
                if True in error_state:
                    state.set("Warning!")
                    entry_11.configure(text_color = "red")
                else:
                    state.set("Normal state")
                    entry_11.configure(text_color = "green")

                if error_state[5]:
                    entry_7.configure(text_color = "red") 
                elif entry_7.cget("text_color") == "red":
                    entry_7.configure(text_color = "black") 

            try:    #write down newly set antenna or.
                with open("config.txt", "r", encoding = "utf-8") as config:
                    content = config.readlines()
                    config.close()
                content[0] = text + " °\n"    
                with open("config.txt", "w", encoding = "utf-8") as config:
                    config.writelines(content)
                    config.close()
            except:
                config = open("config.txt", "x", encoding = "utf-8")
                config.writelines([text + " °\n", "\n", "\n", "\n", "\n", "\n", "\n", "\n", "\n", "\n"])
                config.close()
    except:
        msg.CTkMessagebox(title="No change.", message="No change.")


def com_select(choice:str):
    """Function called after selcting from option menu. Tries to connect to selected COM port. 
        Args:
            choice (str): selected COM port from option menu
    """
    global ser_com
    try:
        ser_com.close()
    except:
        pass

    if not com_menu.cget("values") or '' in com_menu.cget("values") or "??" in com_menu.cget("values"):
        ports = available_com()
        if ports:
            com_menu.configure(values = ports)
        else:
            com_menu.configure(values = ["??"])
    if ping(choice):    #if MCU is responding on given COM port
        try:
            with open("config.txt", "r", encoding = "utf-8") as config: #save the selected COM port to config file
                content = config.readlines()    #at first we have to read the content of config file
                config.close()  
                if len(content) == 1:   #if there is just one line in config file we append the COM port at the end of the file
                    content.append(choice + "\n")
                else:
                    content[1] = choice + "\n"  #if there is more lines the we owerwrite second line 
                try:
                    with open("config.txt", "w", encoding = "utf-8") as config: #save changes into config file
                        config.writelines(content)
                        config.close()
                except:
                    msg.CTkMessagebox(title="Settings not saved.", message="Settings not saved. Unable to write to configuration file.")
            
            ser_com = serial_start(choice)  #start ser. comm. on given COM port
            
            try:    #because the queues are loaded with None values if there is no ser. comm. it must be emptied before valid values will be loaded
                while not q_UI.empty():
                    q_UI.get()
                q_UI.task_done()
            except:
                pass
                  
            try:
                while not q_temp.empty():
                    q_temp.get()                   
                q_temp.task_done()
            except:
                pass

            try:
                while not q_orient.empty():
                    q_orient.get()
                q_orient.task_done()
            except:
                pass
        
            if ser_com:
                switch_com_TK.set("Switch: Connected")   
                t = threading.Timer(function = update_data_from_switch, interval = 0.7)
                t.daemon = True
                t.start()  
                #threading.Thread(target = update_data_from_switch, daemon = True).start()   #request all diag. data from switch
        except:
            try:
                with open("config.txt", "w", encoding = "utf-8") as config: #if there is no config file, then create new one
                    config.writelines(["\n", choice + "\n"])
                    config.close()
            except:
                msg.CTkMessagebox(title="Settings not saved.", message = "Settings not saved. Error while saving the serial port setting.")
    else:
        switch_com_TK.set("Switch: Disconnected")


def create_new_window():
    """Create settings window with widgets."""
    btn_3.configure(state = "disabled") #disable opening of another same window
    try:
        with open("config.txt", "r", encoding = "utf-8") as config: #if there are limit values saved in config file then load them
            content = config.readlines()
            config.close()
        max_cur_A.set(content[2][:-1])  #new line character is cutt of by [:-1]
        max_cur_B.set(content[3][:-1])
        max_temp_n_A.set(content[4][:-1])
        max_temp_p_A.set(content[5][:-1])
        max_temp_n_B.set(content[6][:-1])
        max_temp_p_B.set(content[7][:-1])
        max_az_dev.set(content[8][:-1])      
        min_u_fant.set(content[9][:-1])
        max_u_fant.set(content[10][:-1])
        B_connected.set(bool(float(content[11][:-1])))
        elevation_treshold_TK.set(int(float(content[12][:-1])))
    except: #otherwise load default values
        max_cur_A.set("650")
        max_cur_B.set("650")
        max_temp_n_A.set("-10")
        max_temp_p_A.set("50")
        max_temp_n_B.set("-10")
        max_temp_p_B.set("50")
        max_az_dev.set("10")
        B_connected.set(False)
        max_u_fant.set("12")
        min_u_fant.set("7")
        elevation_treshold_TK.set(70)

    change_el_treshold(elevation_treshold_TK.get())

    app_set_range = cstk.CTkToplevel(app)   #create new window
    app_set_range.geometry("500x750")
    app_set_range.minsize(width = 500, height = 750)
    app_set_range.title("Set error tresholds")
    app_set_range.focus()
    #photo = PhotoImage(file = "icon.ico")
    #app_set_range.iconphoto(False, photo)
    #app_set_range.iconbitmap(default = False, bitmap = "icon.ico")

    #pack the window with labels and entrys
    L_title = cstk.CTkLabel(app_set_range, text = "Settings", font = ("Cambria", 17, "bold"), anchor = "center")
    L_title.grid(column = 0, columnspan = 2, row = 0, sticky = "NSEW")

    L_set_current_A = cstk.CTkLabel(app_set_range, text = "Set error treshold for current to LNAs on A board [mA]:", font = ("Cambria", 14, "bold"))
    L_set_current_A.grid(column = 0, columnspan = 2, row = 1, padx = 50, pady = 2, sticky = "NSEW")

    E_set_current_A = cstk.CTkEntry(app_set_range, textvariable = max_cur_A, font = ("Cambria", 14))
    E_set_current_A.grid(column = 0, columnspan = 2, row = 2, padx = 50, sticky = "NSEW")

    L_set_current_B = cstk.CTkLabel(app_set_range, text = "Set error treshold for current to LNAs on B board [mA]:", font = ("Cambria", 14, "bold"))
    L_set_current_B.grid(column = 0, columnspan = 2, row = 3, padx = 50, pady = 2, sticky = "NSEW")

    E_set_current_B = cstk.CTkEntry(app_set_range, textvariable = max_cur_B, font = ("Cambria", 14))
    E_set_current_B.grid(column = 0, columnspan = 2, row = 4, padx = 50, sticky = "NSEW")

    L_set_temp_n_A = cstk.CTkLabel(app_set_range, text = "Set lower error treshold for temperature of A board [°C]:", font = ("Cambria", 14, "bold"))
    L_set_temp_n_A.grid(column = 0, columnspan = 2, row = 5, padx = 50, pady = 2, sticky = "NSEW")

    E_set_temp_n_A = cstk.CTkEntry(app_set_range, textvariable = max_temp_n_A, font = ("Cambria", 14))
    E_set_temp_n_A.grid(column = 0, columnspan = 2, row = 6, padx = 50, sticky = "NSEW")

    L_set_temp_p_A = cstk.CTkLabel(app_set_range, text = "Set upper error treshold for temperature of A board [°C]:", font = ("Cambria", 14, "bold"))
    L_set_temp_p_A.grid(column = 0, columnspan = 2, row = 7, padx = 50, pady = 2, sticky = "NSEW")

    E_set_temp_p_A = cstk.CTkEntry(app_set_range, textvariable = max_temp_p_A, font = ("Cambria", 14))
    E_set_temp_p_A.grid(column = 0, columnspan = 2, row = 8, padx = 50, sticky = "NSEW")

    L_set_temp_n_B = cstk.CTkLabel(app_set_range, text = "Set lower error treshold for temperature of B board [°C]:", font = ("Cambria", 14, "bold"))
    L_set_temp_n_B.grid(column = 0, columnspan = 2, row = 9, padx = 50, pady = 2, sticky = "NSEW")

    E_set_temp_n_B = cstk.CTkEntry(app_set_range, textvariable = max_temp_n_B, font = ("Cambria", 14))
    E_set_temp_n_B.grid(column = 0, columnspan = 2, row = 10, padx = 50, sticky = "NSEW")

    L_set_temp_p_B = cstk.CTkLabel(app_set_range, text = "Set upper error treshold for temperature of B board [°C]:", font = ("Cambria", 14, "bold"))
    L_set_temp_p_B.grid(column = 0, columnspan = 2, row = 11, padx = 50, pady = 2, sticky = "NSEW")

    E_set_temp_p_B = cstk.CTkEntry(app_set_range, textvariable = max_temp_p_B, font = ("Cambria", 14))
    E_set_temp_p_B.grid(column = 0, columnspan = 2, row = 12, padx = 50, sticky = "NSEW")

    L_set_dev_az = cstk.CTkLabel(app_set_range, text = "Set error treshold for deviation from antenna azimuth [°]:", font = ("Cambria", 14, "bold"))
    L_set_dev_az.grid(column = 0, columnspan = 2, row = 13, padx = 50, pady = 2, sticky = "NSEW")

    E_set_dev_az = cstk.CTkEntry(app_set_range, textvariable = max_az_dev, font = ("Cambria", 14))
    E_set_dev_az.grid(column = 0, columnspan = 2, row = 14, padx = 50, sticky = "NSEW")
    
    L_set_n_U = cstk.CTkLabel(app_set_range, text = "Set lower error treshold for phantom voltage [V]:", font = ("Cambria", 14, "bold"))
    L_set_n_U.grid(column = 0, columnspan = 2, row = 15, padx = 50, pady = 2, sticky = "NSEW")

    E_set_n_U = cstk.CTkEntry(app_set_range, textvariable = min_u_fant, font = ("Cambria", 14))
    E_set_n_U.grid(column = 0, columnspan = 2, row = 16, padx = 50, sticky = "NSEW")

    L_set_p_U = cstk.CTkLabel(app_set_range, text = "Set upper error treshold for phantom voltage [V]:", font = ("Cambria", 14, "bold"))
    L_set_p_U.grid(column = 0, columnspan = 2, row = 17, padx = 50, pady = 2, sticky = "NSEW")

    E_set_p_U = cstk.CTkEntry(app_set_range, textvariable = max_u_fant, font = ("Cambria", 14))
    E_set_p_U.grid(column = 0, columnspan = 2, row = 18, padx = 50, sticky = "NSEW")

    L_set_B_conn = cstk.CTkLabel(app_set_range, text = "B board is connected:", font = ("Cambria", 14, "bold"))
    L_set_B_conn.grid(column = 0, columnspan = 2, row = 19, padx = 50, pady = 2, sticky = "NSEW")

    CH_set_B_conn = cstk.CTkCheckBox(app_set_range, variable = B_connected, onvalue = True, offvalue = False, text = "Yes", font = ("Cambria", 14, "bold"), command = B_conn_set)
    CH_set_B_conn.grid(column = 0, columnspan = 2, row = 20, padx = 15, pady = 2)#, sticky = "EW"

    L_slider_EL = cstk.CTkLabel(app_set_range, text = "Set elevation treshold for ant. 5 [°]:", font = ("Cambria", 14, "bold"))
    L_slider_EL.grid(column = 0, columnspan = 2, row = 21, padx = 50, pady = 2, sticky = "NSEW")

    slider_EL_set = cstk.CTkSlider(app_set_range, from_ = 0, to = 91, number_of_steps = 91, variable = elevation_treshold_TK, width = 60, command = change_el_treshold)
    slider_EL_set.grid(column = 0, row = 22, padx = 50, pady = 2, sticky = "EW")

    L_slider_val_EL = cstk.CTkLabel(app_set_range, textvariable = L_TK_elevation, font = ("Cambria", 14, "bold")) #slider to set treshold of elevation for ant 5
    L_slider_val_EL.grid(column = 1, row = 22, padx = 50, pady = 2, sticky = "NSEW")

    B_set = cstk.CTkButton(app_set_range, text = "Save", font = ("Cambria", 14), command = lambda: set_tresholds(app_set_range))
    B_set.grid(column = 0, row = 23, padx = 20, pady = 10, sticky = "NSEW")

    B_close = cstk.CTkButton(app_set_range, text = "Close", font = ("Cambria", 14), command = lambda: close_settings(app_set_range))
    B_close.grid(column = 1, row = 23, padx = 20, pady = 10, sticky = "NSEW")

    app_set_range.protocol("WM_DELETE_WINDOW", lambda:close_settings(app_set_range))    #set what should happend if this window is closed
    app_set_range.after_idle(app_set_range.lift)    #make sure that the window is on top


def change_el_treshold(value):
    if value == 91:
        L_TK_elevation.set("Only ant. 5")
    elif value == 0:
        L_TK_elevation.set("OFF")
    else:
        L_TK_elevation.set(str(int(value)))


def set_tresholds(app_set_range):
    """Called after clicking on set button in Settings window. 
    It makes sure that entered values are valid and highlights the wrong ones.
    
        Args: 
            app_set_range (instance of window): Settings window
    """
    wrong_entry = []
    value_list = []

    for n in app_set_range.children.keys(): #for each widget in settings window
        if "entry" in n or "checkbox" in n or "slider" in n: #if the name of widget contains entry or checkbox
            try:
                text_value = app_set_range.children[n].get()    #get the value of the widget
                if isinstance(text_value, str): #if the value is string
                    text_value = text_value.replace(',', '.').strip('\n')   #replace eventual "," with "." and cut out end of line
                value = float(text_value)
                if ('4' in n or '6' in n) and (value < value_list[-1]): #upper limits of temperature must be higher then lower limits
                    value_list.append(None)
                    raise Exception()
                elif ('2' in n or  n =='!ctkentry') and value < 20: #currne to LNAs must bi higher then 20mA
                    value_list.append(None)
                    raise Exception()
                elif '7' in n and value < 0:    #deviation from antenna azimuth must be positive
                    value_list.append(None)
                    raise Exception()
                elif '8' in n and value < 0:    #lower value of phantom voltage must be bigger then 0 V
                    value_list.append(None)
                    raise Exception()
                elif '9' in n and (value < value_list[-1]) or ('9' in n and value < 0): #upper value of phantom voltage limit must be higher than lowwer value
                    value_list.append(None)
                    raise Exception()
                
                value_list.append(value)

                wrong_entry.append(False)

            except:
                app_set_range.children[n].configure(text_color = "red")
                wrong_entry.append(True)
   #write down changes in settings
    try:    
        with open("config.txt", "r", encoding = "utf-8") as config:
            content = config.readlines()
            config.close()
        
        for n in range(len(value_list)):
            try:
                if not wrong_entry[n]:
                    content[n + 2] = str(value_list[n]) + "\n"
            except:
                if not wrong_entry[n]:
                    content.append(str(value_list[n]) + "\n")
                else:
                    content.append("\n")

        with open("config.txt", "w", encoding = "utf-8") as config:
            config.writelines(content)
            config.close()
    except:
        config = open("config.txt", "x", encoding = "utf-8")
        content = ["\n", "\n"]
        for n in range(len(value_list)):
            if wrong_entry[n]:
                content.append(str(value_list[n]) + "\n")
            else:
                content.append("\n")
        config.writelines(content)
        config.close()
    
    if True in wrong_entry: #if there is not allowed value then pop up info dialog
        msg.CTkMessagebox(title="Error", message="Invalid value!")
    else:
        if ser_com: #there are diag. data then check if they are in newly set ranges 
            error_state = q_state.get()
            error_state[0] = evaluate_state("IA", float(cur_A_TK.get()))
            if B_connected.get():
                error_state[1] = evaluate_state("IB", float(cur_B_TK.get()))
                error_state[4] = evaluate_state("TB", float(temp_B_TK.get()))
            else:
                error_state[1] = False
                error_state[4] = False
            error_state[2] = evaluate_state("U", float(fant_volt_TK.get()))
            error_state[3] = evaluate_state("TA", float(temp_A_TK.get()))
            error_state[5] = evaluate_state("C", float(orientation_TK.get()[:-2]))
            q_state.put(error_state)
            q_state.task_done()

            if True in error_state:
                state.set("Warning!")
                entry_11.configure(text_color = "red")
            else:
                state.set("Normal state")
                entry_11.configure(text_color = "green")
            
            if error_state[0]:
                entry_5.configure(text_color = "red")

            elif entry_5.cget("text_color") == "red":
                entry_5.configure(text_color = "black")

            if error_state[1]:
                entry_8.configure(text_color = "red")  

            elif entry_8.cget("text_color") == "red":
                entry_8.configure(text_color = "black") 

            if error_state[2]:
                entry_4.configure(text_color = "red") 

            elif entry_4.cget("text_color") == "red":
                entry_4.configure(text_color = "black") 

            if error_state[3]:
                entry_6.configure(text_color = "red")

            elif entry_6.cget("text_color") == "red":
                entry_6.configure(text_color = "black")

            if error_state[4]:
                entry_9.configure(text_color = "red")

            elif entry_9.cget("text_color") == "red":
                entry_9.configure(text_color = "black")

            if error_state[5]:
                entry_7.configure(text_color = "red") 

            elif entry_7.cget("text_color") == "red":
                entry_7.configure(text_color = "black") 
            
        close_settings(app_set_range)
    

def close_settings(app_set_range):
    """Called on settings window closing. Enables clickability of app settings button.
    """
    btn_3.configure(state = "normal")   #after closing the setting window, enable app settings button to be clicked
    app_set_range.destroy() #close settings window


def app_info():
    """Open github readme in the browser."""
    webbrowser.open('https://github.com/vaclav-kubes/Antenna_switch_control_SW/blob/main/README.md')


def src_path(rel_path):
    """Retrieve absolute path to file for dev and for PyInstaller otherwise icon wont load"""
    try:
        b_path = sys._MEIPASS
    except:
        b_path = os.path.abspath(".")

    return os.path.join(b_path, rel_path)


#==================== Creation of Main window ====================
cstk.set_appearance_mode("System")
app = cstk.CTk()    #creating the main window of the app
app.geometry("630x590")
app.minsize(width = 630, height = 590)

try:
    app.iconbitmap(True, src_path('icon.ico'))
except:
    pass

app.title("Antenna switch controller")

app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)
app.rowconfigure(0, weight=1)
app.rowconfigure(1, weight=1)
app.rowconfigure(2, weight=1)
app.rowconfigure(3, weight=1)

#==================== Declaration of variables ====================
#declaring the TKinter variables for widgets
auto_switch = cstk.IntVar(value = 1)
ant1_on = cstk.BooleanVar()
ant2_on = cstk.BooleanVar()
ant3_on = cstk.BooleanVar()
ant4_on = cstk.BooleanVar()
ant5_on = cstk.BooleanVar()
coupling = cstk.BooleanVar()
dde_data = cstk.StringVar()
azimut_TK = cstk.StringVar()
elevation_TK = cstk.StringVar()
orientation_TK = cstk.StringVar()
orbitron_conn_TK = cstk.StringVar()
ant_TK = cstk.StringVar()
switch_com_TK = cstk.StringVar()
com_TK = cstk.StringVar()
temp_A_TK = cstk.StringVar()
temp_B_TK = cstk.StringVar()
cur_A_TK = cstk.StringVar()
cur_B_TK = cstk.StringVar()
fant_volt_TK = cstk.StringVar()
orientation_manual_TK = cstk.StringVar()
state = cstk.StringVar(value = "Waiting for data...")
max_cur_A = cstk.StringVar()
max_cur_B = cstk.StringVar()
max_temp_n_A = cstk.StringVar()
max_temp_n_B = cstk.StringVar()
max_temp_p_A = cstk.StringVar()
max_temp_p_B = cstk.StringVar()
max_az_dev = cstk.StringVar()
B_connected = cstk.BooleanVar()
max_u_fant = cstk.StringVar()
min_u_fant = cstk.StringVar()
elevation_treshold_TK = cstk.IntVar()
L_TK_elevation = cstk.StringVar()
#switch_off = cstk.BooleanVar()

#declaring variables
list_com = []
config_com = ""
ant_old = 0
delay_read_UI = 30#60 #time for requesting new diagnostic data in sec
delay_read_T = 300
delay_read_C = 900
dde_con = False

#declaring queue for data handover between threads
q_UI = queue.Queue()
q_temp = queue.Queue()
q_orient = queue.Queue()
q_done = queue.Queue()
q_done.put(True)
q_state = queue.Queue()
q_state.put([False, False, False, False, False, False])

#==================== Actions at start of app ====================
#creating the dde client to connect to Orbitron dde server
s = dde.CreateServer()  #create a DDE client and start conversation
s.Create("GetData") #GetData client
c = dde.CreateConversation(s)   #create a conversation between client and server

try:
    c.ConnectTo("Orbitron", "Tracking") #connecting to Orbitron dde to request tracking data
    if c.Connected() == 1: #if connection is succesfull
        dde_con = True #first data request is allowed
        orbitron_conn_TK.set("Orbitron: Connected") #indicate that Orbitron is opened in main app window
    else:
        azimut_TK.set("00") #if Orbitron app is not opened yet then set values to 0
        elevation_TK.set("00")
        orbitron_conn_TK.set("Orbitron: Not running")
        s.Shutdown()
except:
    orbitron_conn_TK.set("Orbitron: Not running")
    azimut_TK.set("00")
    elevation_TK.set("00")



try: #try to open configuration file and retrieve the config. data: ant. orintation, COM port, limit values for error warning
    config = open("config.txt", "r", encoding = "utf-8")
    config_or = config.readline()
    orientation_manual_TK.set(config_or)
    config_com = config.readline()
    max_cur_A.set(config.readline().strip("\n"))
    max_cur_B.set(config.readline().strip("\n"))
    max_temp_n_A.set(config.readline().strip("\n"))
    max_temp_p_A.set(config.readline().strip("\n"))
    max_temp_n_B.set(config.readline().strip("\n"))
    max_temp_p_B.set(config.readline().strip("\n"))
    max_az_dev.set(config.readline().strip("\n"))
    min_u_fant.set(config.readline().strip("\n"))
    max_u_fant.set(config.readline().strip("\n"))
    B_connected.set(bool(float(config.readline().strip("\n")+'0')))
    elevation_treshold_TK.set(int(float(config.readline().strip("\n"))))
    config.close()
    
except: #if config file doesnt exist create new file and write there default values for limits of diagn. data, COM port and ant. or. is left empty for further writing
    config = open("config.txt", "x", encoding = "utf-8")
    config.writelines(["\n","\n", "650\n", "650\n", "-10\n", "50\n", "-10\n", "50\n", "10\n", "7\n", "12\n", "0\n", "70\n"])
    config.close()
    max_cur_A.set("650")
    max_cur_B.set("650")
    max_temp_n_A.set("-10")
    max_temp_p_A.set("50")
    max_temp_n_B.set("-10")
    max_temp_p_B.set("50")
    max_az_dev.set("10")
    max_u_fant.set("12")
    min_u_fant.set("7")
    B_connected.set(False)
    elevation_treshold_TK.set(70)

get_com = available_com()   #get available COM ports

if not (get_com and config_com): #if list of COM ports is empty and there is COM port in config file
    list_com.append(config_com[:-1]) #append COM port from config file to option menu 
    com_TK.set(config_com[:-1])
elif get_com and config_com:   #if there are COM ports available then put them to option menu
    list_com.append(config_com[:-1]) 
    for one_com in get_com:
        if one_com != config_com[:-1]:
            list_com.append(one_com)
    com_TK.set(list_com[0])
else:
    com_TK.set("??")

if config_com: #if there is COM port in config file 
    if ping(config_com[:-1]):   #try to ping to device on that COM port
        switch_com_TK.set("Switch: Connected") #if ping is succesfull indicate that switch is connected
        ser_com = serial_start(config_com[:-1])
        first_data = True   #first requesting data from switch is allowed
    else:
        switch_com_TK.set("Switch: Disconnected")
        ser_com = None
        first_data = False
else:
    switch_com_TK.set("Switch: Disconnected")
    ser_com = None
    first_data = False


#==================== Main window widgets ====================
#place title of the aplication
label_1 = cstk.CTkLabel(app, text = "Antenna switch controller", font = ("Cambria", 20, "bold"), anchor = "center")
label_1.grid(column = 0, row = 0, columnspan = 2, sticky = "NSEW")
app.grid_rowconfigure(0, weight = 1)

#create frame for displaying data from Orbitron
fr_sat_pos = cstk.CTkFrame(app, width=200, height=200)
fr_sat_pos.grid(column = 0, row = 1, padx = 20, pady = 20, sticky = "NSEW")
fr_sat_pos.grid_propagate(False)
app.grid_rowconfigure(1, weight = 1)
fr_sat_pos.columnconfigure(0,weight = 1)
fr_sat_pos.columnconfigure(1,weight = 1)
label_2 = cstk.CTkLabel(fr_sat_pos, text = "Satellite position", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3, width=200)
label_2.grid(column = 0, row = 0, columnspan = 2, sticky = "EW")#
label_3 = cstk.CTkLabel(fr_sat_pos, text = "Azimuth:", font = ("Cambria", 14))
label_3.grid(column = 0, row = 1, pady = 5, padx = 5, sticky = "E")
entry_1 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), width = 80, state = "disabled", textvariable = azimut_TK)
entry_1.grid(column = 1, row = 1, padx = 2, sticky = "W")
label_4 = cstk.CTkLabel(fr_sat_pos, text = "Elevation:", font=("Cambria", 14))
label_4.grid(column=0, row = 2, pady = 5, padx = 5, sticky = "E")
entry_2 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), state = "disabled", width = 80, textvariable = elevation_TK)
entry_2.grid(column = 1, row = 2, padx = 2, sticky = "W")
label_5 = cstk.CTkLabel(fr_sat_pos, text = "Antenna in use:", font = ("Cambria", 14))
label_5.grid(column = 0, row = 3, columnspan = 2, pady = 10, sticky = "NSEW")
entry_3 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), state = "disabled", width = 80, textvariable = ant_TK, justify = "center")
entry_3.grid(column = 0, row = 4, columnspan = 2, padx = 15, sticky = "NSEW")
checkbtn_6 = cstk.CTkCheckBox(fr_sat_pos, text = "Coupling of two", variable = coupling, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2)
checkbtn_6.grid(column = 0, row = 5, columnspan = 2, pady = 10, padx = 35,  sticky = "WE")

#create frame for displaying diagnostitcal data from swich
fr_status = cstk.CTkFrame(app, width = 250, height = 230)
fr_status.grid(column = 1, row = 1, padx = 20, pady = 20, sticky = "NSEW")
fr_status.columnconfigure(0, weight = 1)
fr_status.columnconfigure(1, weight = 1)
fr_status.columnconfigure(2, weight = 1)
fr_status.grid_propagate(False)
label_6 = cstk.CTkLabel(fr_status, text = "Status info", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3, width=200)
label_6.grid(column = 0, row = 0, columnspan = 3, sticky = "NSEW")
label_8 = cstk.CTkLabel(fr_status, text = "Phantom voltage [V]:", font = ("Cambria", 14))
label_8.grid(column = 0, row = 1, pady = 5, padx = 5, sticky = "E")
entry_4 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = fant_volt_TK)
entry_4.grid(column = 1, row = 1, columnspan = 2, padx = 2, sticky = "WE")
label_9 = cstk.CTkLabel(fr_status, text = "Current to LNAs [mA]:", font = ("Cambria", 14))
label_9.grid(column = 0, row = 2, pady = 5, padx = 5, sticky = "E")
entry_5 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 35, textvariable = cur_A_TK)
entry_5.grid(column = 1, row = 2, padx = 2, sticky = "WE")
entry_8 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 35, textvariable = cur_B_TK)
entry_8.grid(column = 2, row = 2, sticky = "WE")
label_10 = cstk.CTkLabel(fr_status, text = "Temperature [°C]:", font = ("Cambria", 14))
label_10.grid(column = 0, row = 3, pady = 5, padx = 5, sticky = "E")
entry_6 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 35, textvariable = temp_A_TK)
entry_6.grid(column = 1, row = 3, padx = 2, sticky = "WE")
entry_9 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 35, textvariable = temp_B_TK)
entry_9.grid(column = 2, row = 3, sticky = "WE")
label_11 = cstk.CTkLabel(fr_status, text = "Ant. orientation \nmeasured/set:", font = ("Cambria", 14))
label_11.grid(column = 0, row = 4, pady = 5, padx = 5, sticky = "E")
entry_7 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = orientation_TK)
entry_7.grid(column = 1, row = 4, padx = 2, sticky = "WE")
entry_12 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = orientation_manual_TK)
entry_12.grid(column = 2, row = 4, padx = 2, sticky = "WE")
entry_11 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = state, justify = "center")
entry_11.grid(column = 0, row = 5, columnspan = 2, padx = 20, pady = 5, sticky = "WE")
#btn_5 = cstk.CTkButton(fr_status,  image= refresh_button_image, text = "",  width=25, height=25, border_width=0,  command = threading.Thread(target = update_data_from_switch, daemon = True).start)
btn_5 = cstk.CTkButton(fr_status, corner_radius = 3, text = "Man.\nRefresh", font = ("Cambria", 11), width= 20, command=lambda: threading.Thread(target = update_data_from_switch, daemon = True).start())
btn_5.grid(column = 2, row = 5, sticky = "NS", pady = 5, padx = 5)#, pady = 5, padx = 5, ipadx = 0, ipady = 0

#create frame for antenna switch configuration
fr_ant_ctrl = cstk.CTkFrame(app, width = 200, height = 260)
fr_ant_ctrl.grid(column = 0, row = 2, padx = 20, sticky = "WE")
fr_ant_ctrl.grid_propagate(False)
fr_ant_ctrl.columnconfigure(0,weight = 1)
fr_ant_ctrl.columnconfigure(1,weight = 1)
label_7 = cstk.CTkLabel(fr_ant_ctrl, text = "Antenna switch", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3)
label_7.grid(column = 0, row = 0, columnspan = 2, sticky = "EW") 
auto_radbutton = cstk.CTkRadioButton(fr_ant_ctrl, text = "Auto", variable = auto_switch, value = 1, font = ("Cambria", 14), border_width_unchecked = 2, border_width_checked = 7, command = auto_on)
auto_radbutton.grid(column = 0, row = 1, pady = 5, padx = 3)
manual_radbutton = cstk.CTkRadioButton(fr_ant_ctrl, text = "Manual:", variable = auto_switch, value = 2, font = ("Cambria", 14), border_width_unchecked = 2, border_width_checked = 7, command = manual_on)
manual_radbutton.grid(column = 0, row = 2, pady = 5, padx = 3)
off_radbutton = cstk.CTkRadioButton(fr_ant_ctrl, text = "Off", variable = auto_switch, value = 3, font = ("Cambria", 14), border_width_unchecked = 2, border_width_checked = 7, command = switch_set_off)
off_radbutton.grid(column = 1, row = 1, pady = 5, padx = 3)
checkbtn_1 = cstk.CTkCheckBox(fr_ant_ctrl, text = "Ant. 1", variable = ant1_on, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2, state = "disabled", command = checkbtn_fun)
checkbtn_1.grid(column = 1, row = 3, pady = 3)
checkbtn_2 = cstk.CTkCheckBox(fr_ant_ctrl, text = "Ant. 2", variable = ant2_on, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2, state = "disabled", command = checkbtn_fun)
checkbtn_2.grid(column = 1, row = 4, pady = 3)
checkbtn_3 = cstk.CTkCheckBox(fr_ant_ctrl, text = "Ant. 3", variable = ant3_on, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2, state = "disabled", command = checkbtn_fun)
checkbtn_3.grid(column = 1, row = 5, pady = 3)
checkbtn_4 = cstk.CTkCheckBox(fr_ant_ctrl, text = "Ant. 4", variable = ant4_on, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2, state = "disabled", command = checkbtn_fun)
checkbtn_4.grid(column = 1, row = 6, pady = 3)
checkbtn_5 = cstk.CTkCheckBox(fr_ant_ctrl, text = "Ant. 5", variable = ant5_on, onvalue = True, offvalue = False, font = ("Cambria", 14), border_width = 2, state = "disabled", command = checkbtn_fun)
checkbtn_5.grid(column = 1, row = 7, pady = 3)

#create frame for app setings
fr_settings = cstk.CTkFrame(app, width = 200, height = 260)
fr_settings.grid(column = 1, row = 2, padx = 20, sticky = "WE")
fr_settings.grid_propagate(False)
fr_settings.columnconfigure(0,weight = 1)
fr_settings.columnconfigure(1,weight = 1)
btn_1 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "Manual ant. \n orientation set.", font = ("Cambria", 14), command = ant_orientation_set_m)
btn_1.grid(column = 0, row = 0, sticky = "NWES", padx = 5, pady = 10)
btn_2 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "Set current \n ant. orientation", font = ("Cambria", 14), command = ant_orientation_set_a)
btn_2.grid(column = 1, row = 0, sticky = "NWES", padx = 5, pady = 10)
btn_3 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "App settings", font = ("Cambria", 14), command = create_new_window)
btn_3.grid(column = 0, columnspan = 2, row = 3, sticky = "NWES", padx = 45, pady = 25)
btn_4 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "App info", font = ("Cambria", 14), command = app_info)
btn_4.grid(column = 0, columnspan = 2, row = 4, sticky = "NWES", padx = 45)
label_14 = cstk.CTkLabel(fr_settings,  font = ("Cambria", 14), text = "Serial port:") 
label_14.grid(column = 0, columnspan =2, row = 1, sticky = "S", pady = 5)
com_menu = cstk.CTkOptionMenu(fr_settings, font = ("Cambria", 14), values = list_com, command = com_select, width = 30, anchor = "center", variable = com_TK)
com_menu.grid(column = 0, columnspan =2, row = 2, sticky = "N", pady = 5)
app.grid_rowconfigure(3, weight = 1, minsize = 20)
app.grid_rowconfigure(4, weight = 1)
fr_conn1 = cstk.CTkFrame(app, corner_radius=0, height = 20)
fr_conn1.grid(column = 0, row = 4, sticky = "WES")
label_12 = cstk.CTkLabel(fr_conn1, textvariable = orbitron_conn_TK, font = ("Cambria", 12, "italic")) 
label_12.pack(anchor = 's', side = "bottom")
fr_conn2 = cstk.CTkFrame(app, corner_radius=0, height = 20)
fr_conn2.grid(column = 1, row = 4, sticky = "WES")
label_13 = cstk.CTkLabel(fr_conn2, textvariable = switch_com_TK, font = ("Cambria", 12, "italic"))
label_13.pack(anchor = 's', side = "bottom")

#==================== Starting the timers for data refresh ====================
if first_data: #if serial comm. was succesfully estabilished after app start then request all diag. data from switch 1 sec after app start 
    app.after(1000, threading.Thread(target = update_data_from_switch, daemon = True).start)

if dde_con: #if Orbitron is connected (the app is opened)
    app.after(500, update_data_from_orbitron) #then after 0.5 sec read the data from Orbitron
else:
    app.after(2571, check_conn_orbitron)    #else each 2.5 sec check if Orbitron app is opened

#each checking interval is opened thread to get data from serial line, thread is necessary because serial readig and writing blocks the main loop
t1 = threading.Timer(function = read_U_I, interval = delay_read_UI) #start thread after given interval and do given fun
t1.daemon = True #thread is closed if main thread is closed otherwise some tasks wont stop after closing the app
t1.start()

t2 = threading.Timer(function = read_temp, interval = delay_read_T)
t2.daemon = True
t2.start()

t3 = threading.Timer(function = read_orient, interval = delay_read_C)
t3.daemon = True
t3.start()

#after given time update data on screen by reading the proccesed data from ser. line
#app.after(delay_read_T * 1000 + 3000, update_temp)  
#app.after(delay_read_UI * 1000 + 3500, update_current_voltage)
#app.after(delay_read_C * 1000 + 3000, update_orintation)

app.protocol("WM_DELETE_WINDOW", on_closing)    #on closing the app, call given function to end the ser. comm. and dde server 
app.mainloop() #run the app

#to generate EXE:
#               $pyinstaller --onefile --noconsole --clean --icon='icon.ico' --add-data 'icon.ico;.' --name antenna_switch_control  main.py