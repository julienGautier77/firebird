# -*- coding: utf-8 -*-
"""
Created on 01 December 2023
@author: Julien Gautier (LOA)
last modified 22 decembre 2023

Dialog to RSAI motors rack via firebird database

"""

from firebird.driver import connect    ### pip install  firebird-driver
import time
from pyqtgraph.Qt import QtCore
import  socket
from  PyQt6.QtCore import QUuid


IPSoft = socket.gethostbyname(socket.gethostname()) # get the ip adress of the computer

UUIDSoftware = QUuid.createUuid() # create unique Id for software
UUIDSoftware = str(UUIDSoftware.toString()).replace("{","")
UUIDSoftware = UUIDSoftware.replace("}","")


# if not local  dsn=10.0.5.X/ ??

## connection to data base 
con = connect('C:\PilMotDB\PILMOTCONFIG.FDB', user='sysdba', password='masterkey')
cur = con.cursor()

def closeConnection():
    # close connection
    con.close()

" dict for table values"
listParaStr ={'nomAxe' : 2 ,'nomEquip':10, 'nomRef1': 1201 , 'nomRef2':1202 , 'nomRef3':1203 , 'nomRef4':1204 , 'nomRef5':1205 , 'nomRef6':1206 , 'nomRef7':1207 , 'nomRef8':1208 , 'nomRef9':1209 , 'nomRef10':1210}
listParaReal = {'Step':1106 , 'Ref1Val': 1211 , 'Ref2Val':1212 , 'Ref3Val':1213 , 'Ref4Val':1214 , 'Ref5Val':1215 , 'Ref6Val':1216 , 'Ref7Val':1217 , 'Ref8Val':1218 , 'Ref9Val':1219 , 'Ref10Val':1220}
listParaInt = {'ButLogPlus': 1009 , 'ButLogNeg':1010 }

def addSoftToConnectedList():
    # add adress ip of the soft in the data base 
    # not working yet  to do ...
    # need to create new Pikd for the table... 
    insert = ( "INSERT INTO TbConnectedList(d_ParaDbUUID, d_ParaDbConnectName,d_ParaDbAlias) values(%s,%s,%s)" % (str(UUIDSoftware),str(IPSoft),"" ))
    cur.execute(insert)
    con.commit()
    
def listProgConnected():
    # Read the list of programs connected to database
    # nbProgConnected :  number of programs connected into database
    # p_ListPrg (returned): Described list of programs into database
    #  (Format of the field of the list for one program: PkId, UUID, SoftName, Alias, Hostname, IpAddress, TimeConnection, HeartCnt)
    SoftName = []
    HostName = []
    IpProgram = []
    cur.execute("SELECT * FROM " + "TBCONNECTEDLIST" + " ORDER BY PkId;" )

    for row in cur:
        SoftName.append(row[2])
        HostName.append(row[4])
        IpProgram.append(row[5])
    nbProgConnected = len(SoftName)
    return nbProgConnected, SoftName, HostName, IpProgram

def rEquipmentList():
    '''
    Read the list of Equipment connected to database equipement =Rack =IPadress 
    Described list of equipment into database
    Format of the field of the list for one equipment: PkId, Address, Category, Status)
    '''
    addressEquipement=[]
    cur.execute("SELECT * FROM " + "TBEQUIPMENT")
    for row in cur:
        addressEquipement.append (row[1])
    return addressEquipement

def getValueWhere1ConditionAND(TableName, ValToRead, ConditionColName,ConditionValue):
    ''' 
    Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead'  FROM TableName WHERE ConditionColName = ConditionValue
    TableName : Table in which execute query
    ValToRead : Field Value to read
    ConditionColName : Column name for the condition of the query search
    ConditionValue : Value name for the condition of the query search
    return param p_DataRead : values read
    '''
   
    Prepare1Cond= "SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName + " = '" + ConditionValue + "' ;"
    cur.execute(Prepare1Cond )
    if cur is not None :
        for row in cur:
            p_DataRead=row[0]
    con.commit()
    return p_DataRead

def rEquipmentIdNbr(IpAddress):
    # Get Identification number of one PilMot equipement from its IP Address
    # IpAddress: IP Address
    #p_IdEquipment: Identification number of the equipement
    p_IdEquipment = getValueWhere1ConditionAND("TbEquipment", "PkId", "Address", IpAddress)
    
    return p_IdEquipment

def getSlotNumber(NoMotor):
    # Get the slot number of ESBIM corresponding to the motor number
    # return Slot number (value from 1 to 7)
    SlotNbr = 0
    SlotNbr = (NoMotor + 1 ) / 2
    return SlotNbr

def getAxisNumber(NoMotor):
 #Get the axis number of module corresponding to the motor number
 #return Slot number (value 1 or 2)
    AxisNbr = 1
    if(NoMotor % 2) == 0:
        AxisNbr = 2
    return AxisNbr

def readPkModBim2BOC(PkEsbim, NumSlotMod, NumAxis, FlgReadWrite=1):
    #  Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    #  PkEsbim : numero Equipment on which the module is plugged
    #  NumSlotMod : Number of the slot of the module to get PK
    #  NumAxis : Axis number of the module
    #  param FlgReadWrite : Indicate if the function accesses to Read or Write table (value : 1=ReadTb, 0=WriteTb)
    TbToRead = "TbBim2Boc_1Axis_W"

    cur.execute( "SELECT m.PkId FROM TbModule m INNER JOIN TbEquipment e ON m.idEquipment = e.PKID WHERE (e.PkId = " + str(int(PkEsbim)) + " and m.NumSlot = " + str(int(NumSlotMod)) + ");" )
   
    for row in cur :
        TmpPkModBim=row[0] # cle dans TbModule correspondant cle Esbim dans TbEquipement et numero du slot  
    
    cur.execute( "SELECT b.PkId FROM " + TbToRead + " b WHERE IdModule = " + str(TmpPkModBim) + " AND NumAxis = " + str(int(NumAxis)) + ";" );
    for row in cur :
        p_PKModBim =row[0]
    return p_PKModBim # cle dans TbBim2Boc_1Axis_W correpondant idmodule et au numero d axe



def nameMoteur(IpAdress,NoMotor):
    # Get motor name from Ipadress et axe number
    IdEquipt = rEquipmentIdNbr(IpAdress)
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    name=rStepperParameter(PkIdTbBoc,NoMotor,listParaStr['nomAxe'])
    return name

def listMotorName(IpAdress):
    #  List des moteurs sur l'equipement IpAdress
    IdEquipt = rEquipmentIdNbr(IpAdress)
    
    listSlot=[]
    SELECT = 'select NumSlot from %s  where  IdEquipment= %s and NumSlot>=0'% ('TbModule',str(IdEquipt))   # list SLot
    cur.execute(SELECT)
    for row in cur :
       listSlot.append(row[0])
    
    listNameMotor=[]
    for noMot in range (1,2*len(listSlot)+1): # dans notre cas 1...14
        listNameMotor.append(nameMoteur(IpAdress,noMot))
    return listNameMotor
 
def nameEquipment(IpAdress):
    # return the equipment name defined by IpAdress
    IdEquipt = rEquipmentIdNbr(IpAdress)
    SELECT = 'select PkId from %s  where  IdEquipment = %s and NumSlot = -1'% ('TbModule',str(IdEquipt))   # list Pkid module
    cur.execute(SELECT)
    for row in cur :
        PkIdMod = row[0]
    SELECT = 'select ValParam from %s where IDMODULE = %s and IDNAME = 10 '% ('TbParameterSTR',str(PkIdMod))
    cur.execute(SELECT)
    for row in cur :
        nameEquip=row[0]
    return nameEquip


def getValueWhere1ConditionAND(TableName, ValToRead, ConditionColName,ConditionValue):
    # Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead'  FROM TableName WHERE ConditionColName = ConditionValue
    # TableName : Table in which execute query
    # ValToRead : Field Value to read
    # ConditionColName : Column name for the condition of the query search
    # ConditionValue : Value name for the condition of the query search
    # return param p_DataRead : values read
    Prepare1Cond= "SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName + " = '" + ConditionValue + "' ;"
    cur.execute(Prepare1Cond )
    if cur is not None :
        for row in cur:
            p_DataRead=row[0]
    con.commit()
    return p_DataRead
    
def getValueWhere2ConditionAND(TableName, ValToRead, ConditionColName1, ConditionValue1, ConditionColName2, ConditionValue2):
    #  Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead' FROM TableName WHERE 'ConditionColName1' = 'ConditionValue1' AND 'ConditionColName2' = 'ConditionValue2' "
    #  TableName : Table in which execute query
    #  ValToRead : Field Value to read
    #  ConditionColName1 : First column name for the condition of the query search
    #  ConditionValue1 : First value name for the condition of the query search
    #  ConditionColName2 : Second column name for the condition of the query search
    #  ConditionValue2 : Second value name for the condition of the query search
    # return p_DataRead : values read
    cur.execute("SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName1 + " = '" + ConditionValue1 + "' AND " + ConditionColName2 + " = '" + ConditionValue2 + "' ;" )
    for row in cur:
        p_DataRead=row[0]
    con.commit()
    return p_DataRead

def getValueWhere3ConditionAND(TableName, ValToRead,  ConditionColName1, ConditionValue1, ConditionColName2, ConditionValue2, ConditionColName3,  ConditionValue3):
    #  Read the field value in a table where the 'column' equals 'value' corresponding Query = SELECT 'ValToRead' FROM TableName WHERE 'ConditionColName1' = 'ConditionValue1' AND 'ConditionColName2' = 'ConditionValue2' " ...
    #  param TableName : Table in which execute query
    #  ValToRead : Field Value to read
    #  ConditionColName1 : First column name for the condition of the query search
    #  ConditionValue1 : First value name for the condition of the query search
    #  ConditionColName2 : Second column name for the condition of the query search
    #  ConditionValue2 : Second value name for the condition of the query search
    #  ConditionColName3 : Third column name for the condition of the query search
    #  ConditionValue3 : Third value name for the condition of the query search
    cur.execute( "SELECT " + ValToRead  + " FROM " + TableName + " WHERE " + ConditionColName1 + " = '" + ConditionValue1 + "' AND " + ConditionColName2 + " = '" + ConditionValue2 + "' AND " + ConditionColName3 + " = '" + ConditionValue3 + "' ;" )
    for row in cur:
        p_DataRead=row[0]
    con.commit()
    return p_DataRead

def rEquipmentStatus(IpAddress): 
    # Read the status of an equipment from its IP Address
    status =getValueWhere1ConditionAND("TbEquipment", "status", "Address", IpAddress)
    return status

def rStepperParameter(PkIdTbBoc,NoMotor, NoParam):
    #  Read one stepper parameter
    #  PkIdTbBoc: Primary key identifier of an axis module Bim2BOC
    #  NoMotor: number of the motor on the equipment
    #  NoParam: number(Id) of the parameter to read
    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    #PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    PkIdModuleBIM = getValueWhere2ConditionAND( "TbBim2BOC_1Axis_R", "IdModule", "PkId", str(PkIdTbBoc), "NumAxis", str(NoAxis))
        
    if NoParam  in listParaStr.values()  : #  str 
        tbToread = "TbParameterSTR"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue    
    elif NoParam in listParaReal.values(): # Real
        tbToread="TbParameterREAL"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue 
    elif  NoParam in listParaInt.values(): # Int 
        tbToread="TbParameterINT"
        p_ReadValue = getValueWhere3ConditionAND(tbToread, "ValParam", "IdName", str(NoParam), "IdModule", str(PkIdModuleBIM), "NumAxis", str(NoAxis))
        return p_ReadValue 
    else :
        print( 'parameter value not valid')
        return 0

def wStepperParameter(IdEquipt,NoMotor, NoParam,valParam):
    #  write one stepper parameter
    #  param IdEquipt: Ident of equipment to read
    #  NoMotor: number of the motor on the equipment
    # NoParam: number(Id) of the parameter to read

    NoMod  = getSlotNumber(NoMotor)
    NoAxis = getAxisNumber(NoMotor)
    PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
    PkIdModuleBIM = getValueWhere2ConditionAND( "TbBim2BOC_1Axis_R", "IdModule", "PkId", str(PkIdTbBoc), "NumAxis", str(NoAxis))
    
    
    if NoParam  in listParaStr.values()  : #  str 
        tbToread = "TbParameterSTR"
        UPDATE = "UPDATE %s set ValParam ='%s' WHERE IdName= %s and IdModule =%s and NumAxis =%s" % (tbToread,valParam,str(NoParam),str(PkIdModuleBIM),str(NoAxis))
        cur.execute(UPDATE)
        con.commit()

    elif NoParam in listParaReal.values():
        tbToread="TbParameterREAL"
        UPDATE = "UPDATE %s set ValParam =%s WHERE IdName= %s and IdModule =%s and NumAxis =%s" % (tbToread,valParam,str(NoParam),str(PkIdModuleBIM),str(NoAxis))
        cur.execute(UPDATE)
        con.commit() 
    elif  NoParam in listParaInt.values():
        tbToread="TbParameterINT"
        UPDATE= "UPDATE %s set ValParam =%s WHERE IdName= %s and IdModule =%s and NumAxis =%s" % (tbToread,valParam,str(NoParam),str(PkIdModuleBIM),str(NoAxis))
        cur.execute(UPDATE)
        con.commit() 
    else :
        print( 'parameter value is not valid')
        return 0

def wStepperCmd(PkIdTbBoc, RegOrder, RegPosition, RegVelocity=1000):
    # Write a command to a stepper axis (BOCM)
    # PkIdTbBoc = readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1) 
    # CmdRegister: command register to write
    # SetpointPosition: Position setpoint
    # SetpointVelocity: Velocity setpoint
    # IdEquipt = rEquipmentIdNbr(IpAdress)
    # NoMod  = getSlotNumber(NoMotor)
    # NoAxis = getAxisNumber(NoMotor)
    # 
    # to do 
    # 
    if getValueWhere1ConditionAND('TBBIM2BOC_1AXIS_W','Cmd','PkId',str(PkIdTbBoc)) ==0  or getValueWhere1ConditionAND('TBBIM2BOC_1AXIS_c','StateCmd','PkId',str(PkIdTbBoc)) == (0 or 3 or 4):

        UPDATE = 'UPDATE %s set RegOrder = %s, RegPosition = %s, RegVelocity = %s WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(RegOrder),str(RegPosition),str(RegVelocity),str(PkIdTbBoc))
        cur.execute(UPDATE)
        UPDATE = 'UPDATE  %s set cmd=1 WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(PkIdTbBoc)) # take write right
        cur.execute(UPDATE)
        con.commit()
        time.sleep(0.05) # ?? sinon ca marche pas ...
    #  todi test si commande est terminé cmd=3 ou 4 (erreur)
    # liberer le champ cmd =0 
        UPDATE = 'UPDATE  %s set  Cmd = 0 WHERE PkId =%s ' % ('TBBIM2BOC_1AXIS_W',str(PkIdTbBoc)) # clear commande right
        cur.execute(UPDATE)
        con.commit()
        time.sleep(0.05)


class MOTORRSAI():
    """Motor class Motor is defined by Ipadress of the rack and  axis number 
    """

    def __init__(self, IpAdrress,NoMotor,parent=None):
            # RSAI motor class for 1 motor defined by mot1=str()
        self.IpAdress = IpAdrress
        self.NoMotor = NoMotor
        self.IdEquipt = rEquipmentIdNbr(self.IpAdress)
        self.NoMod  = getSlotNumber(self.NoMotor)
        self.NoAxis = getAxisNumber(self.NoMotor)
        self.PkIdTbBoc = readPkModBim2BOC(self.IdEquipt, self.NoMod, self.NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim
        self._name=rStepperParameter(self.PkIdTbBoc,NoMotor,listParaStr['nomAxe'])
    
    def position(self):
        # return motor postion
        posi = getValueWhere1ConditionAND("TbBim2BOC_1Axis_R", "PosAxis", "PkId", str(self.PkIdTbBoc))
        #↕print('position',posi)
        return  posi
    
    def getName(self):
        # get motor name
        self._name=rStepperParameter(self.PkIdTbBoc,self.NoMotor,listParaStr['nomAxe'])
        return self._name
    
    def setName(self,nom):
        # set motor name
        valParam = nom
        wStepperParameter(self.IdEquipt,self.NoMotor, listParaStr['nomAxe'],valParam)
        time.sleep(0.05)
        #self._name=nom

    def getRefName(self,nRef) :
        # set ref n° name
        key = listParaStr['nomRef'+str(nRef)]
        return rStepperParameter(self.PkIdTbBoc, self.NoMotor, key)
    
    def setRefName(self,nRef,name) :
        # set ref n° name
        key = listParaStr['nomRef'+str(nRef)]
        wStepperParameter(self.IdEquipt, self.NoMotor, key, name)   # to do change to self.PkIdTbBoc?

    
    def getRefValue(self,nRef) :
        # get value of the refereence position nRef
        key = listParaReal['Ref'+str(nRef)+'Val']
        return rStepperParameter(self.PkIdTbBoc, self.NoMotor, key)
    
    def setRefValue(self,nReff,value) :
        # set value of the refereence position nRef
        key=listParaReal['Ref'+str(nReff)+'Val']
        wStepperParameter(self.IdEquipt, self.NoMotor, key, value) # to do change to self.PkIdTbBoc?

    def getStepValue(self):
        # Valeur de 1 pas dans l'unites
        key=listParaReal['Step'] #1106
        
        return rStepperParameter(self.PkIdTbBoc, self.NoMotor, key)

    def getButLogPlusValue(self):
        key=listParaInt['ButLogPlus'] 
        return rStepperParameter(self.PkIdTbBoc, self.NoMotor, key)
    
    def setButLogPlusValue(self,butPlus):
        key=listParaInt['ButLogPlus'] 
        wStepperParameter(self.IdEquipt, self.NoMotor, key, butPlus) # to do change to self.PkIdTbBoc?
    
    def getButLogMoinsValue(self):
        key=listParaInt['ButLogNeg'] 
        return rStepperParameter(self.PkIdTbBoc, self.NoMotor, key)
    
    def setButLogMoinsValue(self,butMoins):
        key=listParaInt['ButLogNeg'] 
        wStepperParameter(self.IdEquipt, self.NoMotor, key, butMoins) # to do change to self.PkIdTbBoc?

    def rmove(self,posrelatif,vitesse=1000):
        # relative move of NoMotor of IpAdress
        # posrelatif = position to move in step
        RegOrder = 3
        print('relative move of ',posrelatif)
        wStepperCmd(self.PkIdTbBoc, RegOrder, RegPosition=posrelatif,RegVelocity=vitesse)  # to do change to self.PkIdTbBoc?

    def move(self,pos,vitesse=1000):
        # relative move of NoMotor  of IpAdress
        # pos = position to move in step
        RegOrder = 2
        wStepperCmd(self.PkIdTbBocr, RegOrder, RegPosition=pos,RegVelocity=vitesse)  # to do change to self.PkIdTbBoc?

    def setzero(self):
        """
        ## setzero(self.moteurname):Set Zero
        """
        RegOrder=10  #  commande pour zero le moteur 
        wStepperCmd(self.PkIdTbBoc, RegOrder, RegPosition=0,RegVelocity=0)  # to do change to self.PkIdTbBoc?
        
    def stopMotor(self): # stop le moteur motor
        """ stopMotor(motor): stop le moteur motor """
        RegOrder = 4
        wStepperCmd(self.PkIdTbBoc, RegOrder, RegPosition=0,RegVelocity=0)  # to do change to self.PkIdTbBoc?

    def etatMotor(self):
        # read status of the motor
        TbToRead = "TbBim2Boc_1Axis_R"
        # PkIdTbBoc = readPkModBim2BOC(self.IdEquipt, self.NoMod, self.NoAxis, FlgReadWrite=1) # Read Primary key identifier of an axis module Bim2BOC :  p_PkModBim 
        a =str( hex(getValueWhere1ConditionAND(TbToRead , "StatusAxis", "PkId", str(self.PkIdTbBoc))))
        
        if a=='0x2030' or a=='0x30' or a=='0x20': 
            etat='mvt'
        elif a=='0x2012' or a=='0x12' or a=='0x92' or a=='0x2082': 
            etat='FDC-'
        elif a=='0x2011' or a=='0x11' or a=='0x91' or a=='0x2081': 
            etat='FDC+'
        elif a=='0x2010' or a=='0x10' : 
            etat='ok'
        elif a=='0x2090' or a=='0x90' : 
            etat='ok'    
        elif a=='0x2090' or a=='0x80' : 
            etat='ok'
        elif a=='0x890' or a == '0x2890' or a == '0x880' or a=='0x8c0': 
            etat='Power off'
        
        else:
            etat=str(a)
    
        return etat

    def getEquipementName(self):
        # return the name of the equipement of which the motor is connected
        return nameEquipment(self.IpAdress)    







#list1=listMotorName('10.0.6.31')
#print(list1)
# dicts={}
# i=1
# for val in list1:
#     dicts[val] = i
#     i+=1
# print(dicts)

if __name__ == '__main__':

    a=MOTORRSAI('10.0.6.31', 2)
    pos=a.position()
# print(pos)
    print('name',pos)

# print('name motor ',a.getName())

#print('step',a.getStepValue())
# time.sleep(1)
# print('position',a.position())
# a.stopMotor()


    closeConnection()

