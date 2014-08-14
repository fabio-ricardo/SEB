#coding: utf-8
import gdal, osgeo, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

class AbreImagem():
	def __init__(self,nomeArquivoEntrada):
		self.driver = gdal.GetDriverByName('GTiff')
		self.driver.Register()
		self.entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)
		if  self.entrada is None:
			print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
			sys.exit(1)
		pastaSaida = 'S-SEBI__'+nomeArquivoEntrada+'/'
		try:
			os.mkdir(pastaSaida)
		except:
			print 'Diretorio: ' + pastaSaida + ' Já existe.'
			print 'Recriando arquivos, se existir.'
	
	def getLinhas(self):
		return self.entrada.RasterYSize
	
	def getColunas(self):
		return self.entrada.RasterXSize
	
	def getDriverEntrada(self):
		return self.entrada.GetDriver()
	
	def getBandas(self):
		return self.entrada.RasterCount
	
	def getProjecao(self):	
		return self.entrada.GetProjection()

class Valores():
	def __init__(self):
		self.extensao = '.tif'
		self.noValue = -9999.0
		self.pi = math.pi
		self.Z = 50.24
		self.cosZ = math.cos((90 - self.Z) * self.pi / 180)
		self.julianDay = 248.0
		self.dr = 1.0 + 0.033 * math.cos((self.julianDay * 2 * self.pi) / 365)
		self.ap = 0.03
		self.Ta = 32.74
		self.UR = 36.46
		self.ea = (0.61078 * math.exp(17.269 * self.Ta / (237.3 + self.Ta))) * self.UR / 100.0
		self.P = 99.3
		self.W = 0.14 * self.ea * self.P + 2.1
		self.Kt = 1.0
		self.tsw = 0.35 + 0.627 * math.exp((-0.00146 * self.P / (self.Kt * self.cosZ)) - 0.075 * math.pow((self.W / self.cosZ), 0.4))
		self.p2 = 1.0 / (self.tsw * self.tsw)
		self.L = 0.1
		self.K1 = 607.76
		self.K2 = 1260.56
		self.constSB = 5.67E-8
		self.S = 1367.0
		self.T0 = 273.15
		self.Ea = 0.625 * math.pow((1000.0 * self.ea / (self.Ta + self.T0)), 0.131)
		self.radOndaCurtaInci = (self.S * self.cosZ * self.cosZ) / (1.085 * self.cosZ + 10.0 * self.ea * (2.7 + self.cosZ) * 0.001 + 0.2)
		self.radOndaLongaInci = self.Ea * self.constSB * math.pow(self.Ta + self.T0, 4)
		self.G = 0.5
		self.qtdPontos = 20
		self.Rg24h = 243.95
		self.Tao24h = 0.63

	def setZ(self,z):
		self.Z = z
	
	def setJulianDay(self,n):
		self.julianDay = n
	
	def setTa(self,n):
		self.Ta = n
		
	def setUR(self,n):
		self.UR = n
		
	def setEA(self,n):
		self.ea = n

class Formulas(Valores):
	def reflectanciaParte1(self,NBandas):
		self.p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)
		for k in xrange(1,NBandas+1):
			if (k != 6):
				self.p1[k] = Valores.pi / (descBandas[k][5] * Valores.cosZ * Valores.dr)
		
	
if __name__== '__main__': 
	img = AbreImagem('empilhada1000x1000.tif')
	
