
from queue import Empty
from tkinter import *
import CTkMessagebox as msg
import customtkinter as cstk
import win32ui
import dde
from serial_com import *
import time
import threading
import queue

def on_closing():
    try:
        ser_com.close()
        s.Shutdown()
        t1.join(timeout=1)
        t2.join(timeout=1)
        app.destroy()
    except:
        app.destroy()

def read_U_I():
    while True:
        q.put(extract_val(get_curr_A(ser_com)[1]))
        time.sleep(0.07)
        q.put(extract_val(get_curr_B(ser_com)[1]))
        time.sleep(0.07)
        q.put(extract_val(get_fant_U(ser_com)[1]))
        time.sleep(3)

def read_temp():
    while True:
        q1.put(extract_val(get_temp_A(ser_com)[1]))
        time.sleep(0.07)
        q1.put(extract_val(get_temp_B(ser_com)[1]))
        time.sleep(5.1)

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

def update_current_voltage():#ser_com
    #data_A = extract_val(get_curr_A(ser_com)[1])
    #data_B = extract_val(get_curr_B(ser_com)[1])
    #data_V = extract_val(get_fant_U(ser_com)[1])
    #print(data_A)
    #print(data_B)
    #print(data_V)
    try:
        data_A = q.get()
        data_B = q.get()
        data_V = q.get()
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
    app.after(18001, update_current_voltage)

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
        data_A = q1.get()
        data_B = q1.get()

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
    app.after(47001, update_temp)#300000

def update_orintation(): #ser_com
    data = extract_val(get_compass(ser_com)[1])
    
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
    app.after(93001, update_orintation)#900000

def update_data_from_switch(): #[IA, IB, TA, TB, UF, EC, AN, CB] #ser_com
    #global ser_com
    if ser_com:
        data = extract_val(get_all(ser_com)[1])
        #print(data)
        #ser.close()
        cur_A_TK.set("{:.1f}".format(data[0]))
        cur_B_TK.set("{:.1f}".format(data[1]))
        temp_A_TK.set("{:.1f}".format(data[2]))
        temp_B_TK.set("{:.1f}".format(data[3]))
        fant_volt_TK.set("{:.1f}".format(data[4]))
        orientation_TK.set("{:.1f}".format(data[5]) + " °")
        if switch_com_TK.get() == "Switch: Disconnected":
            switch_com_TK.set("Switch: Connected")
    else:
        switch_com_TK.set("Switch: Disconnected")
        
    #app.after(1000, update_data_from_switch)

def update_data_from_orbitron():
    dde_data.set(c.Request("TrackingData"))
    data = dde_data.get()
    #print(dde_data.get())
    azimut_TK.set(get_AZ_EZ("AZ", data))
    elevation_TK.set(get_AZ_EZ("EL", data))
    if not auto_switch.get():
        #print("auto", auto_select_ant())
        ant_TK.set(str(auto_select_ant()))
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
        return elevation
        #print(elevation)

def ant_orientation_set():
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
            orientation_TK.set(text + " °")
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
                config.write(text + " °\n")
                config.close()
    except:
        msg.CTkMessagebox(title="No change.", message="No change.")
           
def auto_select_ant():
    try:
        ant_orintation = float(orientation_TK.get()[:-1])
        az = float(azimut_TK.get()[:-1])
        ant = 1
        if az >= divmod(ant_orintation - 45, 360)[1] and az <= divmod(ant_orintation + 45, 360)[1]:     
            ant = 1
        elif az >= divmod(ant_orintation + 45, 360)[1] and az <= divmod(ant_orintation + 135, 360)[1]:
            ant = 2
        elif az >= divmod(ant_orintation + 135, 360)[1] and az <= divmod(ant_orintation + 225, 360)[1]:
            ant = 3
        elif az >= divmod(ant_orintation + 225, 360)[1] and az <= divmod(ant_orintation + 315, 360)[1]:
            ant = 4
        return ant
    except:
        return 1

def com_select(choice):
    if ping(choice):
        #ser_com = serial_start(choice)
        switch_com_TK.set("Switch: Connected")
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
            #return ser_com   
        except:
            try:
                with open("config.txt", "w", encoding = "utf-8") as config:
                    config.writelines(["\n", choice + "\n"])
                    config.close()
            except:
                msg.CTkMessagebox(title="Settings not saved.", message = "Settings not saved. Error while saving the serial port setting.")
    else:
        switch_com_TK.set("Switch: Disconnected")

cstk.set_appearance_mode("System")
app = cstk.CTk()
app.geometry("530x590")
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
el_comp_TK = cstk.StringVar()
c_ant = cstk.StringVar()
conn_B = cstk.StringVar()
list_com = []
config_com = ""

q = queue.Queue()
q1 = queue.Queue()
#create a DDE client and start conversation
s = dde.CreateServer()
#the parameter in brackets is the name of this Python file (AddLayers.py)
s.Create("GetData")
#create a conversation between client and server
c = dde.CreateConversation(s)
c.ConnectTo("Orbitron", "Tracking")

#if the connection succeeds, proceed with requests to PhotoModeler
if c.Connected() == 1:
    print("Connection established")
    print(c.Request("TrackingData"))
    orbitron_conn_TK.set("Orbitron: Connected")
else:
    azimut_TK.set("??")
    elevation_TK.set("??")
    orbitron_conn_TK.set("Orbitron: Disconnected")
    s.Shutdown()


try:
    config = open("config.txt", "r", encoding = "utf-8")
    orientation_TK.set(config.readline())
    config_com = config.readline()
    #print(config_com)
    config.close()
except:
    config = open("config.txt", "x", encoding = "utf-8")
    config.close()

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
    else:
        switch_com_TK.set("Switch: Disconnected")
        ser_com = None
else:
    switch_com_TK.set("Switch: Disconnected")
    ser_com = None



label_1 = cstk.CTkLabel(app, text = "Antenna switch controller", font = ("Cambria", 20, "bold"), anchor = "center")
label_1.grid(column = 0, row = 0, columnspan = 2, sticky = "NSEW")

fr_sat_pos = cstk.CTkFrame(app, width=200, height=200) #, width=200, height=200, fg_color="#e3e3e3"
fr_sat_pos.grid(column = 0, row = 1, rowspan = 2, padx = 20, pady = 20, sticky = "NSEW")#
fr_sat_pos.grid_propagate(False)
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
entry_3 = cstk.CTkEntry(fr_sat_pos, font = ("Cambria", 14), state = "disabled", width = 80, textvariable = ant_TK)
entry_3.grid(column = 0, row = 4, columnspan = 2, padx = 15, sticky = "NSEW")

fr_status = cstk.CTkFrame(app, width = 250, height = 230)
fr_status.grid(column = 1, row = 1, rowspan = 2, padx = 20, pady = 20, sticky = "NSEW")
fr_status.columnconfigure(0,weight = 1)
fr_status.columnconfigure(1,weight = 1)
fr_status.columnconfigure(2,weight = 1)
fr_status.grid_propagate(False)
label_6 = cstk.CTkLabel(fr_status, text = "Status info", font = ("Cambria", 15.5, "italic"), fg_color = "#a0a3a8", corner_radius = 3, width=200)
label_6.grid(column = 0, row = 0, columnspan = 3, sticky = "NSEW")

label_8 = cstk.CTkLabel(fr_status, text = "Phantom voltage [V]:", font = ("Cambria", 14))
label_8.grid(column = 0, row = 1, pady = 5, padx = 5, sticky = "E")
entry_4 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = fant_volt_TK)
entry_4.grid(column = 1, row = 1, columnspan = 2, padx = 2, sticky = "WE")

label_9 = cstk.CTkLabel(fr_status, text = "Currnet to LNAs [mA]:", font = ("Cambria", 14))
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

label_11 = cstk.CTkLabel(fr_status, text = "Ant. orientation:", font = ("Cambria", 14))
label_11.grid(column = 0, row = 4, pady = 5, padx = 5, sticky = "E")
entry_7 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70, textvariable = orientation_TK)
entry_7.grid(column = 1, row = 4, columnspan = 2, padx = 2, sticky = "WE")

entry_11 = cstk.CTkEntry(fr_status, font = ("Cambria", 14), state = "disabled", width = 70)
entry_11.grid(column = 0, row = 5, columnspan = 3, padx = 20, pady = 15, sticky = "WE")

fr_ant_ctrl = cstk.CTkFrame(app, width = 200, height = 260)
fr_ant_ctrl.grid(column = 0, rowspan = 3, row = 3, padx = 20, sticky = "WE")
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

btn_1 = cstk.CTkButton(app, corner_radius = 3, text = "Manula antenna \n orienation setting", font = ("Cambria", 14), command = ant_orientation_set)
btn_1.grid(column = 1, row = 3, sticky = "N")

label_14 = cstk.CTkLabel(app,  font = ("Cambria", 14), text = "Serial port:") #, width=200
label_14.grid(column = 1, row = 4, sticky = "S", pady = 5)
com_menu = cstk.CTkOptionMenu(app, font = ("Cambria", 14), values = list_com, command = com_select, width = 30, anchor = "center", variable = com_TK)
com_menu.grid(column = 1, row = 5, sticky = "N", pady = 5)

label_12 = cstk.CTkLabel(app, textvariable = orbitron_conn_TK, font = ("Cambria", 12, "italic"), fg_color = "#d9d9d9", height = 15) #, width=200
label_12.grid(column = 0, row = 6, sticky = "EWNS", pady = 18)
label_13 = cstk.CTkLabel(app, textvariable = switch_com_TK, font = ("Cambria", 12, "italic"), fg_color = "#d9d9d9", height = 15) #, width=200
label_13.grid(column = 1, row = 6, sticky = "EWNS", pady = 18)

app.after(500, update_data_from_orbitron)
#t1 = threading.Thread(target = update_data_from_switch, args = (ser_com,), daemon = True)
t1 = threading.Thread(target = read_U_I, daemon = True)#, daemon = True
t1.start()
t2 = threading.Thread(target = read_temp, daemon = True)
t2.start()
#app.after(501, t1.start)
app.after(501, update_data_from_switch)

#t2 = threading.Thread(target = update_temp, args = (ser_com,), daemon = True)
app.after(5700, update_temp)
app.after(5000, update_current_voltage)
#app.after(8000,update_orintation)

#app.after(18001, threading.Thread(target = update_current_voltage, args = (ser_com,)).start())#1800000
#app.after(60000, update_vlotage)
#app.after(90001, threading.Thread(target = update_orintation, args = (ser_com,)).start())#900000
app.protocol("WM_DELETE_WINDOW", on_closing)#, s
app.mainloop()

