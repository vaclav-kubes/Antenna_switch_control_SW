
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

def log_error():
    try:
        now = datetime.datetime.now()
        t = now.strftime("%d/%m/%Y %H:%M:%S")
        with open("error_logs.csv", "r", encoding = "utf-8") as file:
            pass
        with open("error_logs.csv", "a", encoding = "utf-8") as file:
            file.write(t + ',' + cur_A_TK.get() + ',' + cur_B_TK.get() + ',' + temp_A_TK.get() + ',' + temp_B_TK.get() + ',' + fant_volt_TK.get() + ',' + orientation_TK.get() + ','+ ant_TK.get() + '\n')
    except:
      with open("error_logs.csv", "a", encoding = "utf-8") as file:
            file.write("Time,Curr. to A, Curr. to B,Temp. of A,Temp. og B,Voltage,Ant. azimuth,Switched ant.\n")
            file.write(t + ',' + cur_A_TK.get() + ',' + cur_B_TK.get() + ',' + temp_A_TK.get() + ',' + temp_B_TK.get() + ',' + fant_volt_TK.get() + ',' + orientation_TK.get() + ','+ ant_TK.get() + '\n')
              

def switch_ant():
    global ant_old
    
    ant_new = ant_TK.get().strip()
    
    if ant_old != ant_new:
        #print("ant:", ant_new)
        threading.Thread(target = ant_set, args = [ant_new], daemon = True).start()
        ant_old = ant_new

def ant_set(antenna):
    #global block
    while not q_done.get():
        q_done.task_done()
        time.sleep(0.3)
    q_done.put(False)
    #while block:
        #time.sleep(0.3)
    #block = True
    
    #q_done.task_done()
    #print(time.time())
    serial_write(ser_com, "AN"+ antenna.strip())
    if extract_val(serial_read(ser_com)) != antenna:
        log_error()
    #time.sleep(0.7)
    q_done.put(True)
    q_done.task_done()
    #block = False

def evaluate_state(type_of_data, data):
    global config_or
    try:
        if type_of_data == "IA":
            if data >= float(max_cur_A.get()) or data <= 20:
                return True
            else:
                return False
        elif type_of_data == "IB":
            if data >= float(max_cur_B.get()) or data <= 20:
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
    try:
        ser_com.close()
        s.Shutdown()
        #t1.join(timeout=1)
        #t2.join(timeout=1)
        app.destroy()
    except:
        app.destroy()

def auto_connect():
    global ser_com
    while not ping(com_TK.get()): time.sleep(5)
    ser_com = serial_start(com_TK.get())
    #if switch_com_TK.get() == "Switch: Disconnected":
        #switch_com_TK.set("Switch: Connected")
    #t_ser_con.join()


def read_U_I():
    #global block
    #print("vlákno")
    global ser_com
    while not q_done.get():
        q_done.task_done()
        time.sleep(0.3)
    #while block:
        #time.sleep(0.3)
    #block = True
    q_done.put(False)
    #print(time.time())
    IA = extract_val(get_curr_A(ser_com)[1])
    IB = extract_val(get_curr_B(ser_com)[1])
    UF = extract_val(get_fant_U(ser_com)[1])
    q_done.put(True)
    q_done.task_done()
    #block = False
    q_UI.put(IA)
    #time.sleep(0.07)
    q_UI.put(IB)
    #time.sleep(0.07)
    q_UI.put(UF)
    q_UI.task_done()
    
    #block = False
    error_state = q_state.get()
    error_state[0] = evaluate_state("IA", IA)
    error_state[1] = evaluate_state("IB", IB)
    error_state[2] = evaluate_state("U", UF)
    q_state.put(error_state)
    q_state.task_done()
    

    if True in error_state:
        state.set("Warning!")
        entry_11.configure(text_color = "red")
        log_error()
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

    #time.sleep(0.07)
    t = threading.Timer(function = read_U_I, interval = delay_read_UI)#180
    t.daemon = True
    t.start()

def read_temp():
    while not q_done.get():
        q_done.task_done()
        time.sleep(0.3)
  
    q_done.put(False)
    TA = extract_val(get_temp_A(ser_com)[1])
    TB = extract_val(get_temp_B(ser_com)[1])
    q_done.put(True)
    q_temp.put(TA)
    #time.sleep(0.07)
    q_temp.put(TB)
    q_temp.task_done()
    #time.sleep(0.07)
    

    error_state = q_state.get()
    error_state[3] = evaluate_state("TA", TA)
    error_state[4] = evaluate_state("TB", TB)
    q_state.put(error_state)
    q_state.task_done()

    if True in error_state:
        state.set("Warning!")
        entry_11.configure(text_color = "red")
    else:
        state.set("Normal state")
        entry_11.configure(text_color = "green")

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
        state.set("Warning!")
        entry_11.configure(text_color = "red")
    else:
        state.set("Normal state")
        entry_11.configure(text_color = "green")

    if error_state[5]:
        entry_7.configure(text_color = "red") 
    elif entry_7.cget("text_color") == "red":
        entry_7.configure(text_color = "black") 


    t = threading.Timer(function = read_orient, interval = delay_read_C + 0.3)
    t.daemon = True
    t.start()



def auto_on():
    checkbtn_1.configure(state = "disabled")
    checkbtn_2.configure(state = "disabled")
    checkbtn_3.configure(state = "disabled")
    checkbtn_4.configure(state = "disabled")
    checkbtn_5.configure(state = "disabled") 
    ant_TK.set(str(auto_select_ant()))

def manual_on():
    checkbtn_1.configure(state = "normal") 
    checkbtn_2.configure(state = "normal")
    checkbtn_3.configure(state = "normal")
    checkbtn_4.configure(state = "normal")
    checkbtn_5.configure(state = "normal")
    ant1_on.set(False)
    ant2_on.set(False)
    ant3_on.set(False)
    ant4_on.set(False)
    ant5_on.set(False)

def checkbtn_fun():
    
    """
    num_of_ant = []
    if ant1_on.get():
        num_of_ant.append(1)
    else:
        num_of_ant.append(0)
    if ant2_on.get():
        num_of_ant.append(1)
    else:
        num_of_ant.append(0)
    if ant3_on.get():
        num_of_ant.append(1)
    else:
        num_of_ant.append(0)
    if ant4_on.get():
        num_of_ant.append(1)
    else:
        num_of_ant.append(0)
    if ant5_on.get():
        num_of_ant.append(1)
    else:
        num_of_ant.append(0)

    if len(num_of_ant) > 3:
        num_of_ant.index(1)

    print(num_of_ant)
    """
    """
    num_of_ant = [ant1_on, ant2_on, ant3_on, ant4_on, ant5_on]
    cnt = 0
    ant_str = ""
    for i in num_of_ant:
        if cnt > 2:
            cnt -= 1
            i.set(False)
        elif i.get():
            cnt += 1
            ant_str += " " + str(num_of_ant.index(i) + 1)
    ant_TK.set(ant_str)
    """
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
    switch_ant()

def update_current_voltage():#ser_com
    #data_A = extract_val(get_curr_A(ser_com)[1])
    #data_B = extract_val(get_curr_B(ser_com)[1])
    #data_V = extract_val(get_fant_U(ser_com)[1])
    #print(data_A)
    #print(data_B)
    #print(data_V)
    #print("tkinter")
    try:
        data_A = q_UI.get()
        data_B = q_UI.get()
        data_V = q_UI.get()
        #while not q_UI.empty():
            #q_UI.get()
        q_UI.task_done()
        print(data_A,data_B,data_V)
        if data_A != None and data_B != None and data_V != None:
            cur_A_TK.set("{:.1f}".format(data_A))
            cur_B_TK.set("{:.1f}".format(data_B))
            fant_volt_TK.set("{:.1f}".format(data_V))
            if switch_com_TK.get() == "Switch: Disconnected":
                switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")
    
    except queue.Empty:
        pass
    
    #app.after(18001, threading.Thread(target = update_current_voltage, args = (ser_com,), deamon = True).start())
    app.after(delay_read_UI * 1000 + 3500, update_current_voltage)#180100

def update_temp(): #ser_com
    #print("temp1")
    #data_A = extract_val(get_temp_A(ser_com)[1])
    #time.sleep(0.3)
    #print("temp2")
    #data_B = extract_val(get_temp_B(ser_com)[1])
    #time.sleep(0.3)
    #print(data_A)
    #print(data_B)
    #print(data_V)
    try:
        data_A = q_temp.get()
        data_B = q_temp.get()
        #while not q_temp.empty():
            #q_temp.get()
        q_temp.task_done()
        if data_A != None and data_B != None:
            temp_A_TK.set("{:.1f}".format(data_A))
            temp_B_TK.set("{:.1f}".format(data_B))
            if switch_com_TK.get() == "Switch: Disconnected":
                switch_com_TK.set("Switch: Connected")
        else:
            switch_com_TK.set("Switch: Disconnected")
    except queue.Empty:
        pass
    #t2.join()
    #t2 = threading.Thread(target = update_temp, args = (ser_com,), daemon = True)
    #app.after(37001, threading.Thread(target = update_temp, args = (ser_com,), daemon = True).start())#300000
    app.after(delay_read_T * 1000 + 3000, update_temp)#300000

def update_orintation(): #ser_com
    data = q_orient.get()
    #while not q_orient.empty():
        #q_orient.get()
    #q_orient.task_done()
    #print(data_A)
    #print(data_B)
    #print(data_V)
    if data != None:
        orientation_TK.set("{:.1f}".format(data) + " °")
        if switch_com_TK.get() == "Switch: Disconnected":
            switch_com_TK.set("Switch: Connected")
    else:
        switch_com_TK.set("Switch: Disconnected")
    
    #app.after(90001, threading.Thread(target = update_orintation, args = (ser_com,), deamon = True).start())#900000
    app.after(delay_read_C * 1000 + 3000, update_orintation)#900000

def update_data_from_switch(): #[IA, IB, TA, TB, UF, EC, AN, CB] #ser_com
    #global ser_com
    global ant_old
    global ser_com
    if ser_com:
        while not q_done.get():
            q_done.task_done()
            time.sleep(0.3)
        q_done.put(False)
        #q_done.task_done()
        data = extract_val(get_all(ser_com)[1])
        q_done.put(True)
        
        #print(data)
        #ser.close()
        cur_A_TK.set("{:.1f}".format(data[0]))
        cur_B_TK.set("{:.1f}".format(data[1]))
        temp_A_TK.set("{:.1f}".format(data[2]))
        temp_B_TK.set("{:.1f}".format(data[3]))
        fant_volt_TK.set("{:.1f}".format(data[4]))
        orientation_TK.set("{:.1f}".format(data[5]) + " °")
        ant_TK.set("{:n}".format(data[6]))
        ant_old = "{:n}".format(data[6])

        switch_ant()

        error_state = q_state.get()
        error_state[0] = evaluate_state("IA", data[0])
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


        if switch_com_TK.get() == "Switch: Disconnected":
            switch_com_TK.set("Switch: Connected")
    else:
        switch_com_TK.set("Switch: Disconnected")
        
    #app.after(1000, update_data_from_switch)

def update_data_from_orbitron():
    dde_data.set(c.Request("TrackingData"))
    data = dde_data.get()
    #print(data)
    az = get_AZ_EZ("AZ", data)
    el = get_AZ_EZ("EL", data)
    #print("data:", az, el, len(data))
    if len(data) > 2:#not("    "  in az) and not("    " in el):
        azimut_TK.set(az)
        elevation_TK.set(el)
        if orbitron_conn_TK.get() == "Orbitron: No data":
            orbitron_conn_TK.set("Orbitron: Connected")
        if not auto_switch.get():
        #print("auto", auto_select_ant())
            ant_TK.set(str(auto_select_ant()))
            switch_ant()
    else:
        if orbitron_conn_TK.get() == "Orbitron: Connected":
            orbitron_conn_TK.set("Orbitron: No data")



    app.after(500, update_data_from_orbitron)
    """
    else:
        ant_str = ""
        if ant1_on.get():
            ant_str += "1 "
        if ant2_on.get():
            ant_str += "2 "
        if ant3_on.get():
            ant_str += "3 "
        if ant4_on.get():
            ant_str += "4 "
        if ant4_on.get():
            ant_str += "5 "
        ant_TK.set(ant_str)
    #print(azimut_TK.get())
    #print(elevation_TK.get())
    """

def check_conn_orbitron():
    try:
        c.ConnectTo("Orbitron", "Tracking")
        if c.Connected() == 1:
            print("Connection established")
            #print(c.Request("TrackingData"))
            orbitron_conn_TK.set("Orbitron: Connected")
            update_data_from_orbitron()
        else:
            orbitron_conn_TK.set("Orbitron: Not running")
            s.Shutdown()
            app.after(2500, check_conn_orbitron)
    except:
        orbitron_conn_TK.set("Orbitron: Not running")
        app.after(2500, check_conn_orbitron)


def get_AZ_EZ(select, data):
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
        #print(azimut)
        return azimut
        #print(azimut)
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
        #print(elevation)
    
def ant_orientation_set_a():
    if switch_com_TK.get() == "Switch: Connected":
        global config_or
        #dialog = cstk.CTkInputDialog(text="Type in an azimuth of antenna:", title="Manual antenna orientation setting")
        #print("Number:", dialog.get_input()) 
        #print(dialog.get_input()) 
        val = entry_7.get()
        if val == None:
            return
        
        orientation_manual_TK.set(val)
        #config_or = float(val[:-2])
        config_or = val
        error_state = q_state.get()
        error_state[5] = evaluate_state("C", float(val[:-2]))
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

        try:
            with open("config.txt", "r", encoding = "utf-8") as config:
                content = config.readlines()
                config.close()
                content[0] = val + "\n"    
            with open("config.txt", "w", encoding = "utf-8") as config:
                config.writelines(content)
                config.close()
        except:
            config = open("config.txt", "x", encoding = "utf-8")
            config.write("\n")
            config.write(val + "\n")
            config.close()

        msg.CTkMessagebox(message = "Antenna azimuth was set!", title = "Antenna azimuth set")
    else:
        msg.CTkMessagebox(message = "No data", title = "No data from switch!")

def ant_orientation_set_m():
    global config_or
    dialog = cstk.CTkInputDialog(text="Type in an azimuth of antenna:", title="Manual antenna orientation setting")
    #print("Number:", dialog.get_input()) 
    #print(dialog.get_input()) 
    val = dialog.get_input()
    if val == None:
        return
    text = ''
    for i in val:
        #print(ord(i))
        if ord(i) >= 48 and ord(i) <= 57 or ord(i) == 46:
            text += i
        elif ord(i) == 44:
            text += '.'
    print(text)
    try:
        dev = float(text)
        print(dev)
        if dev > 360.0 or dev < 0.0:
            msg.CTkMessagebox(title="Invalid range", message="Azimuth should be in range from 0° to 360°.", icon = "warning")
        else:
            orientation_manual_TK.set(text + " °")
            #r_or = entry_7.get()
            config_or = text + " °"#\n

            error_state = q_state.get()
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

            try:
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
           
def auto_select_ant():
    #print(orientation_manual_TK.get()[:-3].encode("utf-8"))
    try:
        #print(orientation_manual_TK.get(), len(orientation_manual_TK.get()))
        ant_orientation = float(orientation_manual_TK.get()[:-2])
        #print("chyba1")
        #print(azimut_TK.get()[:-1])
        az = float(azimut_TK.get()[:-1])
        
        ant = 1
        if az >= divmod(ant_orientation - 45, 360)[1] and az <= divmod(ant_orientation + 45, 360)[1]:     
            ant = 1
            #ant1_on.set(True)
        elif az >= divmod(ant_orientation + 45, 360)[1] and az <= divmod(ant_orientation + 135, 360)[1]:
            ant = 2
            #ant2_on.set(True)
        elif az >= divmod(ant_orientation + 135, 360)[1] and az <= divmod(ant_orientation + 225, 360)[1]:
            ant = 3
            #ant3_on.set(True)
        elif az >= divmod(ant_orientation + 225, 360)[1] and az <= divmod(ant_orientation + 315, 360)[1]:
            ant = 4
            #ant4_on.set(True)
        return ant
    except:
        #print("chyba3")
        return 1

def com_select(choice):
    global ser_com
    if not com_menu.cget("values"):
        com_menu.configure(values = available_com())
    if ping(choice):
        #ser_com = serial_start(choice)
        #switch_com_TK.set("Switch: Connected")
        try:
            with open("config.txt", "r", encoding = "utf-8") as config:
                content = config.readlines()
                #print(content)
                config.close()
                if len(content) == 1:
                    content.append(choice + "\n")
                else:
                    content[1] = choice + "\n"
                try:
                    with open("config.txt", "w", encoding = "utf-8") as config:
                        config.writelines(content)
                        config.close()
                except:
                    msg.CTkMessagebox(title="Settings not saved.", message="Settings not saved. Unable to write to configuration file.")
            
            ser_com = serial_start(choice)
            
            try:
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
                threading.Thread(target = update_data_from_switch, daemon = True).start()
        except:
            try:
                with open("config.txt", "w", encoding = "utf-8") as config:
                    config.writelines(["\n", choice + "\n"])
                    config.close()
            except:
                msg.CTkMessagebox(title="Settings not saved.", message = "Settings not saved. Error while saving the serial port setting.")
    else:
        switch_com_TK.set("Switch: Disconnected")

def create_new_window():
    print("nove okno")
    btn_3.configure(state = "disabled")
    try:
        with open("config.txt", "r", encoding = "utf-8") as config:
            content = config.readlines()
            config.close()
        max_cur_A.set(content[2][:-1])
        max_cur_B.set(content[3][:-1])
        max_temp_n_A.set(content[4][:-1])
        max_temp_p_A.set(content[5][:-1])
        max_temp_n_B.set(content[6][:-1])
        max_temp_p_B.set(content[7][:-1])
        max_az_dev.set(content[8][:-1])      
        min_u_fant.set(content[9][:-1])
        max_u_fant.set(content[10][:-1])
        B_connected.set(bool(float(content[11][:-1])))
    except:
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

    app_set_range = cstk.CTkToplevel(app)
    app_set_range.title("Set error tresholds")
    app_set_range.focus()
    #app_set_range.state("zoomed")
    L_title = cstk.CTkLabel(app_set_range, text = "Settings", font = ("Cambria", 17, "bold"), anchor = "center")
    L_title.grid(column = 0, columnspan = 2, row = 0, sticky = "NSEW")

    L_set_current_A = cstk.CTkLabel(app_set_range, text = "Set error treshold for curretn to LNAs on A board [mA]:", font = ("Cambria", 14, "bold"))
    L_set_current_A.grid(column = 0, columnspan = 2, row = 1, padx = 50, pady = 2, sticky = "NSEW")

    E_set_current_A = cstk.CTkEntry(app_set_range, textvariable = max_cur_A, font = ("Cambria", 14))
    E_set_current_A.grid(column = 0, columnspan = 2, row = 2, padx = 50, sticky = "NSEW")

    L_set_current_B = cstk.CTkLabel(app_set_range, text = "Set error treshold for curretn to LNAs on B board [mA]:", font = ("Cambria", 14, "bold"))
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

    CH_set_B_conn = cstk.CTkCheckBox(app_set_range, variable = B_connected, onvalue = True, offvalue = False, text = "Yes", font = ("Cambria", 14, "bold"))
    CH_set_B_conn.grid(column = 0, columnspan = 2, row = 20, padx = 50, pady = 2, sticky = "NSEW")

    B_set = cstk.CTkButton(app_set_range, text = "Save", font = ("Cambria", 14), command = lambda: set_tresholds(app_set_range))
    B_set.grid(column = 0, row = 21, padx = 20, pady = 10, sticky = "NSEW")

    B_close = cstk.CTkButton(app_set_range, text = "Close", font = ("Cambria", 14), command = lambda: close_settings(app_set_range))
    B_close.grid(column = 1, row = 21, padx = 20, pady = 10, sticky = "NSEW")

    app_set_range.protocol("WM_DELETE_WINDOW", lambda:close_settings(app_set_range))
    #print(app_set_range.children.items())
    app_set_range.after_idle(app_set_range.lift)

def set_tresholds(app_set_range):
    wrong_entry = []
    value_list = []
    #print(app_set_range.children.keys())
    for n in app_set_range.children.keys():
        if "entry" in n or "checkbox" in n:
            try:
                #print("dobrý4")
                text_value = app_set_range.children[n].get()
                #print("dobrý3")
                if isinstance(text_value, str):
                    text_value = text_value.replace(',', '.').strip('\n')
                #print("dobrý1")
                value = float(text_value)
                #print("dobrý2")
                if ('4' in n or '6' in n) and (value < value_list[-1]):
                    #print("něco spatně")
                    value_list.append(None)
                    raise Exception()
                elif ('2' in n or  n =='!ctkentry') and value < 20:
                    value_list.append(None)
                    raise Exception()
                elif '7' in n and value < 0:
                    value_list.append(None)
                    raise Exception()
                elif '8' in n and value < 0:
                    value_list.append(None)
                    raise Exception()
                elif '9' in n and (value < value_list[-1]) or ('9' in n and value < 0):
                    value_list.append(None)
                    raise Exception()
                
                value_list.append(value)

                wrong_entry.append(False)

            except:
                app_set_range.children[n].configure(text_color = "red")
                wrong_entry.append(True)
                print("chyba")
   
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
    
    if True in wrong_entry:
        msg.CTkMessagebox(title="Error", message="Invalid value!")
    else:
        error_state = q_state.get()
        error_state[0] = evaluate_state("IA", float(cur_A_TK.get()))
        error_state[1] = evaluate_state("IB", float(cur_B_TK.get()))
        error_state[2] = evaluate_state("U", float(fant_volt_TK.get()))
        error_state[3] = evaluate_state("TA", float(temp_A_TK.get()))
        error_state[4] = evaluate_state("TB", float(temp_B_TK.get()))
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
    btn_3.configure(state = "normal")
    app_set_range.destroy()

def app_info():
    webbrowser.open('https://github.com/vaclav-kubes/Antenna_switch_control_SW/blob/main/README.md')

cstk.set_appearance_mode("System")
app = cstk.CTk()
app.geometry("630x590")
app.minsize(width = 630, height = 590)
app.title("Antenna switch controller")

app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)
app.rowconfigure(0, weight=1)
app.rowconfigure(1, weight=1)
app.rowconfigure(2, weight=1)
app.rowconfigure(3, weight=1)

#curr_ant_text = cstk.StringVar(app, "Currnetly operating antenna: 1, 2, 3")
auto_switch = cstk.BooleanVar()
ant1_on = cstk.BooleanVar()
ant2_on = cstk.BooleanVar()
ant3_on = cstk.BooleanVar()
ant4_on = cstk.BooleanVar()
ant5_on = cstk.BooleanVar()
dde_data = cstk.StringVar()
azimut_TK = cstk.StringVar()
elevation_TK = cstk.StringVar()
orientation_TK = cstk.StringVar()#value = "0 °"
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
list_com = []
config_com = ""
ant_old = 0
delay_read_UI = 5#30 
delay_read_T = 300
delay_read_C = 900
dde_con = False
#error_state = [False, False, False, False, False, False]# IA IB FU TA TB CE
#global ser_com
q_UI = queue.Queue()
q_temp = queue.Queue()
q_orient = queue.Queue()
q_done = queue.Queue()
q_done.put(True)
q_state = queue.Queue()
q_state.put([False, False, False, False, False, False])
#create a DDE client and start conversation
s = dde.CreateServer()
#the parameter in brackets is the name of this Python file (AddLayers.py)
s.Create("GetData")
#create a conversation between client and server
c = dde.CreateConversation(s)
try:
    c.ConnectTo("Orbitron", "Tracking")
    if c.Connected() == 1:
        dde_con = True
        print("Connection established")
        print(c.Request("TrackingData"))
        orbitron_conn_TK.set("Orbitron: Connected")
    else:
        azimut_TK.set("00")
        elevation_TK.set("00")
        orbitron_conn_TK.set("Orbitron: Not running")
        s.Shutdown()
except:
    orbitron_conn_TK.set("Orbitron: Not running")
    azimut_TK.set("00")
    elevation_TK.set("00")

#if the connection succeeds, proceed with requests to PhotoModeler



try:
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
    max_u_fant.set(config.readline().strip("\n"))
    min_u_fant.set(config.readline().strip("\n"))
    B_connected.set(bool(float(config.readline().strip("\n")+'0')))
    #print(config_com)
    config.close()
    
except:
    config = open("config.txt", "x", encoding = "utf-8")
    config.writelines(["\n","\n", "650\n", "650\n", "-10\n", "50\n", "-10\n", "50\n", "10\n", "7\n", "12\n", "0\n"])
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

get_com = available_com()

if not get_com and config_com:
    list_com.append(config_com[:-1])
    com_TK.set(config_com[:-1])
elif get_com:
    list_com = get_com
    com_TK.set(list_com[0])
else:
    com_TK.set("??")

if config_com:
    if ping(config_com[:-1]):
        switch_com_TK.set("Switch: Connected")
        ser_com = serial_start(com_TK.get())
        first_data = True
    else:
        switch_com_TK.set("Switch: Disconnected")
        ser_com = None
        #t_ser_con = threading.Thread(target = auto_connect, daemon = True)
        #t_ser_con.start()
        first_data = False
else:
    switch_com_TK.set("Switch: Disconnected")
    ser_com = None
    first_data = False



label_1 = cstk.CTkLabel(app, text = "Antenna switch controller", font = ("Cambria", 20, "bold"), anchor = "center")
label_1.grid(column = 0, row = 0, columnspan = 2, sticky = "NSEW")
app.grid_rowconfigure(0, weight = 1)

fr_sat_pos = cstk.CTkFrame(app, width=200, height=200) #, width=200, height=200, fg_color="#e3e3e3"
fr_sat_pos.grid(column = 0, row = 1, padx = 20, pady = 20, sticky = "NSEW")#, rowspan = 2
fr_sat_pos.grid_propagate(False)
app.grid_rowconfigure(1, weight = 1)
fr_sat_pos.columnconfigure(0,weight = 1)
fr_sat_pos.columnconfigure(1,weight = 1)
#fr_sat_pos.rowconfigure(0,weight = 1)
#fr_sat_pos.rowconfigure(1,weight = 1)
label_2 = cstk.CTkLabel(fr_sat_pos, text = "Satellite position", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3, width=200)
label_2.grid(column = 0, row = 0, columnspan = 2, sticky = "EW")#

label_3 = cstk.CTkLabel(fr_sat_pos, text = "Azimut:", font = ("Cambria", 14))
label_3.grid(column = 0, row = 1, pady = 5, padx = 5, sticky = "E")
entry_1 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), width = 80, state = "disabled", textvariable = azimut_TK)#
entry_1.grid(column = 1, row = 1, padx = 2, sticky = "W")
label_4 = cstk.CTkLabel(fr_sat_pos, text = "Elevation:", font=("Cambria", 14))
label_4.grid(column=0, row = 2, pady = 5, padx = 5, sticky = "E")
entry_2 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), state = "disabled", width = 80, textvariable = elevation_TK)
entry_2.grid(column = 1, row = 2, padx = 2, sticky = "W")
label_5 = cstk.CTkLabel(fr_sat_pos, text = "Antenna in use:", font = ("Cambria", 14))
label_5.grid(column = 0, row = 3, columnspan = 2, pady = 10, sticky = "NSEW")
entry_3 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), state = "disabled", width = 80, textvariable = ant_TK, justify = "center")
entry_3.grid(column = 0, row = 4, columnspan = 2, padx = 30, sticky = "NSEW")

fr_status = cstk.CTkFrame(app, width = 250, height = 230)
fr_status.grid(column = 1, row = 1, padx = 20, pady = 20, sticky = "NSEW")#, rowspan = 2
#app.grid_rowconfigure(2, weight = 1)
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

label_9 = cstk.CTkLabel(fr_status, text = "Currnet to LNAs [mA]:", font = ("Cambria", 14))
label_9.grid(column = 0, row = 2, pady = 5, padx = 5, sticky = "WE")
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
entry_11.grid(column = 0, row = 5, columnspan = 3, padx = 70, pady = 5, sticky = "WE")

fr_ant_ctrl = cstk.CTkFrame(app, width = 200, height = 260)
fr_ant_ctrl.grid(column = 0, row = 2, padx = 20, sticky = "WE")#, rowspan = 3
#app.grid_rowconfigure(3, weight = 1)
fr_ant_ctrl.grid_propagate(False)
fr_ant_ctrl.columnconfigure(0,weight = 1)
fr_ant_ctrl.columnconfigure(1,weight = 1)
label_7 = cstk.CTkLabel(fr_ant_ctrl, text = "Antenna switch", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3) #, width=200
label_7.grid(column = 0, row = 0, columnspan = 2, sticky = "EW") #
auto_radbutton = cstk.CTkRadioButton(fr_ant_ctrl, text = "Auto", variable = auto_switch, value = False, font = ("Cambria", 14), border_width_unchecked = 2, border_width_checked = 7, command = auto_on)
auto_radbutton.grid(column = 0, row = 1, pady = 5, padx = 3)
manual_radbutton = cstk.CTkRadioButton(fr_ant_ctrl, text = "Manual:", variable = auto_switch, value = True, font = ("Cambria", 14), border_width_unchecked = 2, border_width_checked = 7, command = manual_on)
manual_radbutton.grid(column = 0, row = 2, pady = 5, padx = 3)
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

fr_settings = cstk.CTkFrame(app, width = 200, height = 260)
fr_settings.grid(column = 1, row = 2, padx = 20, sticky = "WE")#, rowspan = 3
#app.grid_rowconfigure(4, weight = 1)
fr_settings.grid_propagate(False)
fr_settings.columnconfigure(0,weight = 1)
fr_settings.columnconfigure(1,weight = 1)
btn_1 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "Manula ant. \n orienation set.", font = ("Cambria", 14), command = ant_orientation_set_m)
btn_1.grid(column = 0, row = 0, sticky = "NWES", padx = 5, pady = 10)
btn_2 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "Set current \n ant. orienation", font = ("Cambria", 14), command = ant_orientation_set_a)
btn_2.grid(column = 1, row = 0, sticky = "NWES", padx = 5, pady = 10)
btn_3 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "App settings", font = ("Cambria", 14), command = create_new_window)
btn_3.grid(column = 0, columnspan = 2, row = 3, sticky = "NWES", padx = 35, pady = 25)
btn_4 = cstk.CTkButton(fr_settings, corner_radius = 3, text = "App info", font = ("Cambria", 14), command = app_info)
btn_4.grid(column = 0, columnspan = 2, row = 4, sticky = "NWES", padx = 35)#, pady = -10

label_14 = cstk.CTkLabel(fr_settings,  font = ("Cambria", 14), text = "Serial port:") #, width=200
label_14.grid(column = 0, columnspan =2, row = 1, sticky = "S", pady = 5)
com_menu = cstk.CTkOptionMenu(fr_settings, font = ("Cambria", 14), values = list_com, command = com_select, width = 30, anchor = "center", variable = com_TK)
com_menu.grid(column = 0, columnspan =2, row = 2, sticky = "N", pady = 5)
#app.grid_rowconfigure(5, weight = 1)
app.grid_rowconfigure(3, weight = 1, minsize = 20)

app.grid_rowconfigure(4, weight = 1)
fr_conn1 = cstk.CTkFrame(app, corner_radius=0, height = 20)#, width = 200
fr_conn1.grid(column = 0, row = 4, sticky = "WES")#, rowspan = 3, pady = 15
label_12 = cstk.CTkLabel(fr_conn1, textvariable = orbitron_conn_TK, font = ("Cambria", 12, "italic")) #, fg_color = "#d9d9d9", width=200, height = 15
label_12.pack(anchor = 's', side = "bottom")#.grid(column = 0, row = 3, sticky = "EW")#, pady = 18
fr_conn2 = cstk.CTkFrame(app, corner_radius=0, height = 20)#, width = 200, height = 260
fr_conn2.grid(column = 1, row = 4, sticky = "WES")#, rowspan = 3, padx = 15
label_13 = cstk.CTkLabel(fr_conn2, textvariable = switch_com_TK, font = ("Cambria", 12, "italic")) #, fg_color = "#d9d9d9", width=200, height = 15
label_13.pack(anchor = 's', side = "bottom")#grid(column = 1, row = 3, sticky = "EW")#, pady = 18

#app.grid_rowconfigure(6, weight = 1)
if dde_con:
    app.after(1500, update_data_from_orbitron)
else:
    app.after(2500, check_conn_orbitron)

#s_UI = schedule.every(3).minutes.do(read_U_I)
#app.after(0, serial_get_data)
#t = threading.Thread(target = serial_get_data, daemon = True)
#t.start()

#t1 = threading.Thread(target = update_data_from_switch, args = (ser_com,), daemon = True)
#t1 = threading.Thread(target = read_U_I, daemon = True)#, daemon = True
#t1.start()
t1 = threading.Timer(function = read_U_I, interval = delay_read_UI)#, daemon = True
t1.daemon = True
t1.start()

t2 = threading.Timer(function = read_temp, interval = delay_read_T)#, daemon = True
t2.daemon = True
t2.start()

t3 = threading.Timer(function = read_orient, interval = delay_read_C)#, daemon = True
t3.daemon = True
t3.start()
#t2 = threading.Thread(target = read_temp, daemon = True)
#t2.start()
#app.after(501, t1.start)
app.after(delay_read_T * 1000 + 3000, update_temp)#300100
app.after(delay_read_UI * 1000 + 3500, update_current_voltage)
app.after(delay_read_C * 1000 + 3000, update_orintation)#900100

if first_data:
    app.after(200, threading.Thread(target = update_data_from_switch, daemon = True).start)

#t2 = threading.Thread(target = update_temp, args = (ser_com,), daemon = True)


#app.after(5000, threading.Thread(target = read_U_I, daemon=True).start)#1800000
#app.after(60000, update_vlotage)
#app.after(8500, threading.Thread(target = read_temp, daemon=True).start)#900000
app.protocol("WM_DELETE_WINDOW", on_closing)#, s
app.mainloop()

