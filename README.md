# Antenna switch controller - SW

This Github page servs as presentation, help and archive page for *Antenna swtich controller* application, developed as part of bachelors thesis by Václav Kubeš at Department of radioelectronics FEEC BUT.

**Antenna switch controller app** is used for: 

 - Obtaining and evaluating diagnostic data from five chanell active antenna switch
 - Simple logging of error states base on diagnostic data
 - Manual control of switching of the antenna switch
 - Automatic control of switching of the antenna switch based on tracking data from Orbitron satellite tracking software

## Communication between *Antenna switch controller* app and antenna switch

The exchange of diagnostic data and commands is ensured by serial communication. 
Serial communication parameters are following:

 - Baudrate: 9600 Bd
 - Frame: 8N1

To connect to antenna switch for the first time, you have to connect inside unit with USB/Serial converter to your PC and then start the *Antenna switch controller* app. Afther that you have to choose the COM port whitch corresponds to the connected inside unit with USB/Serial convertor. After clicking on selected COM port from offered list of COM ports, serial connection will be estabilished and if no problem with that will occure, the COM port will be saved into `config.txt` file, so next time connection will be estabilished automatically. 

To connect to antenna switch after first time setting, it app will try to estabilish serial communication automatically if the inside unit is connected to PC before *Antenna switch controller* app start otherwise if internal unit is connected after app start, the COM port must be selected manualy to estabilish connection.

To indicate if serial connection is fine, there is status footer. If there is some problem with estabilishing the connection or recieved data,  `Switch: Disconnected` message will be displayed in the footer. 

When the connection is estabilished, all diagnostic data are requested from the antenna switch and after their succesfull reception are displayed in appropriate boxes.

## Connection to Orbitorn satellite tracking software
Tracking data from the Orbitron are handovered by DDE server. *Antenna switch controller* app will connect to the DDE server automatically. To start tracking data transfer there must be in the window `Rotor/Radio` of Orbitron, driver started. *Antenna switch controller* app  can be used as the driver or any other driver can be used.  After succesfull connection and data transfer azimuth and elevation of tracked sattelite is displayed in corresponding boxes.

To indicate if connection to Orbitron is fine, there is status footer. If there is some problem with transfered data form Orbitron or driver is not turned on,  `Orbitron: No data` message will be displayed in the footer. If Orbitron application is not running then `Orbitron: Disconnected` message will be displayed. Otherwise `Orbitron: Connected` label will be shown.

## Setting of absolute space orientation of antenna
At first start of *Antenna switch controller* app  orintation of switched antennas must be set. If not, then antennas will not be switched.

Absolute space orintation in this case means the azimuth of center of antenna one main lobe.

Orientation can be set in to ways:

 - **Manual entry:**: after clicking on `Manual ant. orientation set` button, entry dialog will pop up and after filling up and clicking on `Ok` button, the azimuth is set and it should appear in appropriate box. Note that only positive numbers in range from 0 ° to 360 ° will be accepted.
 - **Auto measure entry:** after clicking on `Set current ant. orinetation` button, currenty displayed value of measured antenna one azimuth will be set. If there is no data, then info message will pop up.

Entered value is saved to `config.txt` file, so after initial setting there is no need for repeated entering.

## App settings - error tresholds
User can set error tresholds for recieved data. It can be done by clicking on `App settings` button. In new window there can be set new ranges of error states for each diagnostic information. Default values are in the picture below:
If values are set correctly (upper value if higher than lower value...) they are saved to `config.txt` file, otherwise default values are used. 
When value of one or more diagnostic data are in error range. `Warning!` message will occure in the lowest box of *Status info* frame and invalid values will be highlighted by red colour and values will be logged into `error_log.csv` file.

## Antenna switch controll
Antenna switching can be set to **Auto mode**, **Manual mode** or can be switched off. 
When **Auto mode** is choosen, antennas are switched according to tracking data from Orbitron and set antenna orinetation.
When **Manual mode** is choosen, radiobuttons are enabled and user can set whitch antenna(s) should be switched on. Limit of number of switched on antennas is three.
All antennas can be sitched off by clicking on **Off** checkbutton.
Antennas in use are displayed in lowest box of *Satellite position* frame.
## How to solve problems with *Antenna switch controller* app
The easiest solution is to close the app and start it again.
