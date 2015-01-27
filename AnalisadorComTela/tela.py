#coding:utf-8

import time
import toPython as toPy
import imageIO as imgIO
import numpy

#----------

from PyQt4 import QtCore, QtGui
import sys

#----------

inicio = time.time()

#----------

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#----------

class Ui_Principal(object):
    def sCAParametros(self):
        if(len(self.lineEditAbrirImg.text()) > 0 and len(self.lineEditAbrirFunc.text()) > 0):

            self.codigo = toPy.analisarETransformar(self.endArquivoFunc,self.nomeFuncao)

            if(self.codigo[0] == False):
                self.labelAviso.setText(u""+self.codigo[1])
            else:
                #----------

                self.entrada = imgIO.abrir(self.endArquivoImg,self.nomeImagem)

                if(self.entrada[0] == False):
                    self.labelAviso.setText(u""+self.entrada[1])
                else:
                    #----------

                    self.parametrosReceber = self.codigo[4]

                    #----------

                    nBandas = self.entrada[1].RasterCount

                    optionsCB = ['Selecione','Valor']

                    i = 0
                    while(i < nBandas):
                        optionsCB.append('Banda '+str(i+1))
                        i = i + 1

                    #----------

                #----------

                    widgetSC = QtGui.QWidget()
                    verticalBox = QtGui.QVBoxLayout(widgetSC)

                    self.listaComboBox = []
                    self.listaLineEdit = []

                    for i in xrange(len(self.parametrosReceber)):
                        _aux = QtGui.QHBoxLayout()
                        _aux.addWidget(QtGui.QLabel(self.parametrosReceber[i]))

                        _auxCB = QtGui.QComboBox()
                        _auxCB.addItems(optionsCB)

                        _aux.addWidget(_auxCB)

                        _auxLE = QtGui.QLineEdit()
                        _aux.addWidget(_auxLE)

                        _aux.addStretch(1)
                        verticalBox.addLayout(_aux)

                        self.listaComboBox.append(_auxCB)
                        self.listaLineEdit.append(_auxLE)

                    self.scrollArea.setWidget(widgetSC)

                #----------

    def abrirImg(self):
        self.nomeImagem = str(QtGui.QFileDialog.getOpenFileName())
        self.lineEditAbrirImg.setText(self.nomeImagem)

        i = len(self.nomeImagem)-1
        posPath = 0
        posExt = 0

        while(i > 0):
            if(self.nomeImagem[i] == '/'):
                posPath = i
                break

            if(self.nomeImagem[i] == '.'):
                posExt = i

            i = i - 1

        self.endArquivoImg = self.nomeImagem[:posPath+1]
        self.extensaoImg = self.nomeImagem[posExt:]
        self.nomeImagem = self.nomeImagem[posPath+1:]

        self.sCAParametros()

    def abrirFunc(self):
        self.nomeFuncao = str(QtGui.QFileDialog.getOpenFileName())
        self.lineEditAbrirFunc.setText(self.nomeFuncao)

        i = len(self.nomeFuncao)-1
        posPath = 0

        while(i > 0):
            if(self.nomeFuncao[i] == '/'):
                posPath = i
                break

            i = i - 1

        self.endArquivoFunc = self.nomeFuncao[:posPath+1]
        self.nomeFuncao = self.nomeFuncao[posPath+1:]

        self.sCAParametros()

    def verificarParametros(self):
        for i in xrange(len(self.listaComboBox)):
            if(self.listaComboBox[i].currentText() == 'Selecione'):
                self.labelAviso.setText("Parametros faltando.")
                return False

        return True

    def verificarValorParametros(self):
        for i in xrange(len(self.listaComboBox)):
            if(self.listaComboBox[i].currentText() == 'Valor'):
                if(str(self.listaLineEdit[i].text()).strip() != ''):
                    self.valoresParametros[i] = float(str(self.listaLineEdit[i].text()))
                else:
                    self.labelAviso.setText('Valor faltando.')
                    return False
            else:
                self.valoresParametros[i] = str(self.listaComboBox[i].currentText())
                self.bSelecionadas.append(int(self.valoresParametros[i][6:]))
                self.valoresParametros[i] = 'bandas['+self.valoresParametros[i][6:]+']'

        return True

    def executar(self):
        self.valoresParametros = numpy.empty([len(self.parametrosReceber)],dtype=numpy.ndarray)

        if(len(self.lineEditAbrirImg.text()) < 1):
            self.labelAviso.setText(u"Imagem não definida.")
        elif(len(self.lineEditAbrirFunc.text()) < 1):
            self.labelAviso.setText(u"Função não definida.")
        else:
            self.labelAviso.setText("")

            #----------

            if(self.verificarParametros()):
                self.bSelecionadas = []

                if(self.verificarValorParametros()):
                    auxValPar = ''

                    i = 0
                    while(i < len(self.valoresParametros)):
                        auxValPar = auxValPar + str(self.valoresParametros[i]) + ','

                        i = i + 1

                    self.parametros = auxValPar[:len(auxValPar)-1]

                    #----------

                    self.bandas = imgIO.ler(self.entrada[1],self.bSelecionadas)

                    #----------

                    self.retorno = toPy.executar(self.codigo,self.bandas,self.parametros)

                    #----------

                    self.terminado = imgIO.salvar(self.entrada[1],self.retorno,self.codigo[3],self.endArquivoImg,self.extensaoImg)

                    if(self.terminado[0] == False):
                        self.labelAviso.setText(u""+self.terminado[1])

                    #----------

                    self.labelAviso.setText(u"Processo Concluído.")

                    #----------

                #----------

            #----------

    def setupUi(self, Principal):
        Principal.setObjectName(_fromUtf8("Principal"))
        Principal.setWindowModality(QtCore.Qt.NonModal)
        Principal.resize(450, 480)
        resolution = QtGui.QDesktopWidget().screenGeometry()
        Principal.move((resolution.width() / 2) - (Principal.frameSize().width() / 2),
                  (resolution.height() / 2) - (Principal.frameSize().height() / 2))
        self.centralWidget = QtGui.QWidget(Principal)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.labelAbrirFunc = QtGui.QLabel(self.centralWidget)
        self.labelAbrirFunc.setGeometry(QtCore.QRect(10, 150, 111, 30))
        self.labelAbrirFunc.setMinimumSize(QtCore.QSize(111, 0))
        self.labelAbrirFunc.setMaximumSize(QtCore.QSize(111, 16777215))
        self.labelAbrirFunc.setObjectName(_fromUtf8("labelAbrirFunc"))
        self.ButtonAbrirFunc = QtGui.QPushButton(self.centralWidget)
        self.ButtonAbrirFunc.setGeometry(QtCore.QRect(330, 150, 99, 30))
        self.ButtonAbrirFunc.setObjectName(_fromUtf8("ButtonAbrirFunc"))
        QtCore.QObject.connect(self.ButtonAbrirFunc, QtCore.SIGNAL('clicked()'), self.abrirFunc)
        self.lineEditAbrirFunc = QtGui.QLineEdit(self.centralWidget)
        self.lineEditAbrirFunc.setGeometry(QtCore.QRect(100, 150, 221, 31))
        self.lineEditAbrirFunc.setReadOnly(True)
        self.lineEditAbrirFunc.setObjectName(_fromUtf8("lineEditAbrirFunc"))
        self.labelParametrosFunc = QtGui.QLabel(self.centralWidget)
        self.labelParametrosFunc.setGeometry(QtCore.QRect(10, 190, 111, 30))
        self.labelParametrosFunc.setMinimumSize(QtCore.QSize(111, 0))
        self.labelParametrosFunc.setMaximumSize(QtCore.QSize(111, 16777215))
        self.labelParametrosFunc.setObjectName(_fromUtf8("labelParametrosFunc"))
        self.ButtonExecutar = QtGui.QPushButton(self.centralWidget)
        self.ButtonExecutar.setGeometry(QtCore.QRect(170, 440, 99, 27))
        self.ButtonExecutar.setObjectName(_fromUtf8("ButtonExecutar"))
        QtCore.QObject.connect(self.ButtonExecutar, QtCore.SIGNAL('clicked()'), self.executar)
        self.label = QtGui.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(140, 20, 181, 51))
        self.label.setObjectName(_fromUtf8("label"))
        self.ButtonAbrirImg = QtGui.QPushButton(self.centralWidget)
        self.ButtonAbrirImg.setGeometry(QtCore.QRect(330, 100, 99, 30))
        self.ButtonAbrirImg.setObjectName(_fromUtf8("ButtonAbrirImg"))
        QtCore.QObject.connect(self.ButtonAbrirImg, QtCore.SIGNAL('clicked()'), self.abrirImg)
        self.labelAbrirImg = QtGui.QLabel(self.centralWidget)
        self.labelAbrirImg.setGeometry(QtCore.QRect(10, 100, 111, 30))
        self.labelAbrirImg.setMinimumSize(QtCore.QSize(111, 0))
        self.labelAbrirImg.setMaximumSize(QtCore.QSize(111, 16777215))
        self.labelAbrirImg.setObjectName(_fromUtf8("labelAbrirImg"))
        self.lineEditAbrirImg = QtGui.QLineEdit(self.centralWidget)
        self.lineEditAbrirImg.setGeometry(QtCore.QRect(100, 100, 221, 31))
        self.lineEditAbrirImg.setReadOnly(True)
        self.lineEditAbrirImg.setObjectName(_fromUtf8("lineEditAbrirImg"))
        self.scrollArea = QtGui.QScrollArea(self.centralWidget)
        self.scrollArea.setGeometry(QtCore.QRect(117, 200, 310, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.labelAviso = QtGui.QLabel(self.centralWidget)
        self.labelAviso.setGeometry(QtCore.QRect(10, 400, 431, 31))
        self.labelAviso.setText(_fromUtf8(""))
        self.labelAviso.setObjectName(_fromUtf8("labelAviso"))
        Principal.setCentralWidget(self.centralWidget)

        self.retranslateUi(Principal)
        QtCore.QMetaObject.connectSlotsByName(Principal)

    def retranslateUi(self, Principal):
        Principal.setWindowTitle(_translate("Principal", "Landsat 5 - TM", None))
        self.labelAbrirFunc.setText(_translate("Principal", "<html><head/><body><p><span style=\" font-size:18pt;\">Função:</span></p></body></html>", None))
        self.ButtonAbrirFunc.setText(_translate("Principal", "Abrir", None))
        self.labelParametrosFunc.setText(_translate("Principal", "<html><head/><body><p><span style=\" font-size:14pt;\">Parametros:</span></p></body></html>", None))
        self.ButtonExecutar.setText(_translate("Principal", "Executar", None))
        self.label.setText(_translate("Principal", "<html><head/><body><p><span style=\" font-size:20pt;\">​Landsat 5 - TM</span></p></body></html>", None))
        self.ButtonAbrirImg.setText(_translate("Principal", "Abrir", None))
        self.labelAbrirImg.setText(_translate("Principal", "<html><head/><body><p><span style=\" font-size:16pt;\">Imagem:</span></p></body></html>", None))

#----------

class ControlPrincipal(QtGui.QMainWindow):
  def __init__(self, parent=None):
    super(ControlPrincipal, self).__init__(parent)
    self.ui =  Ui_Principal()
    self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlPrincipal()
    mySW.show()
    sys.exit(app.exec_())

#----------

fim = time.time()

print 'Tempo:',(fim-inicio)