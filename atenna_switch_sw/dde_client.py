

import win32ui
import dde

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
s.Shutdown