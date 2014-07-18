#coding:utf-8
import osgeo
from Tkinter import *
import math
from tkFileDialog import askopenfilename
from tkMessageBox import *
import gdal, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

inicio = time.time()

class  Main:
	
	def __init__(self):
		gdal.AllRegister()
		driver = gdal.GetDriverByName('GTiff')
			
	def equiAlbedo(self):
		for k in range(1,NBandas+1):
			if (k != 6):
				p1[k] = pi / (descBandas[k][5] * cosZ * dr)
		#----------
		pastaSaida = 'S-SEBI__'+nomeArquivoEntrada

		try:
			os.mkdir(pastaSaida)
		except:
			print 'Diretorio: ' + pastaSaida + ' Já existe.'
			print 'Recriando arquivos, se existir.'
		dados = entrada.GetRasterBand(1).ReadAsArray().astype(numpy.float64)
		radiancia = descBandas[1][3] + (descBandas[1][6] * dados)
		reflectancia = p1[1] * radiancia

		albedoPlanetario = descBandas[1][7] * reflectancia

		dados = None
		radiancia = None
		reflectancia = None

		#----------

		dados = entrada.GetRasterBand(2).ReadAsArray().astype(numpy.float64)
		radiancia = descBandas[2][3] + (descBandas[2][6] * dados)
		reflectancia = p1[2] * radiancia

		albedoPlanetario += descBandas[2][7] * reflectancia

		dados = None
		radiancia = None
		reflectancia = None

		#----------

		dados = entrada.GetRasterBand(3).ReadAsArray().astype(numpy.float64)
		radiancia = descBandas[3][3] + (descBandas[3][6] * dados)
		reflectanciaB3 = p1[3] * radiancia

		albedoPlanetario += descBandas[3][7] * reflectanciaB3

		dados = None
		radiancia = None

		#----------

		dados = entrada.GetRasterBand(4).ReadAsArray().astype(numpy.float64)
		radiancia = descBandas[4][3] + (descBandas[4][6] * dados)
		reflectanciaB4 = p1[4] * radiancia

		albedoPlanetario += descBandas[4][7] * reflectanciaB4

		dados = None
		radiancia = None


class Tela(Main):
	def __init__(self,raiz):
		self.raiz = raiz
		self.raiz.title('CÁLCULO S-SEBI')
		
		raiz.maxsize(width = 500, height= 300)
		raiz.minsize(width = 500, height= 300)
		
		Label(self.raiz,text='Ângulo de Elevação Solar (graus):').grid(row=5, column=1,sticky=W, pady=5, columnspan=2)
		Label(self.raiz,text='Dia Sequencial do Ano:').grid(row=7, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Altitude do pixel (m):').grid(row=9, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Temperatura do ar (K):').grid(row=11, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Modo de processamento:').grid(row=13, column=1,sticky=W, pady=5)
		
		self.msg=Label(self.raiz,text=' CALCULO ALGORTIMO S-SEBI ',fg='black',font=('Verdana','14','bold'))
		self.msg.grid(row=1, column=1, columnspan=3)
		
		self.msg=Label(self.raiz,text='Clique em OK para iniciar o calculo')
		self.msg.grid(row=16, column=1, columnspan=3)
		
		self.ang=Entry(self.raiz, width=10)
		self.ang.grid(row=5, column=3, sticky=E+W, pady=3)
		self.ang.focus_force()
		
		self.dia=Entry(self.raiz, width=10)
		self.dia.grid(row=7, column=3, sticky=E+W, pady=3)
		self.dia.focus_force()
		
		self.alt=Entry(self.raiz, width=10)
		self.alt.grid(row=9, column=3, sticky=E+W, pady=3)
		self.alt.focus_force()
		
		self.T=Entry(self.raiz, width=10)
		self.T.grid(row=11, column=3, sticky=E+W, pady=3)
		self.T.focus_force()
		
		self.arq=Button(self.raiz, width=15, command=self.escreveNome,text='Selecionar imagem',bg = 'gray')
		self.arq.grid(row=12, column=3, padx=2, pady=3)
		
		self.ok=Button(self.raiz, width=8, command=self.inicia,text='OK',bg = 'gray')
		self.ok.grid(row=15, column=1, padx=2, pady=3, columnspan=2)
		
		self.close=Button(self.raiz, width=8, command=self.fechar,text='Fechar', bg = 'gray')
		self.close.grid(row=15, column=2, padx=4, pady=5, columnspan=2)
	
		self.radio1 = Radiobutton(text="Economia de Memória",value=1, command=self.select1)
		self.radio1.grid(row=13, column=2, padx=1, pady=2)

		self.radio2 = Radiobutton(text="Equilibrado",value=2, command=self.select2)
		self.radio2.grid(row=13, column=3, padx=1, pady=2)

		
	def select1(self): 
		global option
		option = 1	
	
	def select2(self): 
		global option
		option = 2
	
	def erroDigito(self):
		    showerror("Erro", "Valores devem ser não nulos, positivos e numéricos!")
	
	def erro(self):
		    showerror("Erro", "Arquivo não é uma imagem TIFF.")
		
		
	def inicia(self):
		global nome
		if self.ang.get().isdigit() and self.dia.get().isdigit() and self.alt.get().isdigit() and self.T.get().isdigit() and (nomeArquivoEntrada[-4:] == '.tif' or nomeArquivoEntrada[-5:] == '.tiff'):
			global cosX, dr, z, Ta
			cosZ = math.pi*(90 -float(self.ang.get()))/180
			dr = 1+0.033*math.cos((2*math.pi* float(self.dia.get()))/365)
			z = float(self.alt.get())
			Ta = float(self.T.get())
			self.fechar()
		else: 
			if not(nomeArquivoEntrada[-4:] == '.tif' or nomeArquivoEntrada[-5:] == '.tiff'):
				self.erro()
			else:
				self.erroDigito()

	def fechar(self): 
		self.raiz.destroy()
	
	def escreveNome(self):
		global nomeArquivoEntrada
		nomeArquivoEntrada = askopenfilename()
		Label(self.raiz,text=nomeArquivoEntrada).grid(row=12, column=1,sticky=W, pady=5)
	

if __name__== '__main__': Main() 

option = 0
pi = math.pi
cosZ = 0
dr = 0
ap = 0.03
z = 0
Ta = 0
nomeArquivoEntrada = ''

inst1=Tk()
Tela(inst1)
inst1.mainloop()

entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)	
if  entrada is None:
	print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
	sys.exit(1)
	
linhas = entrada.RasterYSize
colunas = entrada.RasterXSize
NBandas = entrada.RasterCount
driverEntrada = entrada.GetDriver()

tsw = 0.75 + 2*0.00001 * z
p2 = 1 / (tsw * tsw)
L = 0.5
K1 = 607.76
K2 = 1260.56
constSB = 0.0000000567
S = 1367
radOndaCurtaInci = S * cosZ * dr * tsw
Ea = 0.85 * math.pow(-1 * math.log(tsw),0.09)
radOndaLongaInci = Ea * constSB * math.pow(Ta,4)
qtdPontos = 20
x1 = 0.1
x2 = 0.9
x2x1 = x2 - x1
ap = 0.03
p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
p1[0] = 0
p1[6] = 0

print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driverEntrada.ShortName

