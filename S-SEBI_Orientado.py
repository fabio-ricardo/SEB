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
			os.mkdir(self.pastaSaida)
		except:
			print 'Diretorio: ' + self.pastaSaida + ' Já existe.'
			print 'Recriando arquivos, se existir.'
		print 'linhas:',self.getLinhas(),' colunas:',self.getColunas(),'bandas:',self.getBandas(),'driver:',self.getDriverEntrada().ShortName
	
	def getEntrada(self):
		return self.entrada
	
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
		saida = self.driver.Create(self.pastaSaida+nome+self.extensao,self.getColunas(),self.getLinhas(),1,GDT_Float32)
		if saida is None:
			print 'Erro ao criar o arquivo: ' + nome+self.extensao
			sys.exit(1)

		saida.SetProjection(self.getProjecao())
		banda = saida.GetRasterBand(1)
		banda.WriteArray(calculo,0,0)
		banda.SetNoDataValue(Valores.noValue)
		banda = None
		saida = None
		print nome + ' - Pronto!'
		
	

class Valores():

	noValue = -9999.0
	pi = math.pi
	Z = 50.24
	cosZ = math.cos((90 - Z) * pi / 180)
	julianDay = 248.0
	dr = 1.0 + 0.033 * math.cos((julianDay * 2 * pi) / 365)
	ap = 0.03
	Ta = 32.74
	UR = 36.46
	ea = (0.61078 * math.exp(17.269 * Ta / (237.3 + Ta))) * UR / 100.0
	P = 99.3
	W = 0.14 * ea * P + 2.1
	Kt = 1.0
	tsw = 0.35 + 0.627 * math.exp((-0.00146 * P / (Kt * cosZ)) - 0.075 * math.pow((W / cosZ), 0.4))
	p2 = 1.0 / (tsw * tsw)
	L = 0.1
	K1 = 607.76
	K2 = 1260.56
	constSB = 5.67E-8
	S = 1367.0
	T0 = 273.15
	Ea = 0.625 * math.pow((1000.0 * ea / (Ta + T0)), 0.131)
	radOndaCurtaInci = (S * cosZ * cosZ) / (1.085 * cosZ + 10.0 * ea * (2.7 + cosZ) * 0.001 + 0.2)
	radOndaLongaInci = Ea * constSB * math.pow(Ta + T0, 4)
	G = 0.5
	qtdPontos = 20
	Rg24h = 243.95
	Tao24h = 0.63

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
	
	def reflectanciaParte2(self,NBandas,entrada):
		dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)
		self.albedoPlanetario = 0
		for k in xrange(1,NBandas+1):
			dados[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
			radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])

			if (k == 2):
				self.mask = dados[k-1] == dados[k]
				dados[k-1] = None
			elif(k > 2):
				self.mask = valueOff == dados[k]

			if(k != NBandas and k >= 2):
				valueOff = numpy.choose(self.mask,(numpy.nan, dados[k]))

			if(k >= 2):
				dados[k] = None

			if(k != 6):
				reflectancia = self.p1[k] * radiancia

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
		self.mask = numpy.choose(self.mask,(True,False))
		valueOff = None
		dados = None
		self.entrada = None
	
	def fazCalculos(self):	
		self.ndvi()
		self.savi()
		self.iaf()
		self.albedoSuper()
		self.enb_e_e0()
		self.temperaturaSuperficie()
		self.saldoRadiacao()
		self.fluxoCalSolo()
		self.fracaoEvaporativa()
		self.passoFinal()
	
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
		return (self.E0 * Valores.constSB) * numpy.power(self.temperaturaSuperficie,4)
		
		
	def saldoRadiacao(self):
		self.saldoRadiacao = numpy.choose(self.mask, (Valores.noValue, ((1.0 - self.albedoSuperficie) * Valores.radOndaCurtaInci) +\
                                    (self.E0 * Valores.radOndaLongaInci - self.radOndaLongaEmi())))
		
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

		limSupEsq = numpy.average(limSupEsq)
		limInfEsq = numpy.average(limInfEsq)
		limSupDir = numpy.average(limSupDir)
		limInfDir = numpy.average(limInfDir)
		
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
	
	def getFluxoCalorLatente(self):
		return numpy.choose(self.mask, (Valores.noValue, self.fracaoEvaporativa * (self.saldoRadiacao - self.fluxoCalSolo)))
		
	def getEvapotranspiracao24h(self):
		return numpy.choose(self.mask, (Valores.noValue, (self.fracaoEvaporativa * (Valores.Rg24h * (1.0 - self.albedoSuperficie)\
                                                    - 110.0 * Valores.Tao24h) * 86.4) / 2450.0))
	def passoFinal(self):
		self.mask = None
		self.evapotranspiracao24h = None
		self.fluxoCalorLatente = None
		self.fracaoEvaporativa = None
		self.fluxoCalSolo = None
		self.saldoRadiacao = None
		self.albedoSuperficie = None

if __name__== '__main__': 
	inicio = time.time()
	
	img = AbreImagem('empilhada2000x2000.tif')
	formulas = Formulas()
	formulas.reflectanciaParte1(img.getBandas())
	formulas.reflectanciaParte2(img.getBandas(),img.getEntrada())
	formulas.fazCalculos()
	img.saidaImagem('ndvi',formulas.getNDVI())
	img.saidaImagem('savi',formulas.getSAVI())
	img.saidaImagem('iaf',formulas.getIAF())
	img.saidaImagem('albedoSuperficie',formulas.getAlbedoSuper())
	img.saidaImagem('temperaturaSuperficie',formulas.getTemperaturaSuperficie())
	img.saidaImagem('saldoRadiacao',formulas.getSaldoRadiacao())
	img.saidaImagem('fluxoCalSolo',formulas.getFluxoCalSolo())
	img.saidaImagem('fracaoEvaporativa',formulas.getFracaoEvaporativa())
	img.saidaImagem('fluxoCalorSensivel',formulas.getFluxoCalorSensivel())
	img.saidaImagem('fluxoCalorLatente',formulas.getFluxoCalorLatente())
	img.saidaImagem('evapotranspiracao24h',formulas.getEvapotranspiracao24h())
	img.passoFinal()
	img = None
	formulas = None
	fim = time.time()

	print 'Tempo total: '+str(fim - inicio)+' segundos.'
