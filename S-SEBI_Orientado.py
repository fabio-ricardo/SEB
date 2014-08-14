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
		self.cosZ = math.cos((90 - Z) * pi / 180)
		self.julianDay = 248.0
		self.dr = 1.0 + 0.033 * math.cos((julianDay * 2 * pi) / 365)
		self.ap = 0.03
		self.Ta = 32.74
		self.UR = 36.46
		self.ea = (0.61078 * math.exp(17.269 * Ta / (237.3 + Ta))) * UR / 100.0
		self.P = 99.3
		self.W = 0.14 * ea * P + 2.1
		self.Kt = 1.0
		self.tsw = 0.35 + 0.627 * math.exp((-0.00146 * P / (Kt * cosZ)) - 0.075 * math.pow((W / cosZ), 0.4))
		self.p2 = 1.0 / (tsw * tsw)
		self.L = 0.1
		self.K1 = 607.76
		self.K2 = 1260.56
		self.constSB = 5.67E-8
		self.S = 1367.0
		self.T0 = 273.15
		self.Ea = 0.625 * math.pow((1000.0 * ea / (Ta + T0)), 0.131)
		self.radOndaCurtaInci = (S * cosZ * cosZ) / (1.085 * cosZ + 10.0 * ea * (2.7 + cosZ) * 0.001 + 0.2)
		self.radOndaLongaInci = Ea * constSB * math.pow(Ta + T0, 4)
		self.G = 0.5
		self.qtdPontos = 20
		self.Rg24h = 243.95
		self.Tao24h = 0.63
class S_SEBI(Valores):
if __name__== '__main__': 
	img = AbreImagem('empilhada1000x1000.tif')
	valores = Valores()
