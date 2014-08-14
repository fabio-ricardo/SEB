#coding: utf-8
import gdal, osgeo, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

class AbreImagem():
	extensao = '.tif'
	def __init__(self,nomeArquivoEntrada):
		self.driver = gdal.GetDriverByName('GTiff')
		self.driver.Register()
		self.entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)
		if  self.entrada is None:
			print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
			sys.exit(1)
		self.pastaSaida = 'S-SEBI__'+nomeArquivoEntrada+'/'
		try:
			os.mkdir(pastaSaida)
		except:
			print 'Diretorio: ' + pastaSaida + ' Já existe.'
			print 'Recriando arquivos, se existir.'
		print 'linhas:',self.getLinhas(),' colunas:',self.getColunas(),'bandas:',self.getBandas(),'driver:',self.getDriverEntrada().ShortName
	
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
	
	def saidaImagem(self,nome, calculo):
		saida = driver.Create(self.pastaSaida+nome+self.extensao,self.getColunas(),self.getLinhas(),1,GDT_Float32)
		if saida is None:
			print 'Erro ao criar o arquivo: ' + nome+self.extensao
			sys.exit(1)

		saida.SetProjection(projecao)
		banda = saida.GetRasterBand(1)
		banda.WriteArray(calculo,0,0)
		banda.SetNoDataValue(noValue)
		banda = None
		saida = None
		print nome + ' - Pronto!'
		
	

class Valores():
	def __init__(self):
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
	
	def setJulianDay(self,jd):
		self.julianDay = jd
	
	def setTa(self,ta):
		self.Ta = ta
		
	def setUR(self,ur):
		self.UR = ur
		

class Formulas(Valores):
	
	def reflectanciaParte1(self,NBandas):
		self.p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)
		for k in xrange(1,NBandas+1):
			if (k != 6):
				self.p1[k] = Valores.pi / (descBandas[k][5] * Valores.cosZ * Valores.dr)
	
	def reflectanciaParte2(self,NBandas):
		dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)
		self.albedoPlanetario = 0
		for k in xrange(1,NBandas+1):
			dados[k] = self.entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
			radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])

			if (k == 2):
				self.mask = dados[k-1] == dados[k]
				dados[k-1] = None
			elif(k > 2):
				self.mask = valueOff == dados[k]

			if(k != NBandas and k >= 2):
				valueOff = numpy.choose(mask,(numpy.nan, dados[k]))

			if(k >= 2):
				dados[k] = None

			if(k != 6):
				reflectancia = p1[k] * radiancia

				self.albedoPlanetario += descBandas[k][7] * reflectancia

				radiancia = None

				if(k == 3):
					self.reflectanciaB3 = reflectancia
				elif(k == 4):
					self.reflectanciaB4 = reflectancia

				reflectancia = None
			else:
				self.radianciaB6 = radiancia
				radiancia = None
		self.mask = numpy.choose(mask,(True,False))
		valueOff = None
		dados = None
		self.entrada = None
	
	def ndvi(self):
		self.ndvi = numpy.choose(self.mask, (Valores.noValue, (self.reflectanciaB4 - self.reflectanciaB3) / (self.reflectanciaB4 + self.reflectanciaB3)))
	
	def getNDVI(self):
		return self.ndvi
		
	def savi(self):
		self.savi = numpy.choose(self.mask, (Valores.noValue, ((1 + Valores.L) * (self.reflectanciaB4 - self.reflectanciaB3)) / (Valores.L + (self.reflectanciaB4 + self.reflectanciaB3))))
		self.reflectanciaB4 = None
		self.reflectanciaB3 = None
	
	def getSAVI(self):
		return self.savi
			
	def iaf(self):
		numpy.seterr(all='ignore')
		self.mask1 = numpy.logical_and(((0.69 - self.savi) / 0.59) > 0, self.mask)
		self.iaf = numpy.choose(self.mask1, (Valores.noValue, -1 * (numpy.log((0.69 - self.savi) / 0.59) / 0.91)))
		self.mask1 = self.savi <= 0.1
		self.iaf = numpy.choose(self.mask1,(self.iaf, 0.0))
		self.mask1 = self.savi >= 0.687
		self.iaf = numpy.choose(self.mask1,(self.iaf, 6.0))
		numpy.seterr(all='warn')
		
	def getIAF(self):
		return self.iaf
		
	def albedoSuper(self):
		self.albedoSuperficie = numpy.choose(self.mask, (Valores.noValue, (self.albedoPlanetario - Valores.ap) * Valores.p2))
		self.albedoPlanetario = None
		
	def getAlbedoSuper(self):
		return self.albedoSuperficie
		
	def enb_e_e0(self):
		self.ENB = 0.97 + 0.0033 * self.iaf
		self.E0 = 0.95 + 0.01 * self.iaf
		self.mask1 = self.iaf >= 3
		self.ENB = numpy.choose(self.mask1, (self.ENB, 0.98))
		self.E0 = numpy.choose(self.mask1, (self.E0, 0.98))
		self.mask1 = self.ndvi <= 0
		self.ENB = numpy.choose(self.mask1, (self.ENB, 0.99))
		self.E0 = numpy.choose(self.mask1, (self.E0, 0.985))
		self.mask1 = None
		self.savi = None
		self.iaf = None
	
	def temperaturaSuperficie(self):
		self.temperaturaSuperficie = numpy.choose(self.mask, (Valores.noValue, Valores.K2 / numpy.log(((self.ENB * Valores.K1) / self.radianciaB6) + 1.0)))
		self.radianciaB6 = None
		self.ENB = None
	
	def getTemperaturaSuperficie(self):
		return self.temperaturaSuperficie
	
	def radOndaLongaEmi(self):
		return (E0 * constSB) * numpy.power(temperaturaSuperficie,4)
		
		
	def saldoRadiacao(self):
		self.saldoRadiacao = numpy.choose(self.mask, (Valores.noValue, ((1.0 - self.albedoSuperficie) * Valores.radOndaCurtaInci) +\
                                    (E0 * Valores.radOndaLongaInci - this.radOndaLongaEmi())))
        self.E0 = None  
  	
  	def getSaldoRadiacao(self):
		return self.saldoRadiacao       
         
    def fluxoCalSolo(self):
		self.mask1 = self.ndvi < 0
		self.fluxoCalSolo = numpy.choose(self.mask1, (((self.temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * self.albedoSuperficie))\
							   * (1.0 - (0.98 * numpy.power(self.ndvi,4)))) * self.saldoRadiacao, Valores.G))
		self.mask1 = None
		self.fluxoCalSolo = numpy.choose(self.mask, (Valores.noValue, self.fluxoCalSolo))
		self.ndvi = None
		
	def getFluxoCalSolo(self):
		return self.fluxoCalSolo
	
	def fracaoEvaporativa(self):
		albedoSupMax = numpy.amax(self.albedoSuperficie)

		maskAlbedoSuper = numpy.logical_and(self.albedoSuperficie <= (albedoSupMax * 0.2), self.albedoSuperficie != Valores.noValue)
		limiteLadoEsq = self.temperaturaSuperficie[maskAlbedoSuper]

		maskAlbedoSuper = self.albedoSuperficie >= (albedoSupMax * 0.8)
		limiteLadoDir = self.temperaturaSuperficie[maskAlbedoSuper]

		maskAlbedoSuper = None

		self.mask1 = limiteLadoEsq != Valores.noValue
		limiteLadoEsq = limiteLadoEsq[self.mask1]

		self.mask1 = limiteLadoDir != Valores.noValue
		limiteLadoDir = limiteLadoDir[self.mask1]

		self.mask1 = None

		limiteLadoEsq = numpy.sort(limiteLadoEsq)
		limiteLadoDir = numpy.sort(limiteLadoDir)

		limSupEsq = limiteLadoEsq[::-1][0:Valores.qtdPontos]
		limInfEsq = limiteLadoEsq[0:Valores.qtdPontos]

		limSupDir = limiteLadoDir[::-1][0:Valores.qtdPontos]
		limInfDir = limiteLadoDir[0:Valores.qtdPontos]

		limiteLadoEsq = None
		limiteLadoDir = None

		#----------

		limSupEsq = numpy.mean(limSupEsq)
		limInfEsq = numpy.mean(limInfEsq)

		limSupDir = numpy.mean(limSupDir)
		limInfDir = numpy.mean(limInfDir)

		x1 = 0.1
		x2 = albedoSupMax
		x2x1 = x2 - x1

		m1 = (limSupDir - limSupEsq) / x2x1
		m2 = (limInfDir - limInfEsq) / x2x1

		c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
		c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1

		#----------

		self.fracaoEvaporativa = numpy.choose(self.mask, (Valores.noValue, (c1 + (m1 * self.albedoSuperficie) - self.temperaturaSuperficie)\
												/ ((c1 - c2) + ((m1 - m2) * self.albedoSuperficie))))
		self.temperaturaSuperficie = None

	def getFracaoEvaporativa(self):
		return self.fracaoEvaporativa

	def getFluxoCalorSensivel(self):
		return numpy.choose(self.mask, (Valores.noValue, (1 - self.fracaoEvaporativa) * (self.saldoRadiacao - self.fluxoCalSolo)))
		
	def fluxoCalorLatente(self):		
		fluxoCalorLatente = numpy.choose(mask, (noValue, fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)))
	
	def getFlucoCalorLatente(self):
		return self.fluxoCalorLatente
		
if __name__== '__main__': 
	img = AbreImagem('empilhada1000x1000.tif')
	formulas = Formulas()
	formulas.reflectanciaParte1()
	formulas.reflectanciaParte2()
	img.saidaImagem('ndvi',formulas.getNDVI())
	img.saidaImagem('savi',formulas.getSAVI())
	img.saidaImagem('iaf',formulas.getIAF())
	img.saidaImagem('albedoSuperficie',formulas.getAlbedoSuper())
	formulas.enb_e_e0()
	img.saidaImagem('temperaturaSuperficie',formulas.getTemperaturaSuperficie())
	img.saidaImagem('saldoRadiacao',formulas.getSaldoRadiacao())
	img.saidaImagem('fluxoCalSolo',formulas.getFluxoCalSolo())
	img.saidaImagem('fracaoEvaporativa',formulas.getFracaoEvaporativa())
	img.saidaImagem('fluxoCalorSensivel',formulas.getFluxoCalorSensivel())
