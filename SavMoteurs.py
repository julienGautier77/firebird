


from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget,QMessageBox
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout,QPushButton,QGridLayout,QDoubleSpinBox
from PyQt6.QtWidgets import QComboBox,QLabel,QCheckBox
from PyQt6.QtGui import QIcon
import qdarkstyle,sys, time
import moteurRSAIFDB 


class MAINSAVE(QWidget):
    """  widget for printing position motors 
    """

    def __init__(self, parent=None):
        super(MAINSAVE, self).__init__(parent)
        self.isWinOpen = False
        self.parent = parent
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        self.setWindowIcon(QIcon('./icons/LOA.png'))
        self.setWindowTitle('Main save')
        self.listRack = moteurRSAIFDB.rEquipmentList()
        self.rackName = []

        for IP in self.listRack:
            self.rackName.append(moteurRSAIFDB.nameEquipment(IP))

        self.listMotor=[]
        for IPadress in self.listRack:
            self.listMotor.append(moteurRSAIFDB.listMotorName(IPadress))

        self.SETUP()
        self.actionButton()
        
    def SETUP(self):

        self.vbox = QVBoxLayout()
        hboxRack = QHBoxLayout()
        LabelRack = QLabel(' Rack NAME to save ')
        hboxRack.addWidget(LabelRack)
        self.box = []
        
        i = 0 
        for name in self.rackName: # create QCheckbox for each rack
            self.box.append(checkBox(name=str(name), ip=self.listRack[i], parent=self))
            hboxRack.addWidget(self.box[i])
            i+=1

        self.setLayout(self.vbox)
        self.vbox.addLayout(hboxRack)
        self.butt=QPushButton()
        self.vbox.addWidget(self.butt)

    def actionButton(self):
        for b in self.box:
            b.stateChanged.connect(self.clik)
        self.butt.clicked.connect(self.Action)
    
    def allPosition(self,IpAdress):
        listPosi = []
        IdEquipt = moteurRSAIFDB.rEquipmentIdNbr(IpAdress)
        for NoMotor in range (1,15):
            NoMod  = moteurRSAIFDB.getSlotNumber(NoMotor)
            NoAxis = moteurRSAIFDB.getAxisNumber(NoMotor)
            PkIdTbBoc = moteurRSAIFDB.readPkModBim2BOC(IdEquipt, NoMod, NoAxis, FlgReadWrite=1)
            pos = moteurRSAIFDB.getValueWhere1ConditionAND("TbBim2BOC_1Axis_R", "PosAxis", "PkId", str(PkIdTbBoc))
            listPosi.append(pos)
        return listPosi
    
    def clik(self):
        print('click')
        sender = QtCore.QObject.sender(self) 
        print(str(sender.objectName()))
    
    def Action(self):
        for b in self.box:
            if b.isChecked():
                print(self.allPosition(b.ip))

    def closeEvent(self, event):
        """ 
        When closing the window
        """
        moteurRSAIFDB.closeConnection()
        time.sleep(0.1)
        event.accept()    

class checkBox(QCheckBox):
    # homemade QCheckBox

    def __init__(self,name='test',ip='', parent=None):
        super(checkBox, self).__init__()
        self.parent = parent 
        self.ip = ip
        self.name = name
        self.setText(self.name+' ( '+ self.ip+ ')')
        self.setObjectName(self.ip)

if __name__=='__main__':
    appli=QApplication(sys.argv)
    s = MAINSAVE()
    s.show()
    appli.exec_()


