# -*- coding: utf-8 -*-
"""
Created on 10 December 2023

@author: Julien Gautier (LOA)
last modified 15 decembre 2023
"""

#%%Import
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget, QMessageBox, QLineEdit, QToolButton
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QDoubleSpinBox, QCheckBox
from PyQt6.QtWidgets import QComboBox, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QRect

import sys
import time
import os
import qdarkstyle
import pathlib
import moteurRSAIFDB 
import __init__     
from scanMotor import SCAN

#import TirGui
__version__=__init__.__version__



class ONEMOTORGUI(QWidget) :
    """
    User interface Motor class : 
    ONEMOTOGUI(IpAddress, NoMotor,nomWin,showRef,unit,jogValue )
    IpAddress : Ip adress of the RSAI RACK
    NoMoro : Axis number
    optional :
        nomWin Name of the windows
        ShowRef = True see the reference windows
        unit : 0: step 1: um 2: mm 3: ps 4: °
        jogValue : Value in unit of the jog
    """

    def __init__(self, IpAdress, NoMotor, nomWin='', showRef=False, unit=1, jogValue=100, parent=None):
       
        super(ONEMOTORGUI, self).__init__(parent)
        
        p = pathlib.Path(__file__)
        sepa = os.sep
        self.icon = str(p.parent) + sepa + 'icons' +sepa
        self.isWinOpen = False
        
        self.refShowId = showRef
        self.indexUnit = unit
        self.jogValue = jogValue
        self.etat='ok'
        #self.tir=TirGui.TIRGUI()
        self.IpAdress = IpAdress
        self.NoMotor = NoMotor
        self.MOT=[0]
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.iconPlay = self.icon+"playGreen.PNG"
        self.iconPlay = pathlib.Path(self.iconPlay)
        self.iconPlay = pathlib.PurePosixPath(self.iconPlay)

        self.iconMoins = self.icon+"moinsBleu.PNG"
        self.iconMoins = pathlib.Path(self.iconMoins)
        self.iconMoins = pathlib.PurePosixPath(self.iconMoins)

        self.iconPlus = self.icon+"plusBleu.PNG"
        self.iconPlus = pathlib.Path(self.iconPlus)
        self.iconPlus = pathlib.PurePosixPath(self.iconPlus)

        self.iconStop = self.icon+"close.PNG"
        self.iconStop = pathlib.Path(self.iconStop)
        self.iconStop = pathlib.PurePosixPath(self.iconStop)
    
        self.MOT[0]=moteurRSAIFDB.MOTORRSAI(self.IpAdress,self.NoMotor)
            
        self.scanWidget=SCAN(MOT=self.MOT[0]) # for the scan
        
        self.stepmotor = [0,0,0]
        self.butePos = [0,0,0]
        self.buteNeg = [0,0,0]
        self.name = [0,0,0]
        
        for zzi in range(0,1):
            
            self.stepmotor[zzi] = float(1/(self.MOT[0].getStepValue())) # list of stepmotor values for unit conversion
            self.butePos[zzi] = float(self.MOT[0].getButLogPlusValue()) # list 
            self.buteNeg[zzi] = float(self.MOT[0].getButLogMoinsValue())
            self.name[zzi] = str(self.MOT[0].getName())
        
        self.setWindowTitle(nomWin + str(self.MOT[0].getEquipementName()) + ' ('+ str(self.IpAdress)+ ')  '+ ' [M'+ str(self.NoMotor) + ']  ' + self.name[0]     )
        
        self.thread = PositionThread(self,mot=self.MOT[0]) # thread for displaying position
        self.thread.POS.connect(self.Position)
        self.thread.ETAT.connect(self.Etat)
        
        
        
        ## initialisation of the jog value 
        if self.indexUnit == 0: #  step
            self.unitChange = 1
            self.unitName = 'step'
            
        if self.indexUnit == 1: # micron
            self.unitChange = float((1*self.stepmotor[0])) 
            self.unitName = 'um'
        if self.indexUnit == 2: #  mm 
            self.unitChange = float((1000*self.stepmotor[0]))
            self.unitName = 'mm'
        if self.indexUnit == 3: #  ps  double passage : 1 microns=6fs
            self.unitChange = float(1*self.stepmotor[0]/0.0066666666) 
            self.unitName = 'ps'
        if self.indexUnit == 4: #  en degres
            self.unitChange = 1 *self.stepmotor[0]
            self.unitName = '°'    
        
        self.setup()
        
        self.unit()
        self.jogStep.setValue(self.jogValue)
        
    def startThread2(self):
        self.thread.ThreadINIT()
        self.thread.start()
        time.sleep(0.1)
        
        
    def setup(self):
        
        vbox1 = QVBoxLayout() 
        hboxTitre = QHBoxLayout()
        self.nom = QLabel(self.name[0])
        self.nom.setStyleSheet("font: bold 20pt;color:yellow")
        hboxTitre.addWidget(self.nom)
        
        self.enPosition = QLineEdit()
        #self.enPosition.setMaximumWidth(50)
        self.enPosition.setStyleSheet("font: bold 15pt")
        self.enPosition.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        hboxTitre.addWidget(self.enPosition)
        self.butNegButt = QCheckBox('But Neg',self)
        hboxTitre.addWidget(self.butNegButt)
       
        self.butPosButt = QCheckBox('But Pos',self)
        hboxTitre.addWidget(self.butPosButt)
        vbox1.addLayout(hboxTitre)
        #vbox1.addSpacing(10)
        
        hShoot=QHBoxLayout()
        self.shootCibleButton = QPushButton('Shot')
        self.shootCibleButton.setStyleSheet("font: 12pt;background-color: red")
        self.shootCibleButton.setMaximumWidth(100)
        self.shootCibleButton.setMinimumWidth(100)
        hShoot.addWidget(self.shootCibleButton)
        vbox1.addLayout(hShoot)
        
        hbox0=QHBoxLayout()
        self.position = QLabel('1234567')
        self.position.setMaximumWidth(300)
        self.position.setStyleSheet("font: bold 40pt" )
        
        self.unitBouton = QComboBox()
        self.unitBouton.addItem('Step')
        self.unitBouton.addItem('um')
        self.unitBouton.addItem('mm')
        self.unitBouton.addItem('ps')
        self.unitBouton.addItem('°')
        self.unitBouton.setMaximumWidth(100)
        self.unitBouton.setMinimumWidth(100)
        self.unitBouton.setStyleSheet("font: bold 12pt")
        self.unitBouton.setCurrentIndex(self.indexUnit)
        
        self.zeroButton = QPushButton('Zero')
        self.zeroButton.setMaximumWidth(50)
        
        hbox0.addWidget(self.position)
        hbox0.addWidget(self.unitBouton)
        hbox0.addWidget(self.zeroButton)
        vbox1.addLayout(hbox0)
        #vbox1.addSpacing(10)
        
        hboxAbs=QHBoxLayout()
        absolueLabel = QLabel('Absolue mouvement')
#        absolueLabel.setStyleSheet("background-color: green")
        self.MoveStep = QDoubleSpinBox()
        self.MoveStep.setMaximum(1000000)
        self.MoveStep.setMinimum(-1000000)
        #self.MoveStep.setStyleSheet("background-color: green")
        
        self.absMvtButton = QToolButton()
        
        self.absMvtButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlay,self.iconPlay))
        
        self.absMvtButton.setMinimumHeight(50)
        self.absMvtButton.setMaximumHeight(50)
        self.absMvtButton.setMinimumWidth(50)
        self.absMvtButton.setMaximumWidth(50)
        #self.absMvtButton.setStyleSheet("background-color: green")
        hboxAbs.addWidget(absolueLabel)
        hboxAbs.addWidget(self.MoveStep)
        hboxAbs.addWidget(self.absMvtButton)
        vbox1.addLayout(hboxAbs)
        vbox1.addSpacing(10)
        hbox1 = QHBoxLayout()
        self.moins = QToolButton()
        self.moins.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconMoins,self.iconMoins))
        
        self.moins.setMinimumHeight(70)
        self.moins.setMaximumHeight(70)
        self.moins.setMinimumWidth(70)
        self.moins.setMaximumWidth(70)
        
        #self.moins.setStyleSheet("border-radius:20px")
        hbox1.addWidget(self.moins)
        
        self.jogStep = QDoubleSpinBox()
        self.jogStep.setMaximum(1000000)
        self.jogStep.setMaximumWidth(130)
        self.jogStep.setStyleSheet("font: bold 12pt")
        self.jogStep.setValue(self.jogValue)
  
        hbox1.addWidget(self.jogStep)
        
        self.plus = QToolButton()
        self.plus.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlus,self.iconPlus))
        self.plus.setMinimumHeight(70)
        self.plus.setMaximumHeight(70)
        self.plus.setMinimumWidth(70)
        self.plus.setMaximumWidth(70)
        #self.plus.setStyleSheet("border-radius:20px")
        hbox1.addWidget(self.plus)
        
        vbox1.addLayout(hbox1)
        #vbox1.addStretch(10)
        vbox1.addSpacing(10)
        
        hbox2=QHBoxLayout()
        self.stopButton = QToolButton()
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconStop,self.iconStop))
        
        #self.stopButton.setStyleSheet("border-radius:20px;background-color: red")
        self.stopButton.setMaximumHeight(70)
        self.stopButton.setMaximumWidth(70)
        self.stopButton.setMinimumHeight(70)
        self.stopButton.setMinimumWidth(70)
        hbox2.addWidget(self.stopButton)
        vbox2=QVBoxLayout()
        
        self.showRef = QPushButton('Show Ref')
        self.showRef.setMaximumWidth(90)
        vbox2.addWidget(self.showRef)
        self.scan = QPushButton('Scan')
        self.scan.setMaximumWidth(90)
        vbox2.addWidget(self.scan)
        hbox2.addLayout(vbox2)
        
        vbox1.addLayout(hbox2)
        vbox1.addSpacing(10)
        
        self.REF1 = REF1M(num=1)
        self.REF2 = REF1M(num=2)
        self.REF3 = REF1M(num=3)
        self.REF4 = REF1M(num=4)
        self.REF5 = REF1M(num=5)
        self.REF6 = REF1M(num=6)
        
        grid_layoutRef = QGridLayout()
        grid_layoutRef.setVerticalSpacing(4)
        grid_layoutRef.setHorizontalSpacing(4)
        grid_layoutRef.addWidget(self.REF1,0,0)
        grid_layoutRef.addWidget(self.REF2,0,1)
        grid_layoutRef.addWidget(self.REF3,1,0)
        grid_layoutRef.addWidget(self.REF4,1,1)
        grid_layoutRef.addWidget(self.REF5,2,0)
        grid_layoutRef.addWidget(self.REF6,2,1)
        
        self.widget6REF = QWidget()
        self.widget6REF.setLayout(grid_layoutRef)
        vbox1.addWidget(self.widget6REF)
        self.setLayout(vbox1)
        
        self.absRef = [self.REF1.ABSref,self.REF2.ABSref,self.REF3.ABSref,self.REF4.ABSref,self.REF5.ABSref,self.REF6.ABSref] 
        self.posText = [self.REF1.posText,self.REF2.posText,self.REF3.posText,self.REF4.posText,self.REF5.posText,self.REF6.posText]
        self.POS = [self.REF1.Pos,self.REF2.Pos,self.REF3.Pos,self.REF4.Pos,self.REF5.Pos,self.REF6.Pos]
        self.Take = [self.REF1.take,self.REF2.take,self.REF3.take,self.REF4.take,self.REF5.take,self.REF6.take]
        
        self.actionButton()
        self.jogStep.setFocus()
        self.refShow()
        
    def actionButton(self):
        '''
           buttons action setup 
        '''
        self.unitBouton.currentIndexChanged.connect(self.unit) #  unit change
        self.absMvtButton.clicked.connect(self.MOVE)
        self.plus.clicked.connect(self.pMove) # jog + foc
        self.plus.setAutoRepeat(False)
        self.moins.clicked.connect(self.mMove)# jog - fo
        self.moins.setAutoRepeat(False) 
        self.scan.clicked.connect(lambda:self.open_widget(self.scanWidget) )    
        self.zeroButton.clicked.connect(self.Zero) # reset display to 0
        #self.refZeroButton.clicked.connect(self.RefMark) # todo
        self.stopButton.clicked.connect(self.StopMot)#stop motors 
        self.showRef.clicked.connect(self.refShow) # show references widgets
        self.shootCibleButton.clicked.connect(self.ShootAct)
        iii = 1
        for saveNameButton in self.posText: # reference name
            saveNameButton.textChanged.connect(self.savName)
            saveNameButton.setText(self.MOT[0].getRefName(iii)) # print  ref name
            iii+=1   

        for posButton in self.POS: # button GO
            posButton.clicked.connect(self.ref)    # go to reference value
        eee = 1   
        for absButton in self.absRef: 
            nbRef = str(eee)
            absButton.setValue(float(self.MOT[0].getRefValue(eee)/self.unitChange)) # save reference value
            absButton.editingFinished.connect(self.savRef) # sauv value
            eee+=1
       
        for takeButton in self.Take:
            takeButton.clicked.connect(self.take) # take the value 
        
    def open_widget(self,fene):
        
        """ open new widget 
        """
        
        if fene.isWinOpen is False:
            #New widget"
            fene.show()
            fene.isWinOpen=True
    
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()
        
    def refShow(self):
        
        if self.refShowId is True:
            #self.resize(368, 345)
            self.widget6REF.show()
            self.refShowId = False
            self.showRef.setText('Hide Ref')
            self.setFixedSize(430,800) 
        else:
            #print(self.geometry()
            self.widget6REF.hide()
            self.refShowId = True
            self.showRef.setText('Show Ref')
            self.setFixedSize(430,380)
    
    def MOVE(self):
        '''
        absolue mouvment
        '''
        a=float(self.MoveStep.value())
        a=float(a*self.unitChange) # changement d unite
        if a<self.buteNeg[0] :
            print( "STOP : Butée Négative")
            self.butNegButt.setChecked(True)
            self.MOT[0].stopMotor()
        elif a>self.butePos[0] :
            print( "STOP : Butée Positive")
            self.butPosButt.setChecked(True)
            self.MOT[0].stopMotor()
        else :
            self.MOT[0].move(a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)
    
    def pMove(self):
        '''
        action jog + foc 
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChange)
        b=self.MOT[0].position()
        
        if b+a>self.butePos[0] :
            print( "STOP :  Positive switch")
            self.MOT[0].stopMotor()
            self.butPosButt.setChecked(True)
        else :
            self.MOT[0].rmove(a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)
            
    def mMove(self): 
        '''
        action jog - foc
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChange)
        b=self.MOT[0].position()
        if b-a<self.buteNeg[0] :
            print( "STOP : negative switch")
            self.MOT[0].stopMotor()
            self.butNegButt.setChecked(True)
        else :
            self.MOT[0].rmove(-a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)
  
    def Zero(self): #  zero 
        self.MOT[0].setzero()

    def RefMark(self): # 
        """
            todo ....
        """
        #self.motorType.refMark(self.motor)
   
    def unit(self):
        '''
        unit change mot foc
        '''
        self.indexUnit = self.unitBouton.currentIndex()
        valueJog = self.jogStep.value()*self.unitChange
        
        if self.indexUnit == 0: #  step
            self.unitChange = 1
            self.unitName = 'step'
            
        if self.indexUnit == 1: # micron
            self.unitChange = float((1*self.stepmotor[0])) 
            self.unitName = 'um'
        if self.indexUnit == 2: #  mm 
            self.unitChange = float((1000*self.stepmotor[0]))
            self.unitName = 'mm'
        if self.indexUnit == 3: #  ps  double passage : 1 microns=6fs
            self.unitChange = float(1*self.stepmotor[0]/0.0066666666) 
            self.unitName = 'ps'
        if self.indexUnit == 4: #  en degres
            self.unitChange = 1 *self.stepmotor[0]
            self.unitName = '°'    
            
        if self.unitChange == 0:
            self.unitChange = 1 #avoid /0 
            
        self.jogStep.setSuffix(" %s" % self.unitName)
        self.jogStep.setValue(valueJog/self.unitChange)
        self.MoveStep.setSuffix(" %s" % self.unitName)

        eee=1
        for absButton in self.absRef: 
            nbRef = str(eee)
            absButton.setValue(float(self.MOT[0].getRefValue(nbRef))/self.unitChange)
            absButton.setSuffix(" %s" % self.unitName)
            eee+=1
        
    def StopMot(self):
        '''
        stop all motors
        '''
        self.REF1.show()
        for zzi in range(0,1):
            self.MOT[zzi].stopMotor();

    def Position(self,Posi):
        ''' 
        Position  display read from the second thread
        '''
        print(Posi)
        Pos=Posi[0]
        self.etat=str(Posi[1])
        a = float(Pos)
        b=a # value in step
        a=a/self.unitChange # value with unit changed
        
        if self.etat == 'FDC-':
            self.enPosition.setText('FDC -')
            self.enPosition.setStyleSheet('font: bold 28pt;color:red')
            
        elif self.etat == 'FDC+':
            self.enPosition.setText('FDC +')
            self.enPosition.setStyleSheet('font: bold 28pt;color:red')
        elif self.etat == 'Power off' :
            
            self.enPosition.setText('Power Off')
            self.enPosition.setStyleSheet('font: bold 14pt;color:red')
        elif self.etat=='mvt' :
             self.enPosition.setText('Moving...')
             self.enPosition.setStyleSheet('font: bold 28pt;color:white')

        if moteurRSAIFDB.rEquipmentStatus(self.IpAdress) == -1 :
            self.enPosition.setText('Rack not connected')
            self.enPosition.setStyleSheet('font: bold 14pt;color:red')

        self.position.setText(str(round(a,2))) 
        self.position.setStyleSheet('font: bold 40pt;color:white')
            
        positionConnue = 0 # 
        precis = 5 # to show position name
        if positionConnue==0 and (self.etat == 'ok' or self.etat == '?'):
            for nbRefInt in range(1,7):
                nbRef=str(nbRefInt)
                if float(self.MOT[0].getRefValue(nbRef))-precis<b< float(self.MOT[0].getRefValue(nbRef))+precis:
                    self.enPosition.setText(str(self.MOT[0].getRefName(nbRef)))
                    positionConnue=1
        if positionConnue==0 and (self.etat == 'ok' or self.etat == '?'):
            self.enPosition.setText('?' ) 
        
    def Etat(self,etat):
        # return  motor state  
        self.etat=etat
    
    def take (self) : 
        ''' 
        take and save the reference
        '''
        sender=QtCore.QObject.sender(self) # take the name of  the button 
        
        nbRef=str(sender.objectName()[0])
        
        reply=QMessageBox.question(None,'Save Position ?',"Do you want to save this position ?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
               tpos=float(self.MOT[0].position())
               
               self.MOT[0].setRefValue(nbRef,tpos)
               self.absRef[int(nbRef)-1].setValue(tpos/self.unitChange)
               print ("Position saved",tpos)
               
    def ref(self):  
        '''
        Move the motor to the reference value in step : GO button
        '''
        sender=QtCore.QObject.sender(self)
        reply=QMessageBox.question(None,'Go to this Position ?',"Do you want to GO to this position ?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            nbRef=str(sender.objectName()[0])
            for i in range (0,1):
                vref=int(self.MOT[i].getRefValue(nbRef))
                if vref<self.buteNeg[i] :
                    print( "STOP : negative switch")
                    self.butNegButt.setChecked(True)
                    self.MOT[i].stopMotor()
                elif vref>self.butePos[i] :
                    print( "STOP : positive switch")
                    self.butPosButt.setChecked(True)
                    self.MOT[i].stopMotor()
                else :
                    self.MOT[i].move(vref)
                    self.butNegButt.setChecked(False)
                    self.butPosButt.setChecked(False) 

    def savName(self) :
        '''
        Save reference name
        '''
        sender=QtCore.QObject.sender(self)
        nbRef=sender.objectName()[0] #PosTExt1
        vname=self.posText[int(nbRef)-1].text()
        for i in range (0,1):
            self.MOT[i].setRefName(nbRef,str(vname))

    def savRef (self) :
        '''
        save reference  value
        '''
        sender=QtCore.QObject.sender(self)
        nbRef=sender.objectName()[0] # nom du button ABSref1
        
        vref=int(self.absRef[int(nbRef)-1].value())*self.unitChange
        self.MOT[0].setRefValue(nbRef,vref) # on sauvegarde en step 
           
    def ShootAct(self):
        try: 
            self.tir.TirAct()  
        except: pass
    
    def closeEvent(self, event):
        """ 
        When closing the window
        """
        self.fini()
        time.sleep(0.1)
        event.accept()
        
    def fini(self): 
        '''
        at the end we close all the thread 
        '''
        self.thread.stopThread()
        self.isWinOpen=False
        time.sleep(0.1)    
        moteurRSAIFDB.closeConnection()

        if self.scanWidget.isWinOpen==True:
            self.scanWidget.close()
        
class REF1M(QWidget):
    
    def __init__(self,num=0, parent=None):
        super(REF1M, self).__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.wid=QWidget()
        self.id=num
        self.vboxPos=QVBoxLayout()
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.icon=str(p.parent) + sepa + 'icons' +sepa
        self.posText=QLineEdit('ref')
        self.posText.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.posText.setStyleSheet("font: bold 15pt")
        self.posText.setObjectName('%s'%self.id)
#        self.posText.setMaximumWidth(80)
        self.vboxPos.addWidget(self.posText)
        self.iconTake=self.icon+"disquette.PNG"
        self.iconTake=pathlib.Path(self.iconTake)
        self.iconTake=pathlib.PurePosixPath(self.iconTake)
        self.take=QToolButton()
        self.take.setObjectName('%s'%self.id)
        self.take.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconTake,self.iconTake))
        self.take.setMaximumWidth(30)
        self.take.setMinimumWidth(30)
        self.take.setMinimumHeight(30)
        self.take.setMaximumHeight(30)
        self.takeLayout=QHBoxLayout()
        self.takeLayout.addWidget(self.take)

        self.iconGo=self.icon+"go.PNG"
        self.iconGo=pathlib.Path(self.iconGo)
        self.iconGo=pathlib.PurePosixPath(self.iconGo)
        self.Pos=QToolButton()
        self.Pos.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconGo,self.iconGo))
        self.Pos.setMinimumHeight(30)
        self.Pos.setMaximumHeight(30)
        self.Pos.setMinimumWidth(30)
        self.Pos.setMaximumWidth(30)
        self.PosLayout=QHBoxLayout()
        self.PosLayout.addWidget(self.Pos)
        self.Pos.setObjectName('%s'%self.id)
        #○self.Pos.setStyleSheet("background-color: rgb(85, 170, 255)")
        Labelref=QLabel('Pos :')
        Labelref.setMaximumWidth(30)
        Labelref.setStyleSheet("font: 9pt" )
        self.ABSref=QDoubleSpinBox()
        self.ABSref.setMaximum(500000000)
        self.ABSref.setMinimum(-500000000)
        self.ABSref.setValue(123456)
        self.ABSref.setMaximumWidth(80)
        self.ABSref.setObjectName('%s'%self.id)
        self.ABSref.setStyleSheet("font: 9pt" )
        
        grid_layoutPos = QGridLayout()
        grid_layoutPos.setVerticalSpacing(5)
        grid_layoutPos.setHorizontalSpacing(10)
        grid_layoutPos.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        grid_layoutPos.addLayout(self.takeLayout,0,0)
        grid_layoutPos.addLayout(self.PosLayout,0,1)
        grid_layoutPos.addWidget(Labelref,1,0)
        grid_layoutPos.addWidget(self.ABSref,1,1)
        
        self.vboxPos.addLayout(grid_layoutPos)
        self.wid.setStyleSheet("background-color: rgb(60, 77, 87);border-radius:10px")
        self.wid.setLayout(self.vboxPos)
        
        mainVert=QVBoxLayout()
        mainVert.addWidget(self.wid)
        mainVert.setContentsMargins(0,0,0,0)
        self.setLayout(mainVert)


class PositionThread(QtCore.QThread):
    '''
    Secon thread  to display the position
    '''
    import time 
    POS=QtCore.pyqtSignal(object) # signal of the second thread to main thread  to display motors position
    ETAT=QtCore.pyqtSignal(str)
    def __init__(self,parent=None,mot='',):
        super(PositionThread,self).__init__(parent)
        self.MOT=mot
        
        self.parent=parent
        
        self.stop=False

    def run(self):
        while True:
            if self.stop==True:
                break
            else:
                
                Posi=(self.MOT.position())
                time.sleep(0.1)
                
                try :
                    etat = self.MOT.etatMotor()
                    time.sleep(0.1)
                    self.POS.emit([Posi,etat])
                    time.sleep(0.1)
                except:
                    print('error emit')
                  
                
                
    def ThreadINIT(self):
        self.stop=False   
                        
    def stopThread(self):
        self.stop=True
        time.sleep(0.1)
        self.terminate()
        

if __name__ == '__main__':
    
    appli = QApplication(sys.argv)
           
    mot5 = ONEMOTORGUI(IpAdress="10.0.6.30", NoMotor=1, showRef=False, unit=1,jogValue=100)
    mot5.show()
    mot5.startThread2()
    appli.exec_()