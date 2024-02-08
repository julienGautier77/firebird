# -*- coding: utf-8 -*-
"""
Created on 15 December 2023

@author: Julien Gautier (LOA)
last modified 
"""
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget,QMessageBox,QLineEdit,QToolButton
from PyQt6.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QDoubleSpinBox,QCheckBox
from PyQt6.QtWidgets import QComboBox,QLabel
from PyQt6.QtGui import QIcon
import sys,time,os
import qdarkstyle
import pathlib
import __init__
import TirGui
import moteurRSAIFDB
__version__=__init__.__version__
__author__ = __init__. __author__ 

from oneMotorGuiFB import ONEMOTORGUI

class THREEMOTORGUI(QWidget) :
    """
    User interface Motor class : 
    MOTOGUI(str(mot1), str(motorTypeName),str(mot2), str(motorTypeName), nomWin,nomTilt,nomFoc,showRef,unit,unitFoc )
    mot0= lat  'name of the motor ' (child group of the ini file)
    mot1 =vert
    mot 2 =foc
    nonWin= windows name
    nonTilt =windows tilt name
    nomFoc= windows Focus name
    showRef True or False to show refWidget 
    unit= initial Unit of the two fisrt motors :
        0=sterp
        1=Micros
        2=mm
        3=ps
        4=degres
        unitFoc= unit of the third motors
        
    motorTypeName= Controler name  : 'RSAI' or 'A2V' or 'NewFocus' or 'SmartAct' or 'Newport' , Servo, Arduino
    
    fichier de config des moteurs : 'configMoteurRSAI.ini' 'configMoteurA2V.ini' 'configMoteurNewFocus.ini' 'configMoteurSmartAct.ini'
    
    
    """



    def __init__(self, IPLat,NoMotorLat,IPVert,NoMotorVert,IPFoc,NoMotorFoc,nomWin='',nomTilt='',nomFoc='',showRef=False,unit=1,unitFoc=1,jogValue=100,jogValueFoc=100,parent=None):
        
        super(THREEMOTORGUI, self).__init__()
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.etat='ok'
        self.icon=str(p.parent) + sepa + 'icons' +sepa
        self.nomWin=nomWin
        self.iconPlay=self.icon+"playGreen.PNG"
        self.iconPlay=pathlib.Path(self.iconPlay)
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)

        self.iconMoins=self.icon+"moinsBleu.PNG"
        self.iconMoins=pathlib.Path(self.iconMoins)
        self.iconMoins=pathlib.PurePosixPath(self.iconMoins)

        self.iconPlus=self.icon+"plusBleu.PNG"
        self.iconPlus=pathlib.Path(self.iconPlus)
        self.iconPlus=pathlib.PurePosixPath(self.iconPlus)

        self.iconStop=self.icon+"close.PNG"
        self.iconStop=pathlib.Path(self.iconStop)
        self.iconStop=pathlib.PurePosixPath(self.iconStop)

        self.iconUpdate = self.icon +"recycle.PNG"
        self.iconUpdate = pathlib.Path(self.iconUpdate)
        self.iconUpdate = pathlib.PurePosixPath(self.iconUpdate) 

        self.iconFlecheHaut=self.icon+"flechehaut.PNG"
        self.iconFlecheHaut=pathlib.Path(self.iconFlecheHaut)
        self.iconFlecheHaut=pathlib.PurePosixPath(self.iconFlecheHaut)

        self.iconFlecheBas=self.icon+"flechebas.PNG"
        self.iconFlecheBas=pathlib.Path(self.iconFlecheBas)
        self.iconFlecheBas=pathlib.PurePosixPath(self.iconFlecheBas)

        self.iconFlecheDroite=self.icon+"flechedroite.PNG"
        self.iconFlecheDroite=pathlib.Path(self.iconFlecheDroite)
        self.iconFlecheDroite=pathlib.PurePosixPath(self.iconFlecheDroite)

        self.iconFlecheGauche=self.icon+"flechegauche.PNG"
        self.iconFlecheGauche=pathlib.Path(self.iconFlecheGauche)
        self.iconFlecheGauche=pathlib.PurePosixPath(self.iconFlecheGauche)


        self.nomTilt=nomTilt
        self.etatLat='ok'
        self.etatVert='ok'
        self.etatFoc='ok'
        self.configPath=str(p.parent)+sepa+"fichiersConfig"+sepa
        self.isWinOpen=False
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.refShowId=showRef
        self.indexUnit=unit
        self.indexUnitFoc=unitFoc
        self.jogValue=jogValue
        self.jogValueFoc=jogValueFoc

        self.LatWidget=ONEMOTORGUI(IPLat,NoMotorLat,nomWin='Control One Motor : ',showRef=False,unit=1)
        self.VertWidget=ONEMOTORGUI(IPVert,NoMotorVert,nomWin='Control One Motor : ',showRef=False,unit=1)
        self.FocWidget=ONEMOTORGUI(IPFoc,NoMotorFoc,nomWin='Control One Motor : ',showRef=False,unit=1)
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.version=__version__
        self.tir=TirGui.TIRGUI()
        # self.setWindowOpacity(0.5)
        self.MOT=[0,0,0]
        self.MOT[0]=moteurRSAIFDB.MOTORRSAI(IPLat,NoMotorLat)
        self.MOT[1]=moteurRSAIFDB.MOTORRSAI(IPVert,NoMotorVert)
        self.MOT[2]=moteurRSAIFDB.MOTORRSAI(IPVert,NoMotorFoc)

        self.stepmotor=[0,0,0]
        self.butePos=[0,0,0]
        self.buteNeg=[0,0,0]
        self.name=[0,0,0]
        
        for zzi in range(0,3):
            self.stepmotor[zzi] = float(1/(self.MOT[zzi].getStepValue())) # list of stepmotor values for unit conversion
            self.butePos[zzi] = float(self.MOT[zzi].getButLogPlusValue()) # list 
            self.buteNeg[zzi] = float(self.MOT[zzi].getButLogMoinsValue())
            self.name[zzi] = str(self.MOT[0].getName())
        
        self.setWindowTitle(nomWin+'                     V.'+str(self.version))#+' : '+ self.name[0])
        
        self.threadLat=PositionThread(self,mot=self.MOT[0]) # thread for displaying position Lat
        self.threadLat.POS.connect(self.PositionLat)
        
        self.threadVert=PositionThread(self,mot=self.MOT[1]) # thread for displaying  position Vert
        self.threadVert.POS.connect(self.PositionVert)
        
        
        self.threadFoc=PositionThread(self,mot=self.MOT[2]) # thread for displaying  position Foc
        self.threadFoc.POS.connect(self.PositionFoc)
        
        
        ## initialisation of the jog value 
        if self.indexUnitFoc == 0: #  step
            self.unitChangeFoc = 1
            self.unitNameFoc = 'step'
            
        if self.indexUnitFoc == 1: # micron
            self.unitChangeFoc = float((1*self.stepmotor[2])) 
            self.unitNameFoc = 'um'
        if self.indexUnitFoc == 2: #  mm 
            self.unitChangeFoc = float((1000*self.stepmotor[2]))
            self.unitNameFoc = 'mm'
        if self.indexUnitFoc == 3: #  ps  double passage : 1 microns=6fs
            self.unitChangeFoc = float(1*self.stepmotor[2]/0.0066666666) 
            self.unitNameFoc = 'ps'
        if self.indexUnitFoc == 4: #  en degres
            self.unitChangeFoc=1 *self.stepmotor[2]
            self.unitNameFoc = '°'    
        
        if self.indexUnit == 0: # step
            self.unitChangeLat = 1
            self.unitChangeVert = 1
            self.unitNameTrans = 'step'
        if self.indexUnit == 1: # micron
            self.unitChangeLat = float((1*self.stepmotor[0]))  
            self.unitChangeVert = float((1*self.stepmotor[1]))  
            self.unitNameTrans = 'um'
        if self.indexUnit == 2: 
            self.unitChangeLat = float((1000*self.stepmotor[0]))
            self.unitChangeVert = float((1000*self.stepmotor[1]))
            self.unitNameTrans = 'mm'
        if self.indexUnit == 3: #  ps  en compte le double passage : 1 microns=6fs
            self.unitChangeLat = float(1*self.stepmotor[0]/0.0066666666)  
            self.unitChangeVert = float(1*self.stepmotor[1]/0.0066666666)  
            self.unitNameTrans = 'ps'
        if self.unitChangeLat == 0:
            self.unitChangeLat = 1 # if / par 0
        if self.unitChangeVert == 0:
            self.unitChangeVert = 1 #if / 0
        
        self.setup()
        self.update()
        self.unitFoc()
        self.unitTrans()
        self.jogStep.setValue(self.jogValue)
        self.jogStep_2.setValue(self.jogValueFoc)
        self.actionButton()

    def update(self):    
        # update from DB
        # to avoid to access to the database 
        for zzi in range(0,2):
            print('update')
            self.MOT[zzi].update()
            time.sleep(0.1)
            self.stepmotor[zzi] = float(1/(self.MOT[zzi].getStepValue())) # list of stepmotor values for unit conversion
            self.butePos[zzi] = float(self.MOT[zzi].getButLogPlusValue()) # list 
            self.buteNeg[zzi] = float(self.MOT[zzi].getButLogMoinsValue())
            self.name[zzi] = str(self.MOT[zzi].getName())
            
        self.setWindowTitle(self.nomWin)
        
        self.refValueLat = self.MOT[0].refValue
        self.refNameLat = self.MOT[0].refName
        self.refValueVert = self.MOT[1].refValue
        self.refNameVert = self.MOT[1].refName
        self.refValueFoc = self.MOT[2].refValue
        self.refNameFoc = self.MOT[0].refName

        # update ref Name (ref name = ref La) and position ref value
        iii = 0
        for saveNameButton in self.posText: # reference name
            saveNameButton.textChanged.connect(self.savName)
            saveNameButton.setText(self.refNameLat[iii]) # print  ref name
            iii+=1        
        eee = 0  
        for absButton in self.absLatRef: 
            absButton.setValue(float(self.refValueLat[eee]/self.unitChangeLat)) # save reference lat  value
            eee+=1
        eee = 0     
        for absButton in self.absVertRef: 
            absButton.setValue(float(self.refValueVert[eee]/self.unitChangeVert)) #save reference vert value 
        eee = 0    
        for absButton in self.absFocRef: 
            absButton.setValue(float(self.refValueFoc[eee]/self.unitChangeFoc)) # save reference foc value
            eee+=1

    def updateDB(self):
        #  update ref name and ref position to the Data base 
        for m in range (0,2):
            i=1
            for ref in self.refNameLat : 
                self.MOT[m].setRefName(i,ref)
                i+=1
            #♦self.MOT[m].update()
        
        for ref in self.refValueLat : 
            self.MOT[0].setRefValue(i,ref/self.stepmotor[0])
            
        for ref in self.refValueVert : 
            self.MOT[1].setRefValue(i,ref/self.stepmotor[1])

        for ref in self.refValueFoc : 
            self.MOT[2].setRefValue(i,ref/self.stepmotor[2])


    def startThread2(self):
        self.threadVert.ThreadINIT()
        self.threadVert.start()
        time.sleep(0.12)
        self.threadFoc.ThreadINIT()
        self.threadFoc.start()
        time.sleep(0.1)
        self.threadLat.ThreadINIT()
        self.threadLat.start()
        
    def setup(self):

        vbox1 = QVBoxLayout() 
        hboxTitre = QHBoxLayout()
        self.nomTilt = QLabel(self.nomTilt)
        self.nomTilt.setStyleSheet("font: bold 20pt;color:yellow")
        hboxTitre.addWidget(self.nomTilt)
        
        self.unitTransBouton=QComboBox()
        self.unitTransBouton.setMaximumWidth(100)
        self.unitTransBouton.setMinimumWidth(100)
        self.unitTransBouton.setStyleSheet("font: bold 12pt")
        self.unitTransBouton.addItem('Step')
        self.unitTransBouton.addItem('um')
        self.unitTransBouton.addItem('mm')
        self.unitTransBouton.addItem('ps')
        self.unitTransBouton.setCurrentIndex(self.indexUnit)
        
        
        hboxTitre.addWidget(self.unitTransBouton)
        hboxTitre.addStretch(1)
        self.butNegButt = QCheckBox('But Neg',self)
        hboxTitre.addWidget(self.butNegButt)
       
        self.butPosButt = QCheckBox('But Pos',self)
        hboxTitre.addWidget(self.butPosButt)
        vbox1.addLayout(hboxTitre)
        
        hShoot=QHBoxLayout()
        self.shootCibleButton=QPushButton('Shot')
        self.shootCibleButton.setStyleSheet("font: 12pt;background-color: red")
        self.shootCibleButton.setMaximumWidth(100)
        self.shootCibleButton.setMinimumWidth(100)
        hShoot.addWidget(self.shootCibleButton)
        self.updateButton = QToolButton()
        self.updateButton.setToolTip( "update from DB")
        self.updateButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconUpdate,self.iconUpdate))
        hShoot.addWidget(self.updateButton)
        vbox1.addLayout(hShoot)
        
        hLatBox = QHBoxLayout()
        hbox1 = QHBoxLayout()
        
        self.posLat = QPushButton('Lateral:')
        self.posLat.setStyleSheet("font: 12pt")
        self.posLat.setMaximumHeight(30)
        self.position_Lat = QLabel('12345667')
        self.position_Lat.setStyleSheet("font: bold 25pt" )
        self.position_Lat.setMaximumHeight(30)
        self.enPosition_Lat=QLineEdit('?')
        self.enPosition_Lat.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.enPosition_Lat.setMaximumWidth(70)
        self.enPosition_Lat.setStyleSheet("font: bold 10pt")
        self.zeroButtonLat = QPushButton('Zero')
        self.zeroButtonLat.setMaximumWidth(30)
        self.zeroButtonLat.setMinimumWidth(30)
        hLatBox.addWidget(self.posLat)
        hLatBox.addWidget(self.position_Lat)
        hLatBox.addWidget(self.enPosition_Lat)
        hLatBox.addWidget(self.zeroButtonLat)
        hLatBox.addSpacing(25)
        
        hVertBox = QHBoxLayout()
        self.posVert = QPushButton('Vertical:')
        self.posVert.setStyleSheet("font: 12pt")
        self.posVert.setMaximumHeight(30)
        self.position_Vert = QLabel('1234556')
        self.position_Vert.setStyleSheet("font: bold 25pt" )
        self.position_Vert.setMaximumHeight(30)
        self.enPosition_Vert = QLineEdit('?')
        self.enPosition_Vert.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.enPosition_Vert.setMaximumWidth(70)
        self.enPosition_Vert.setStyleSheet("font: bold 10pt")
        self.zeroButtonVert = QPushButton('Zero')
        self.zeroButtonVert.setMaximumWidth(30)
        self.zeroButtonVert.setMinimumWidth(30)
        
        hVertBox.addWidget(self.posVert)
        hVertBox.addWidget(self.position_Vert)
        hVertBox.addWidget(self.enPosition_Vert)
        hVertBox.addWidget(self.zeroButtonVert)
        hVertBox.addSpacing(25)
        
        vboxLatVert = QVBoxLayout() 
        vboxLatVert.addLayout(hLatBox)
        vboxLatVert.addLayout(hVertBox)
        
        hbox1.addLayout(vboxLatVert)
        
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(0)
        grid_layout.setHorizontalSpacing(10)
        self.haut = QToolButton()
        self.haut.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconFlecheHaut,self.iconFlecheHaut))
        
        self.haut.setMaximumHeight(70)
        self.haut.setMinimumWidth(70)
        self.haut.setMaximumWidth(70)
        self.haut.setMinimumHeight(70)
        
        self.bas = QToolButton()
        self.bas.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconFlecheBas,self.iconFlecheBas))
        self.bas.setMaximumHeight(70)
        self.bas.setMinimumWidth(70)
        self.bas.setMaximumWidth(70)
        self.bas.setMinimumHeight(70)
        
        self.gauche = QToolButton()
        self.gauche.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconFlecheGauche,self.iconFlecheGauche))
        self.gauche.setMaximumHeight(70)
        self.gauche.setMinimumWidth(70)
        self.gauche.setMaximumWidth(70)
        self.gauche.setMinimumHeight(70)
        self.droite = QToolButton()

        self.droite.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconFlecheDroite,self.iconFlecheDroite))
        self.droite.setMaximumHeight(70)
        self.droite.setMinimumWidth(70)
        self.droite.setMaximumWidth(70)
        self.droite.setMinimumHeight(70)
        
        
        self.jogStep = QDoubleSpinBox()
        self.jogStep.setMaximum(1000)
        self.jogStep.setStyleSheet("font: bold 12pt")
        self.jogStep.setValue(100)
        self.jogStep.setMaximumWidth(120)
        self.jogStep.setValue(55)
        self.unitChangeLat = 1
    
        center = QHBoxLayout()
        center.addWidget(self.jogStep)
        self.hautLayout = QHBoxLayout()
        self.hautLayout.addWidget(self.haut)
        self.basLayout = QHBoxLayout()
        self.basLayout.addWidget(self.bas)
        grid_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        grid_layout.addLayout(self.hautLayout, 0, 1)
        grid_layout.addLayout(self.basLayout,2,1)
        grid_layout.addWidget(self.gauche, 1, 0)
        grid_layout.addWidget(self.droite, 1, 2)
        grid_layout.addLayout(center,1,1)

        hbox1.addLayout(grid_layout)
        vbox1.addLayout(hbox1)     
        vbox1.addSpacing(10)
        
        hboxFoc = QHBoxLayout()
        self.posFoc = QPushButton('Foc:')
        self.posFoc.setMaximumHeight(30)
        self.posFoc.setStyleSheet("font: bold 12pt")
        self.position_Foc = QLabel('1234567')
        self.position_Foc.setStyleSheet("font: bold 25pt" )
        self.position_Foc.setMaximumHeight(30)
        self.unitFocBouton = QComboBox()
        self.unitFocBouton.addItem('Step')
        self.unitFocBouton.addItem('um')
        self.unitFocBouton.addItem('mm')
        self.unitFocBouton.addItem('ps')
        self.unitFocBouton.setMinimumWidth(80)
        self.unitFocBouton.setStyleSheet("font: bold 12pt")
        self.unitFocBouton.setCurrentIndex(self.indexUnitFoc)
        
        self.enPosition_Foc = QLineEdit()
        self.enPosition_Foc.setMaximumWidth(60)
        self.enPosition_Foc.setStyleSheet("font: bold 10pt")
        self.enPosition_Foc.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.zeroButtonFoc = QPushButton('Zero')
        self.zeroButtonFoc.setMaximumWidth(30)
        self.zeroButtonFoc.setMinimumWidth(30)
        
        hboxFoc.addWidget(self.posFoc)
        
        hboxFoc.addWidget(self.position_Foc)
        hboxFoc.addWidget(self.unitFocBouton)
        hboxFoc.addWidget(self.enPosition_Foc)
        hboxFoc.addWidget(self.zeroButtonFoc)
        hboxFoc.addSpacing(25)
        
        self.moins = QToolButton()
        self.moins.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconMoins,self.iconMoins))
        self.moins.setMaximumWidth(70)
        self.moins.setMinimumHeight(70)
        hboxFoc.addWidget(self.moins)
        
        self.jogStep_2 = QDoubleSpinBox()
        self.jogStep_2.setMaximum(10000)
        self.jogStep_2.setStyleSheet("font: bold 12pt")
        self.jogStep_2.setValue(self.jogValueFoc)
        
        hboxFoc.addWidget(self.jogStep_2)
         
        self.plus = QToolButton()
        self.plus.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: transparent ;border-color: gray;}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: gray}"%(self.iconPlus,self.iconPlus))
        
        self.plus.setMaximumWidth(70)
        self.plus.setMinimumHeight(70)
    
        hboxFoc.addWidget(self.plus)
        
        vbox1.addLayout(hboxFoc)
        vbox1.addSpacing(20)
        
        self.stopButton = QPushButton('STOP')
        self.stopButton.setStyleSheet("background-color: red")
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.stopButton)
        self.showRef = QPushButton('Show Ref')
        self.showRef.setMaximumWidth(70)
        hbox3.addWidget(self.showRef)
        vbox1.addLayout(hbox3)
        
        self.REF1 = REF3M(num=1)
        self.REF2 = REF3M(num=2)
        self.REF3 = REF3M(num=3)
        self.REF4 = REF3M(num=4)
        self.REF5 = REF3M(num=5)
        self.REF6 = REF3M(num=6)
        
        grid_layoutRef = QGridLayout()
        grid_layoutRef.setVerticalSpacing(4)
        grid_layoutRef.setHorizontalSpacing(4)
        grid_layoutRef.addWidget(self.REF1,0,0)
        grid_layoutRef.addWidget(self.REF2,0,1)
        grid_layoutRef.addWidget(self.REF3,0,2)
        grid_layoutRef.addWidget(self.REF4,1,0)
        grid_layoutRef.addWidget(self.REF5,1,1)
        grid_layoutRef.addWidget(self.REF6,1,2)
       
        self.widget6REF = QWidget()
        self.widget6REF.setLayout(grid_layoutRef)
        vbox1.addWidget(self.widget6REF)
        self.setLayout(vbox1)
        self.absLatRef = [self.REF1.ABSLatref,self.REF2.ABSLatref,self.REF3.ABSLatref,self.REF4.ABSLatref,self.REF5.ABSLatref,self.REF6.ABSLatref] 
        self.absVertRef = [self.REF1.ABSVertref,self.REF2.ABSVertref,self.REF3.ABSVertref,self.REF4.ABSVertref,self.REF5.ABSVertref,self.REF6.ABSVertref]
        self.absFocRef = [self.REF1.ABSFocref,self.REF2.ABSFocref,self.REF3.ABSFocref,self.REF4.ABSFocref,self.REF5.ABSFocref,self.REF6.ABSFocref] # pour memoriser les positions
        self.posText = [self.REF1.posText,self.REF2.posText,self.REF3.posText,self.REF4.posText,self.REF5.posText,self.REF6.posText]
        self.POS = [self.REF1.Pos,self.REF2.Pos,self.REF3.Pos,self.REF4.Pos,self.REF5.Pos,self.REF6.Pos]
        self.Take = [self.REF1.take,self.REF2.take,self.REF3.take,self.REF4.take,self.REF5.take,self.REF6.take]
        self.jogStep_2.setFocus()
        self.refShow()

    def actionButton(self):
        '''
           buttons action setup 
        '''
        self.unitFocBouton.currentIndexChanged.connect(self.unitFoc) # Foc unit change
        self.unitTransBouton.currentIndexChanged.connect(self.unitTrans) # Trans unit change
        
        self.haut.clicked.connect(self.hMove) # jog up
        self.haut.setAutoRepeat(False)
        self.bas.clicked.connect(self.bMove) # jog down
        self.bas.setAutoRepeat(False)
        self.gauche.clicked.connect(self.gMove)
        self.gauche.setAutoRepeat(False)
        self.droite.clicked.connect(self.dMove)
        self.droite.setAutoRepeat(False)
        
        self.plus.clicked.connect(self.pMove) # jog + foc
        self.plus.setAutoRepeat(False)
        self.moins.clicked.connect(self.mMove)# jog - fo
        self.moins.setAutoRepeat(False) 
                
        self.zeroButtonFoc.clicked.connect(self.ZeroFoc) # reset display to 0
        self.zeroButtonLat.clicked.connect(self.ZeroLat)
        self.zeroButtonVert.clicked.connect(self.ZeroVert)
        
        #self.refZeroButton.clicked.connect(self.RefMark) # todo
        
        self.stopButton.clicked.connect(self.StopMot)
        self.showRef.clicked.connect(self.refShow)
        
        self.posVert.clicked.connect(lambda:self.open_widget(self.VertWidget))
        self.posLat.clicked.connect(lambda:self.open_widget(self.LatWidget))
        self.posFoc.clicked.connect(lambda:self.open_widget(self.FocWidget))
        self.shootCibleButton.clicked.connect(self.ShootAct)
        
        iii = 0
        for saveNameButton in self.posText: # reference name
            saveNameButton.textChanged.connect(self.savName)
            saveNameButton.setText(self.refNameLat[iii]) # print  ref name
            iii+=1        
        for posButton in self.POS: # button GO
            posButton.clicked.connect(self.ref)    # go to reference value
        eee = 0   
        for absButton in self.absLatRef: 
            absButton.setValue(float(self.refValueLat[eee]/self.unitChangeLat)) # save reference lat  value
            absButton.editingFinished.connect(self.savRefLat) # sauv value
            eee+=1
        eee = 0     
        for absButton in self.absVertRef: 
            absButton.setValue(float(self.refValueVert[eee]/self.unitChangeVert)) #save reference vert value 
            absButton.editingFinished.connect(self.savRefVert) # save  value
            eee+=1
        eee = 0     
        for absButton in self.absFocRef: 
            absButton.setValue(float(self.refValueFoc[eee]/self.unitChangeFoc)) # save reference foc value
            absButton.editingFinished.connect(self.savRefFoc) #
            eee+=1
            
        for takeButton in self.Take:
            takeButton.clicked.connect(self.take)
             # take the value 
        
        self.updateButton.clicked.connect(self.update)

    def open_widget(self,fene):
        
        """ open new widget 
        """
        if fene.isWinOpen==False:
            #New widget"
            fene.show()
            fene.startThread2()
            fene.isWinOpen=True
        else:
            #fene.activateWindow()
            fene.raise_()
            fene.showNormal()  
            
    def refShow(self):
        
        if self.refShowId==True:
            #print(self.geometry())
            #self.resize(368, 345)
            self.widget6REF.show()
            self.refShowId=False
            self.showRef.setText('Hide Ref')
            self.setFixedSize(750,800)
            
        else:
            #print(self.geometry())
            self.widget6REF.hide()
            self.refShowId=True

            self.showRef.setText('Show Ref')
            self.setFixedSize(750,450)
            #self.updateGeometry()      
    
    def pMove(self):
        '''
        action jog + foc 
        '''
        a=float(self.jogStep_2.value())
        a=float(a*self.unitChangeFoc)
        b=self.MOT[2].position()
        a=float(self.jogStep_2.value())
        a=float(a*self.unitChangeFoc)
        b=self.MOT[2].position()
        
        if b+a>self.butePos[2] :
            print( "STOP : Positive switch")
            self.MOT[2].stopMotor()
            self.butPosButt.setChecked(True)
        else :
            self.MOT[2].rmove(a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)

    def mMove(self): 
        '''
        action jog - foc
        '''
        a=float(self.jogStep_2.value())
        a=float(a*self.unitChangeFoc)
        b=self.MOT[2].position()
        if b-a<self.buteNeg[2] :
            print( "STOP : Negative switch")
            self.MOT[2].stopMotor()
            self.butNegButt.setChecked(True)
        else :
            self.MOT[2].rmove(-a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)

    def gMove(self):
        '''
        action button left -
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChangeLat)
        b=self.MOT[0].position()
       
        if b+a>self.butePos[0] :
            print( "STOP : Positive switch")
            self.MOT[0].stopMotor()
            self.butPosButt.setChecked(True)
        else :
            self.MOT[0].rmove(-a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)
            
    def dMove(self):
        '''
        action bouton right +
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChangeLat)
        b=self.MOT[0].position()
        if b-a<self.buteNeg[0] :
            print( "STOP : Negative switch")
            self.MOT[0].stopMotor()
            self.butNegButt.setChecked(True)
        else :
            self.MOT[0].rmove(a)
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)
        
    def hMove(self): 
        '''
        action button up +
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChangeVert)
        b=self.MOT[1].position()
        if b+a>self.butePos[1] :
            print( "STOP : Positive switch")
            self.MOT[1].stopMotor()
            self.butPosButt.setChecked(True)
            
        else :
            self.MOT[1].rmove(a)           
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False) 
        
    def bMove(self):
        '''
        action button up -
        '''
        a=float(self.jogStep.value())
        a=float(a*self.unitChangeVert)
        b=self.MOT[1].position()
        if b-a<self.buteNeg[1] :
            self.MOT[1].stopMotor()
            print( "STOP : Negative switch")
            self.butNegButt.setChecked(True)
        else :
            self.MOT[1].rmove(-a)   
            self.butNegButt.setChecked(False)
            self.butPosButt.setChecked(False)   
        
    def ZeroLat(self): #  zero 
        self.MOT[0].setzero()
    def ZeroVert(self): #  zero 
        self.MOT[1].setzero()
    def ZeroFoc(self): #  zero 
        self.MOT[2].setzero()

    def RefMark(self): # 
        """
            todo ....
        """
        #self.motorType.refMark(self.motor)
   
    def unitFoc(self):
        '''
        unit change mot foc
        '''
        self.indexUnitFoc=self.unitFocBouton.currentIndex()
        valueJog_2=self.jogStep_2.value()*self.unitChangeFoc
        if self.indexUnitFoc==0: #  step
            self.unitChangeFoc=1
            self.unitNameFoc='step'
        if self.indexUnitFoc==1: # micron
            self.unitChangeFoc=float((1*self.stepmotor[2]))  
            self.unitNameFoc='um'
        if self.indexUnitFoc==2: #  mm 
            self.unitChangeFoc=float((1000*self.stepmotor[2]))
            self.unitNameFoc='mm'
        if self.indexUnitFoc==3: #  ps  double passage : 1 microns=6fs
            self.unitChangeFoc=float(1*self.stepmotor[2]/0.0066666666)    
            self.unitNameFoc='ps'
        if self.unitChangeFoc==0:
            self.unitChangeFoc=1 #avoid 0 
        
        self.jogStep_2.setValue(valueJog_2/self.unitChangeFoc)
        self.jogStep_2.setSuffix(" %s" % self.unitNameFoc)
        eee = 0   
        for absButton in self.absFocRef: 
            nbRef = eee
            absButton.setValue(float(self.refValueFoc[nbRef])/self.unitChangeFoc) # save reference foc value
            absButton.setSuffix(" %s" % self.unitNameFoc)
            eee+=1
        
    def unitTrans(self):
        '''
         unit change mot foc
        '''
        valueJog = self.jogStep.value()*self.unitChangeLat
        self.indexUnit = self.unitTransBouton.currentIndex()
        if self.indexUnit == 0: # step
            self.unitChangeLat = 1
            self.unitChangeVert = 1
            self.unitNameTrans = 'step'
        if self.indexUnit == 1: # micron
            self.unitChangeLat = float((1*self.stepmotor[0]))  
            self.unitChangeVert = float((1*self.stepmotor[1]))  
            self.unitNameTrans = 'um'
        if self.indexUnit == 2: 
            self.unitChangeLat = float((1000*self.stepmotor[0]))
            self.unitChangeVert = float((1000*self.stepmotor[1]))
            self.unitNameTrans = 'mm'
        if self.indexUnit == 3: #  ps  en compte le double passage : 1 microns=6fs
            self.unitChangeLat = float(1*self.stepmotor[0]/0.0066666666)  
            self.unitChangeVert = float(1*self.stepmotor[1]/0.0066666666)  
            self.unitNameTrans = 'ps'
        if self.unitChangeLat == 0:
            self.unitChangeLat = 1 # if / par 0
        if self.unitChangeVert == 0:
            self.unitChangeVert = 1 #if / 0
        
        self.jogStep.setValue(valueJog/self.unitChangeLat)
        self.jogStep.setSuffix(" %s" % self.unitNameTrans)
        
        eee = 0  
        for absButton in self.absLatRef: 
            nbRef = eee
            absButton.setValue(float(self.refValueLat[nbRef])/self.unitChangeLat) # save reference lat  value
            absButton.setSuffix(" %s" % self.unitNameTrans)
            eee+= 1
        eee = 0    
        for absButton in self.absVertRef: 
            nbRef = eee
            absButton.setValue(float(self.refValueVert[nbRef])/self.unitChangeVert) #save reference vert value 
            absButton.setSuffix(" %s" % self.unitNameTrans)
            eee+= 1
        
    def StopMot(self):
        '''
        stop all motors
        '''
        for zzi in range(0,3):
            self.MOT[zzi].stopMotor()
            
    def EtatLat(self,etat):
        self.etatLat = etat

    def EtatVert(self,etat):
#        print(etat)
        self.etatVert=etat
    def EtatFoc(self,etat):
#        print(etat)
        self.etatFoc=etat    
        
    def PositionLat(self,Posi):
        ''' 
        Position Lat  display with the second thread
        '''
        Pos = Posi[0]
        self.etatLat = str(Posi[1])
        a = float(Pos)
        b = a # value in step
        a = a/self.unitChangeLat # value with unit changed
        if self.etatLat=='FDC-':
            self.enPosition_Lat.setText('FDC -')
            self.enPosition_Lat.setStyleSheet('font: bold 12pt;color:red')
            
        elif self.etatLat=='FDC+':
            self.enPosition_Lat.setText('FDC +')
            self.enPosition_Lat.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatLat=='Power off' :
            self.enPosition_Lat.setText('Power Off')
            self.enPosition_Lat.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatLat=='mvt' :
             self.enPosition_Lat.setText('Mvt')
             self.enPosition_Lat.setStyleSheet('font: bold 12pt;color:white')
          
        self.position_Lat.setText(str(round(a,2))) 
        self.position_Lat.setStyleSheet('font: bold 25pt;color:white')
            
        positionConnue_Lat=0 # 
        precis=5
        if (self.etatLat == 'ok' or self.etatLat == '?'):
            for nbRefInt in range(1,7):
                if positionConnue_Lat == 0 :
                    
                    if float(self.refValueLat[nbRefInt-1])-precis<b< float(self.refValueLat[nbRefInt-1])+precis:
                        self.enPosition_Lat.setText(str(self.refNameLat[nbRefInt-1]))
                        positionConnue_Lat=1

        if positionConnue_Lat == 0 and (self.etatLat == 'ok' or self.etatLat == '?'):
            self.enPosition_Lat.setText('' ) 
            
    def PositionVert(self,Posi): 
        ''' 
        Position Vert  displayed with the second thread
        '''
        Pos=Posi[0]
        self.etatVert=str(Posi[1])
        a=float(Pos)
        b=a # value in step 
        a=a/self.unitChangeVert # value  with unit changed
        if self.etatVert=='FDC-':
            self.enposition_Vert.setText('FDC -')
            self.enposition_Vert.setStyleSheet('font: bold 12pt;color:red')
            
        elif self.etatVert=='FDC+':
            self.enPosition_Vert.setText('FDC +')
            self.position_Vert.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatVert=='Power off' :
            self.enPosition_Vert.setText('Power Off')
            self.enPosition_Vert.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatVert=='mvt' :
             self.enPosition_Vert.setText('Mvt')
             self.enPosition_Vert.setStyleSheet('font: bold 12pt;color:white')
           
        self.position_Vert.setText(str(round(a,2))) 
        self.position_Vert.setStyleSheet('font: bold 25pt;color:white')
            
        positionConnue_Vert=0 # 
        precis=5
        if (self.etatVert == 'ok' or self.etatVert == '?'):
            for nbRefInt in range(1,7):
                if positionConnue_Vert==0 :
                    if float(self.refValueVert[nbRefInt-1])-precis<b< float(self.refValueVert[nbRefInt-1])+precis:
                        self.enPosition_Vert.setText(str(self.refNameVert[nbRefInt-1]))
                        positionConnue_Vert = 1     
        if positionConnue_Vert == 0 and (self.etatVert == 'ok' or self.etatVert == '?'):
            self.enPosition_Vert.setText(' ' )   
            
    def PositionFoc(self,Posi): 
        ''' 
        Position Foc  displayed with the second thread
        '''
        Pos=Posi[0]
        self.etatFoc=str(Posi[1])
        a=float(Pos)
        b=a # value in step 
        a=a/self.unitChangeFoc # 
        
        if self.etatFoc=='FDC-':
            self.enposition_Foc.setText('FDC -')
            self.enposition_Foc.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatFoc=='FDC+':
            self.enPosition_Foc.setText('FDC +')
            self.enPosition_Foc.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatFoc=='Power off' :
            self.enPosition_Foc.setText('Power Off')
            self.enPosition_Foc.setStyleSheet('font: bold 12pt;color:red')
        elif self.etatFoc=='mvt' :
             self.enPosition_Foc.setText('Mvt')
             self.enPosition_Foc.setStyleSheet('font: bold 12pt;color:white')
           
        self.position_Foc.setText(str(round(a,2))) 
        self.position_Foc.setStyleSheet('font: bold 25pt;color:white')
        
        positionConnue_Foc=0
        precis=5
        if (self.etatFoc == 'ok' or self.etatFoc == '?'):
            for nbRefInt in range(1,7):
                if positionConnue_Foc == 0 :
                    if float(self.refValueFoc[nbRefInt-1]) - precis < b < float(self.refValueFoc[nbRefInt-1]) + precis: #self.MOT[0].getRefValue
                        self.enPosition_Foc.setText(str(self.refNameFoc[nbRefInt-1]))
                        positionConnue_Foc = 1   
        if positionConnue_Foc == 0 and (self.etatFoc == 'ok' or self.etatFoc == '?'):
            self.enPosition_Foc.setText(' ' )
   
    def take (self) : 
        ''' 
        take and save the reference
        '''
        sender=QtCore.QObject.sender(self) # take the name of  the button 
        # print ('sender name',sender)
        reply=QMessageBox.question(None,'Save Position ?',"Do you want to save this position ?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
               tposLat = self.MOT[0].position()
               nbRef = str(sender.objectName()[0])
              # print('ref',nbRef)
               self.refValueLat[int(nbRef)-1] = tposLat
               self.absLatRef[int(nbRef)-1].setValue(tposLat/self.unitChangeLat)
               print ("Position Lat saved" , self.refValueLat )
               tposVert=self.MOT[1].position()
               self.refValueVert[int(nbRef)-1] = tposVert
               self.absVertRef[int(nbRef)-1].setValue(tposVert/self.unitChangeVert)
               print ("Position Vert saved")
               tposFoc=self.MOT[2].position()
               print('tposFoc',tposFoc)
               self.refValueFoc[int(nbRef)-1] = tposFoc
               self.absFocRef[int(nbRef)-1].setValue(tposFoc/self.unitChangeFoc)
               print ("Position Foc saved")
#
    def ref(self):  
        '''
        Move the motor to the reference value in step : GO button
        Fait bouger le moteur a la valeur de reference en step : bouton Go 
        '''
        sender=QtCore.QObject.sender(self)
        reply=QMessageBox.question(None,'Go to this Position ?',"Do you want to GO to this position ?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            nbRef = int(sender.objectName()[0])
            vref=[]
            vref.append(int(self.refValueLat[nbRef-1]))
            vref.append(int(self.refValueVert[nbRef-1]))
            vref.append(int(self.refValueFoc[nbRef-1]))
            print('vref mov',vref)
            for i in range (0,3):
                # print(i)
                
                if vref[i] < self.buteNeg[i] :
                    print( "STOP : negative switch")
                    self.butNegButt.setChecked(True)
                    self.MOT[i].stopMotor()

                elif vref[i] > self.butePos[i] :
                    print( "STOP : positive switch")
                    self.butPosButt.setChecked(True)
                    self.MOT[i].stopMotor()
                else :
                    time.sleep(0.2)
                    self.MOT[i].move(vref[i])
                    time.sleep(1)
                    self.butNegButt.setChecked(False)
                    self.butPosButt.setChecked(False) 
#
    def savName(self) :
        '''
        Save reference name
        '''
        sender=QtCore.QObject.sender(self)
        #print('sender',sender.objectName())
        nbRef = int(sender.objectName()[0]) #PosTExt1
        vname = self.posText[int(nbRef)-1].text()
        
        self.refNameLat[nbRef-1] = str(vname)
        self.refNameVert[nbRef-1] = str(vname)
        self.refNameFoc[nbRef-1] = str(vname)

    def savRefLat (self) :
        '''
        save reference lat value
        '''
        sender = QtCore.QObject.sender(self)
        nbRefLat = sender.objectName()[0] # nom du button ABSref1
        #print('nbref=',nbRefLat)
        vrefLat = int(self.absLatRef[int(nbRefLat)-1].value()*self.unitChangeLat)
        self.refValueLat[int(nbRefLat)-1] = vrefLat # on sauvegarde en step dans la base donnee 
        print(self.refValueLat)
        
    def savRefVert (self) : 
        '''
        save reference Vert value
        '''
        sender=QtCore.QObject.sender(self)
        nbRefVert=sender.objectName()[0] 
        vrefVert=int(self.absVertRef[int(nbRefVert)-1].value()*self.unitChangeVert)
        self.refValueVert[int(nbRefVert)-1 ] = vrefVert # on sauvegarde en step dans la base donnee 
       
    def savRefFoc (self) :
        '''
        save reference Foc value
        '''
        sender=QtCore.QObject.sender(self)
        nbRefFoc=sender.objectName()[0] 
        vrefFoc=int(self.absFocRef[int(nbRefFoc)-1].value()*self.unitChangeFoc)
        self.refValueFoc[int(nbRefFoc)-1] = vrefFoc # on sauvegarde en step dans la base donnee 
        

    def ShootAct(self):
        self.tir.TirAct()
        
    def closeEvent(self, event):
        """ 
        When closing the window
        """
        self.fini()
        time.sleep(0.1)
        event.accept()
        
    def fini(self): 
        '''
        a the end we close all the thread 
        '''
        self.threadLat.stopThread()
        self.threadVert.stopThread()
        self.threadFoc.stopThread()
        self.isWinOpen=False
        time.sleep(0.1) 
         
        self.updateDB()   
        time.sleep(0.2) 
        
class REF3M(QWidget):
    
    def __init__(self,num=0, parent=None):
        QtCore.QObject.__init__(self)
        super(REF3M, self).__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.wid=QWidget()
        self.id=num
        self.vboxPos=QVBoxLayout()
        p = pathlib.Path(__file__)
        sepa=os.sep
        self.icon=str(p.parent) + sepa + 'icons' +sepa
        self.posText=QLineEdit('ref')
        self.posText.setStyleSheet("font: bold 15pt")
        self.posText.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.posText.setObjectName('%s'%self.id)
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
        
        LabeLatref=QLabel('Lat:')
        self.ABSLatref=QDoubleSpinBox()
        self.ABSLatref.setObjectName('%s'%self.id)
        self.ABSLatref.setMaximum(5000000000)
        self.ABSLatref.setMinimum(-5000000000)
        
        LabelVertref=QLabel('Vert:')
        self.ABSVertref=QDoubleSpinBox()
        self.ABSVertref.setObjectName('%s'%self.id)
        self.ABSVertref.setMaximum(5000000000)
        self.ABSVertref.setMinimum(-5000000000)
        
        LabelFocref=QLabel('Foc:')
        self.ABSFocref=QDoubleSpinBox()
        self.ABSFocref.setObjectName('%s'%self.id)
        self.ABSFocref.setMaximum(5000000000)
        self.ABSFocref.setMinimum(-5000000000)
        
        grid_layoutPos = QGridLayout()
        grid_layoutPos.setVerticalSpacing(5)
        grid_layoutPos.setHorizontalSpacing(10)
        grid_layoutPos.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        grid_layoutPos.addLayout(self.takeLayout,0,0)
        grid_layoutPos.addLayout(self.PosLayout,0,1)
        grid_layoutPos.addWidget(LabeLatref,1,0)
        grid_layoutPos.addWidget(self.ABSLatref,1,1)
        grid_layoutPos.addWidget(LabelVertref,2,0)
        grid_layoutPos.addWidget(self.ABSVertref,2,1)
        grid_layoutPos.addWidget(LabelFocref,3,0)
        grid_layoutPos.addWidget(self.ABSFocref,3,1)
        self.vboxPos.addLayout(grid_layoutPos)
#        self.vboxPos.setContentsMargins(-10,-10,-10,-10)
        self.wid.setStyleSheet("background-color: rgb(60, 77, 87)")
        self.wid.setLayout(self.vboxPos)
#        self.setContentsMargins(-10,-10,-10,-10)
        mainVert=QVBoxLayout()
        mainVert.addWidget(self.wid)
        mainVert.setContentsMargins(0,0,0,0)
        self.setLayout(mainVert)
       
        
class PositionThread(QtCore.QThread):
    '''
    Second thread  to display the position
    '''
    import time 
    POS=QtCore.pyqtSignal(object) # signal of the second thread to main thread  to display motors position
    ETAT=QtCore.pyqtSignal(str)

    def __init__(self,parent=None,mot=''):
        super(PositionThread,self).__init__(parent)
        self.MOT=mot
        self.parent=parent
        self.stop=False
        
    def run(self):
        while True:
            if self.stop==True:
                break
            else:
                Posi = (self.MOT.position())
                time.sleep(0.1)
                #try :
                etat = self.MOT.etatMotor()
                time.sleep(0.1)
                self.POS.emit([Posi,etat])
                time.sleep(0.1)
                #except: 
                    #print('error emit etat')  
                    
    def ThreadINIT(self):
        self.stop=False   
                        
    def stopThread(self):
        self.stop=True
        time.sleep(0.1)
        #self.terminate()
        



if __name__ =='__main__':
   
    appli=QApplication(sys.argv)
    mot5=motLat=THREEMOTORGUI(IPLat="10.0.6.30", NoMotorLat=1,IPVert="10.0.6.30", NoMotorVert=2,IPFoc="10.0.6.30", NoMotorFoc=3,nomWin='Camera Tache Focale',nomTilt='',nomFoc='Cam Foc')
    mot5.show()
    mot5.startThread2()
    appli.exec_()