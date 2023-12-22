#########################################################################
# 
# LabVIEW TCP Server Client Script
# 
# 
# 
#########################################################################

import socket as _socket

_serverHost = '147.250.150.21'
_serverPort = 50007
isConnected = 0
_sockobj = None


def tirConnect():
	#'opens a connection to LabVIEW Server'
	global _sockobj, isConnected
	_sockobj = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)      # create socket
	try :
		a=_sockobj.connect((_serverHost, _serverPort))   # connect to LV
		isConnected= 1
	except :
		isConnected = 0
	return isConnected


def disconnect():
    #'closes the connection to LabVIEW Server'
    global isConnected
    try :
        _sockobj.close()                             # close socket
    except:
        pass
    isConnected = 0
    return isConnected


def passCommand(command):
    # passes a command to LabVIEW Server'
    try :
        _sockobj.send(command.encode())
        data = _sockobj.recv(65536)
    except :
        data=0
    #execString = "lvdata = " + data
    #exec execString
    return data

def Tir():
    recu=passCommand("Tir")
    return recu

