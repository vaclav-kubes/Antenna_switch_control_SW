# Antenna switch controller - SW

This Github page servs as presentation, help and archive page for *Antenna swtich controller* application, developed as part of bachelors thesis by Václav Kubeš at Department of radioelectronics FEEC BUT.
(New functions added in version 1.5 ([see sec New functions in ver1.5](#new-functions-in-ver15))- hopefully no more changes will be needed)
**Antenna switch controller app** is used for: 

 - Obtaining and evaluating diagnostic data from five chanell active antenna switch
 - Simple logging of error states base on diagnostic data
 - Manual control of switching of the antenna switch
 - Automatic control of switching of the antenna switch based on tracking data from Orbitron satellite tracking software

## Communication between *Antenna switch controller* app and antenna switch

The exchange of diagnostic data and commands is ensured by serial communication. 
Serial communication parameters are the following:

 - Baudrate: 9600 Bd
 - Frame: 8N1

To connect to antenna switch for the first time, you have to connect the inside unit with USB/Serial converter to your PC and then start the *Antenna switch controller* app. After that, you have to choose the COM port which corresponds to the connected inside unit with USB/Serial converter. After clicking on selected COM port from offered list of COM ports, serial connection will be established and if no problem with that will occur, the COM port will be saved into `config.txt` file, so next time connection will be established automatically. 

![screenshot of com select](/figs/ser_conn_COM_select.jpg)

To connect to antenna switch after first time setting, it will try to establish serial communication automatically if the inside unit is connected to PC before *Antenna switch controller* app start otherwise if internal unit is connected after app start, the COM port must be selected manually to establish connection.

To indicate if serial connection is fine, there is a status footer. If there is some problem with establishing the connection or received data,  `Switch: Disconnected` message will be displayed in the footer. 

When the connection is established, all diagnostic data are requested from the antenna switch and after their successful reception are displayed in appropriate boxes.

## Connection to Orbitron satellite tracking software
Tracking data from the Orbitron are handovered by DDE server. *Antenna switch controller* app will connect to the DDE server automatically. To start tracking data transfer there must be in the window `Rotor/Radio` of Orbitron, driver started. *Antenna switch controller* app  can be used as the driver, or any other driver can be used.  After successful connection and data transfer, azimuth and elevation of tracked satellite is displayed in corresponding boxes.

![screenshot of orbitron conection](/figs/orbitron_conn.jpg)

To indicate if connection to Orbitron is fine, there is a status footer. If there is some problem with transferred data from Orbitron or driver is not turned on,  `Orbitron: No data` message will be displayed in the footer. If Orbitron application is not running, then `Orbitron: Disconnected` message will be displayed. Otherwise, `Orbitron: Connected` label will be shown.

To add *Antenna switch controller* app as "driver" to Orbitron, `antenna_switch_ctrl.exe` is copied into your Orbitron directory and the `Setup.cfg` file in the [Drivers] directory is edited to include `antenna_switch_ctrl.exe` as a driver.
## Setting of absolute space orientation of antenna
At first start of *Antenna switch controller* app  orientation of switched antennas must be set. If not, then antennas will not be switched.

Absolute space orientation in this case means the azimuth of the centre of antenna one main lobe.

![ant orientation](/figs/ant_or_fig.jpg)

Orientation can be set in two ways:

 - **Manual entry:**: after clicking on `Manual ant. orientation set` button, entry dialog window will pop up and after filling up and clicking on `Ok` button, the azimuth is set, and it should appear in appropriate box. Note that only positive numbers in the range from 0 ° to 360 ° will be accepted.

![screenshot of manual antenna orinetation setting](/figs/ant_or_M_set.jpg)
   
 - **Auto measure entry:** after clicking on `Set current ant. orinetation` button, currently displayed value of measured antenna one azimuth will be set. If there is no data, then an info message will pop up.

Entered value is saved to `config.txt` file, so after initial setting there is no need for repeated entering.

## App settings - error thresholds
User can set error thresholds for received data. It can be done by clicking on `App settings` button. In new window, there can be set new ranges of error states for each diagnostic information. Default values are in the picture below:

![screenshot of app settings](/figs/app_settings.jpg)

If values are set correctly (upper value if higher than lower value...) they are saved to `config.txt` file, otherwise default values are used. 
When the value of one or more diagnostic data are in error range. `Warning!` message will occur in the lowest box of *Status info* frame and invalid values will be highlighted by red colour and values will be logged into `error_log.csv` file.

## Antenna switch control
Antenna switching can be set to **Auto mode**, **Manual mode** or can be switched off. 
When **Auto mode** is chosen, antennas are switched according to tracking data from Orbitron and set antenna orientation.
When **Manual mode** is chosen, radio buttons are enabled and user can set which antenna(s) should be switched on. The limit of number of switched on antennas is three.
All antennas can be switched off by clicking on **Off** check button.
Antennas in use are displayed in the lowest box of *Satellite position* frame.

## How to solve problems with *Antenna switch controller* app
The easiest solution is to close the app and start it again.

## Notes for program
- `config.txt` and `error_log.csv` are saved to the same file where `antenna_switch_ctrl.exe` is stored.
- Executable `antenna_switch_ctrl.exe` in antenna_switch_sw folder was compiled on Windows 10, x64.

## Notes for python source code
- External libraries not included in standard Python distribution are listed in [requirements.txt](/antenna_switch_sw/requirements.txt)
  - All of them can be installed by running: `pip install -r requirements.txt`
- Python 3.12.1 was used

## New functions in ver1.5
- Manuall refresh of all diagnostic data can be done via `Man. refresh` button.
- Elevation treshold of satellite position to switch to ant. 5 added to settings.
- Gray out boxes where diag. data from unit B should be disaplyed when unit B not connected.
- No lower treshold of current to LNAs.
