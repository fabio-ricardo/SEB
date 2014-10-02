#coding: utf-8
import gdal, osgeo, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

#Pega os dados da imagem
class AbreImagem():
	def __init__(self,nomeArquivoEntrada, algNome):
		self.driver = gdal.GetDriverByName('GTiff')
		self.driver.Register()
		self.extensao = '.tif'
		self.entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)
		if  self.entrada is None:
			print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
			sys.exit(1)
		
		self.pastaSaida = algNome+'__'+nomeArquivoEntrada+'/'
		
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
	
	def criaImagem(self,nome, linhas, colunas):
		saida = self.driver.Create(self.pastaSaida+nome+self.extensao,colunas, linhas,1,GDT_Float32)
		if saida is None:
			print 'Erro ao criar o arquivo: ' + nome+self.extensao
			sys.exit(1)
		saida.SetProjection(self.getProjecao())
		return saida, saida.GetRasterBand(1)
	
	def saidaImagem(self,nome, banda, calculo,i, j):
		banda.WriteArray(calculo, j , i)
		banda.SetNoDataValue(Valores.noValue)
		print nome + ' - Pronto!'
		
	
#Valores a serem usados
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

#Salva as imagens obtidas pelos cálculos
class SalvaImagens():
	def __init__(self, nome, algNome,fracao):
		self.img = AbreImagem(nome, algNome)	
		self.linhas = self.img.getLinhas()
		self.colunas = self.img.getColunas()
		self.fracao = fracao
	
		self.saidaNDVI, self.bandaNDVI = self.img.criaImagem('ndvi', self.linhas, self.colunas)
		self.saidaSAVI, self.bandaSAVI = self.img.criaImagem('savi', self.linhas, self.colunas)
		self.saidaIAF,self.bandaIAF = self.img.criaImagem('iaf', self.linhas, self.colunas)
		self.saidaAlbedo, self.bandaAlbedoSuper = self.img.criaImagem('albedoSuperficie', self.linhas, self.colunas)
		self.saidaTemp, self.bandaTempSuper = self.img.criaImagem('temperaturaSuperficie', self.linhas, self.colunas)
		self.saidaRad, self.bandaSaldoRad = self.img.criaImagem('saldoRadiacao', self.linhas, self.colunas)
		self.saidaFluxo, self.bandaFluxo = self.img.criaImagem('fluxoCalSolo', self.linhas, self.colunas)
		self.saidaFracao, self.bandaFracao = self.img.criaImagem('fracaoEvaporativa', self.linhas, self.colunas)
		self.saidaCalSen, self.bandaCalSen = self.img.criaImagem('fluxoCalorSensivel', self.linhas, self.colunas)
		self.saidaCalLat, self.bandaCalLat = self.img.criaImagem('fluxoCalorLatente', self.linhas, self.colunas)
		self.saidaEvap, self.bandaEvap = self.img.criaImagem('evapotranspiração24h', self.linhas, self.colunas)
	
	def EscreveTudo(self,Ta, UR, Z, julianDay):
		formulas = Formulas( Ta, UR, Z, julianDay)
		formulas.setBandasSaida(self.saidaNDVI,self.bandaNDVI, self.saidaSAVI, self.bandaSAVI, self.saidaIAF,self. bandaIAF, self.saidaAlbedo, 
		self.bandaAlbedoSuper,self.saidaTemp, self.bandaTempSuper,self.saidaRad, self.bandaSaldoRad, self.saidaFluxo, self.bandaFluxo, self.saidaFracao, self.bandaFracao,
		self.saidaCalSen, self.bandaCalSen, self.saidaCalLat, self.bandaCalLat,self.saidaEvap, self.bandaEvap)
		
		for i in xrange(0,self.linhas,self.yBlockSize):
			if i + self.yBlockSize < self.linhas:
				lerLinhas = self.yBlockSize
			else:
				lerLinhas = self.linhas - i

			for j in xrange(0,self.colunas,self.xBlockSize):
				if j + self.xBlockSize < self.colunas:
					lerColunas = self.xBlockSize
				else:
					lerColunas = self.colunas - j
				
				formulas.reflectanciaParte1(self.img.getBandas())
				formulas.reflectanciaParte2(self.img.getBandas(),self.img.getEntrada(), j, i, lerColunas, lerLinhas)
				formulas.fazCalculos(self.fracao, i, j, lerLinhas, lerColunas)
				self.img.saidaImagem('ndvi',self.bandaNDVI,formulas.getNDVI(), i, j)
				self.img.saidaImagem('savi',self.bandaSAVI,formulas.getSAVI(), i, j)
				self.img.saidaImagem('iaf', self.bandaIAF, formulas.getIAF(), i, j)
				self.img.saidaImagem('albedoSuperficie', self.bandaAlbedoSuper, formulas.getAlbedoSuper(), i, j)
				self.img.saidaImagem('temperaturaSuperficie',self.bandaTempSuper, formulas.getTemperaturaSuperficie(), i, j)
				self.img.saidaImagem('saldoRadiacao',self.bandaSaldoRad, formulas.getSaldoRadiacao(), i, j)
				self.img.saidaImagem('fluxoCalSolo',self.bandaFluxo, formulas.getFluxoCalSolo(), i, j)
				
				self.img.saidaImagem('fracaoEvaporativa', self.bandaFracao, formulas.getFracaoEvaporativa(), i, j)

				self.img.saidaImagem('fluxoCalorSensivel', self.bandaCalSen, formulas.getFluxoCalorSensivel(), i,j )
				self.img.saidaImagem('fluxoCalorLatente',self.bandaCalLat, formulas.getFluxoCalorLatente(), i,j)
				self.img.saidaImagem('evapotranspiracao24h',self.bandaEvap, formulas.getEvapotranspiracao24h(), i,j)
				formulas.passoFinal()
					
		self.saidaNDVI = self.bandaNDVI = None
		self.saidaSAVI = self.bandaSAVI = None
		self.saidaIAF = self.bandaIAF = None
		self.saidaAlbedo = self.bandaAlbedoSuper = None
		self.saidaTemp = self.bandaTempSuper = None
		self.saidaRad = self.bandaSaldoRad = None
		self.saidaFluxo = self.bandaFluxo = None
		self.saidaFracao = self.bandaFracao = None
		self.saidaCalSen = self.bandaCalSen = None
		self.saidaCalLat = self.bandaCalLat = None
		self.saidaEvap = self.bandaEvap = None
		img = None
		formulas = None
		
	def setBlockSize(self, xBlockSize, yBlockSize):
		self.xBlockSize = xBlockSize
		self.yBlockSize = yBlockSize
		
	def setFullSize(self):
		self.xBlockSize = self.img.getLinhas()
		self.yBlockSize = self.img.getColunas()

#Todas as fórmulas utilizadas
class Formulas():
	def __init__(self, Ta, UR, Z, julianDay):
		 self.valores = Valores()
		 self.valores.setTa(Ta)
		 self.valores.setUR(UR)
		 self.valores.setZ(Z)
		 self.valores.setJulianDay(julianDay)
		 self.albedoSupMax = 0
		 
	
	def setBandasSaida(self, saidaNDVI,bandaNDVI, saidaSAVI, bandaSAVI, saidaIAF, bandaIAF, saidaAlbedo, bandaAlbedoSuper,
	saidaTemp, bandaTempSuper, saidaRad, bandaSaldoRad, saidaFluxo, bandaFluxo, saidaFracao, bandaFracao, saidaCalSen, bandaCalSen, saidaCalLat, bandaCalLat,
	saidaEvap, bandaEvap):
		self.saidaNDVI = saidaNDVI
		self.bandaNDVI = bandaNDVI
		self.saidaSAVI = saidaSAVI
		self.bandaSAVI = bandaSAVI
		self.saidaIAF = saidaIAF
		self.bandaIAF = bandaIAF
		self.saidaAlbedo = saidaAlbedo
		self.bandaAlbedoSuper = bandaAlbedoSuper
		self.saidaTemp = saidaTemp
		self.bandaTempSuper = bandaTempSuper
		self.saidaRad = saidaRad
		self.bandaSaldoRad = bandaSaldoRad
		self.saidaFluxo = saidaFluxo
		self.bandaFluxo = bandaFluxo
		self.saidaFracao = saidaFracao
		self.bandaFracao = bandaFracao
		self.saidaCalSen = saidaCalSen
		self.bandaCalSen = bandaCalSen
		self.saidaCalLat = saidaCalLat
		self.bandaCalLat = bandaCalLat
		self.saidaEvap = saidaEvap
		self.bandaEvap = bandaEvap
	
	def reflectanciaParte1(self,NBandas):
		self.p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)
		for k in xrange(1,NBandas+1):
			if (k != 6):
				self.p1[k] = self.valores.pi / (descBandas[k][5] * self.valores.cosZ * self.valores.dr)
	
	def reflectanciaParte2(self,NBandas,entrada, j, i, lerColunas, lerLinhas):
		dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)
		self.albedoPlanetario = 0
		for k in xrange(1,NBandas+1):
			dados[k] = entrada.GetRasterBand(k).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
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
		#self.entrada = None
	
	def fazCalculos(self, fracao,i, j, lerLinhas, lerColunas):	
		self.setNdvi()
		self.setSavi()
		self.setIaf()
		self.albedoSuper()
		self.enb_e_e0()
		self.tempSuper()
		self.setSaldoRadiacao()
		self.setFluxoCalSolo()
		exec(fracao)
	
	def setNdvi(self):
		self.ndvi = numpy.choose(self.mask, (self.valores.noValue, (self.reflectanciaB4 - self.reflectanciaB3) / (self.reflectanciaB4 + self.reflectanciaB3)))

	def getNDVI(self):
		return self.ndvi
		
	def setSavi(self):
		self.savi = numpy.choose(self.mask, (self.valores.noValue, ((1 + self.valores.L) * (self.reflectanciaB4 - self.reflectanciaB3)) / (self.valores.L + (self.reflectanciaB4 + self.reflectanciaB3))))
		self.reflectanciaB4 = None
		self.reflectanciaB3 = None
	
	def getSAVI(self):
		return self.savi
			
	def setIaf(self):
		numpy.seterr(all='ignore')
		self.mask1 = numpy.logical_and(((0.69 - self.savi) / 0.59) > 0, self.mask)
		self.iaf = numpy.choose(self.mask1, (self.valores.noValue, -1 * (numpy.log((0.69 - self.savi) / 0.59) / 0.91)))
		self.mask1 = self.savi <= 0.1
		self.iaf = numpy.choose(self.mask1,(self.iaf, 0.0))
		self.mask1 = self.savi >= 0.687
		self.iaf = numpy.choose(self.mask1,(self.iaf, 6.0))
		numpy.seterr(all='warn')
		
	def getIAF(self):
		return self.iaf
		
	def albedoSuper(self):
		self.albedoSuperficie = numpy.choose(self.mask, (self.valores.noValue, (self.albedoPlanetario - self.valores.ap) * self.valores.p2))
		if numpy.amax(self.albedoSuperficie) > self.albedoSupMax:
			self.albedoSupMax = numpy.amax(self.albedoSuperficie)
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
	
	def tempSuper(self):
		self.temperaturaSuperficie = numpy.choose(self.mask, (self.valores.noValue, self.valores.K2 / numpy.log(((self.ENB * self.valores.K1) / self.radianciaB6) + 1.0)))
		self.radianciaB6 = None
		self.ENB = None
	
	def getTemperaturaSuperficie(self):
		return self.temperaturaSuperficie
	
	def radOndaLongaEmi(self):
		return (self.E0 * self.valores.constSB) * numpy.power(self.temperaturaSuperficie,4)
		
		
	def setSaldoRadiacao(self):
		self.saldoRadiacao = numpy.choose(self.mask, (self.valores.noValue, ((1.0 - self.albedoSuperficie) * self.valores.radOndaCurtaInci) +\
                                    (self.E0 * self.valores.radOndaLongaInci - self.radOndaLongaEmi())))
		
		self.E0 = None  
  	
  	def getSaldoRadiacao(self):
		return self.saldoRadiacao       
         
	def setFluxoCalSolo(self):
		self.mask1 = self.ndvi < 0
		self.fluxoCalSolo = numpy.choose(self.mask1, (((self.temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * self.albedoSuperficie))\
							   * (1.0 - (0.98 * numpy.power(self.ndvi,4)))) * self.saldoRadiacao, self.valores.G * self.saldoRadiacao))
		self.mask1 = None
		self.fluxoCalSolo = numpy.choose(self.mask, (self.valores.noValue, self.fluxoCalSolo))
		
	def getFluxoCalSolo(self):
		return self.fluxoCalSolo

	def getFracaoEvaporativa(self):
		return self.fracaoEvaporativa

	def getFluxoCalorSensivel(self):
		return numpy.choose(self.mask, (self.valores.noValue, (1 - self.fracaoEvaporativa) * (self.saldoRadiacao - self.fluxoCalSolo)))
	
	def getFluxoCalorLatente(self):
		return numpy.choose(self.mask, (self.valores.noValue, self.fracaoEvaporativa * (self.saldoRadiacao - self.fluxoCalSolo)))
		
	def getEvapotranspiracao24h(self):
		return numpy.choose(self.mask, (self.valores.noValue, (self.fracaoEvaporativa * (self.valores.Rg24h * (1.0 - self.albedoSuperficie)\
                                                    - 110.0 * self.valores.Tao24h) * 86.4) / 2450.0))
		
	def passoFinal(self):
		self.temperaturaSuperficie = None
		self.mask = None
		self.evapotranspiracao24h = None
		self.fluxoCalorLatente = None
		self.fracaoEvaporativa = None
		self.fluxoCalSolo = None
		self.saldoRadiacao = None
		self.albedoSuperficie = None
		self.ndvi = None
		self.savi = None
		self.iaf = None
	
	def fracaoEvaporativaSSEBI(self, i, j, lerLinhas, lerColunas):
		limSupEsq = numpy.zeros([self.valores.qtdPontos],dtype=numpy.float32)
		limInfEsq = numpy.zeros([self.valores.qtdPontos],dtype=numpy.float32)
		limEsqPVez = True
		limSupDir = numpy.zeros([self.valores.qtdPontos],dtype=numpy.float32)
		limInfDir = numpy.zeros([self.valores.qtdPontos],dtype=numpy.float32)
		limDirPVez = True
		albedoSuperficie = self.bandaAlbedoSuper.ReadAsArray(j,i,lerColunas,lerLinhas)
		temperaturaSuperficie = self.bandaTempSuper.ReadAsArray(j,i,lerColunas,lerLinhas)
		maskAlbedoSuper = numpy.logical_and(albedoSuperficie <= (self.albedoSupMax * 0.2), albedoSuperficie != self.valores.noValue)
		limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]
		maskAlbedoSuper = albedoSuperficie >= (self.albedoSupMax * 0.8)
		limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]
		maskAlbedoSuper = None
		albedoSuperficie = None
		temperaturaSuperficie = None
		self.mask1 = limiteLadoEsq != self.valores.noValue
		limiteLadoEsq = limiteLadoEsq[self.mask1]
		self.mask1 = limiteLadoDir != self.valores.noValue
		limiteLadoDir = limiteLadoDir[self.mask1]
		self.mask1 = None
		if (limiteLadoEsq.size > 0):
			if (limEsqPVez):
				limiteLadoEsq = numpy.sort(limiteLadoEsq)
				limSupEsq = limiteLadoEsq[::-1][0:self.valores.qtdPontos]
				limInfEsq = limiteLadoEsq[0:self.valores.qtdPontos]
				limEsqPVez = False
			else:
				limSupEsq = numpy.sort(numpy.concatenate((limSupEsq,limiteLadoEsq)))[::-1][0:self.valores.qtdPontos]
				limInfEsq = numpy.sort(numpy.concatenate((limInfEsq,limiteLadoEsq)))[0:self.valores.qtdPontos]
		if (limiteLadoDir.size > 0):
			if (limDirPVez):
				limiteLadoDir = numpy.sort(limiteLadoDir)
				limSupDir = limiteLadoDir[::-1][0:self.valores.qtdPontos]
				limInfDir = limiteLadoDir[0:self.valores.qtdPontos]
				limDirPVez = False
			else:
				limSupDir = numpy.sort(numpy.concatenate((limSupDir,limiteLadoDir)))[::-1][0:self.valores.qtdPontos]
				limInfDir = numpy.sort(numpy.concatenate((limInfDir,limiteLadoDir)))[0:self.valores.qtdPontos]
		limiteLadoEsq = None
		limiteLadoDir = None	
		
		self.limSupEsq = numpy.average(limSupEsq)
		self.limInfEsq = numpy.average(limInfEsq)
		self.limSupDir = numpy.average(limSupDir)
		self.limInfDir = numpy.average(limInfDir)
		
	def fracao(self):	
		x1 = 0.1
		x2 = self.albedoSupMax
		x2x1 = x2 - x1
		m1 = (self.limSupDir - self.limSupEsq) / x2x1
		m2 = (self.limInfDir - self.limInfEsq) / x2x1
		c1 = ((x2 * self.limSupEsq) - (x1 * self.limSupDir)) / x2x1
		c2 = ((x2 * self.limInfEsq) - (x1 * self.limInfDir)) / x2x1
		self.fracaoEvaporativa = numpy.choose(self.mask, (self.valores.noValue, (c1 + (m1 * self.getAlbedoSuper()) - self.temperaturaSuperficie)/((c1 - c2) + ((m1 - m2) * self.getAlbedoSuper()))))

	def fracaoEvaporativaSSEB(self):
		hotNdvi = numpy.array([],dtype=numpy.float32)
		coldTemp = numpy.array([],dtype=numpy.float32)
		coldNdvi = numpy.array([],dtype=numpy.float32)
		hotTemp = numpy.array([],dtype=numpy.float32)
		tempSuperficie = self.temperaturaSuperficie
		tempSuperficie.reshape(-1)
		ndvi_aux = self.getNDVI()
		ndvi_aux.reshape(-1)
		tempSuperficie = tempSuperficie[self.mask]
		ndvi_aux = ndvi_aux[self.mask]
		for i in xrange(self.valores.qtdPontos):
			if hotNdvi.size < self.valores.qtdPontos:
				tempNdviIgual = numpy.array([])
				hotNdvi = numpy.append(hotNdvi,ndvi_aux[numpy.nanargmax(ndvi_aux)])
				tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[numpy.nanargmax(ndvi_aux)])
				ndvi_aux[numpy.nanargmax(ndvi_aux)] = numpy.nan
				prox = numpy.nanargmax(ndvi_aux)
				posUlt = hotNdvi.size-1
				while hotNdvi[posUlt] == ndvi_aux[prox]:
					tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[prox])
					ndvi_aux[prox] = numpy.nan
					prox = numpy.nanargmax(ndvi_aux)
				if tempNdviIgual.size > 1:
					tempNdviIgual = numpy.sort(tempNdviIgual)
					tamTempNdviIg = tempNdviIgual.size
					if tamTempNdviIg > (self.valores.qtdPontos - posUlt):
						tamTempNdviIg = self.valores.qtdPontos - posUlt
					coldTemp = numpy.append(coldTemp,tempNdviIgual[:tamTempNdviIg])
					for j in xrange(tamTempNdviIg-1):
						hotNdvi = numpy.append(hotNdvi,hotNdvi[posUlt])
				else:
					coldTemp = numpy.append(coldTemp,tempNdviIgual[0])
				tempNdviIgual = None
			if coldNdvi.size < self.valores.qtdPontos:
				tempNdviIgual = numpy.array([])
				coldNdvi = numpy.append(coldNdvi,ndvi_aux[numpy.nanargmin(ndvi_aux)])
				tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[numpy.nanargmin(ndvi_aux)])
				ndvi_aux[numpy.nanargmin(ndvi_aux)] = numpy.nan
				prox = numpy.nanargmin(ndvi_aux)
				posUlt = coldNdvi.size-1
				while coldNdvi[posUlt] == ndvi_aux[prox]:
					tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[prox])
					ndvi_aux[prox] = numpy.nan
					prox = numpy.nanargmin(ndvi_aux)
				if tempNdviIgual.size > 1:
					tempNdviIgual = numpy.sort(tempNdviIgual)[::-1]
					tamTempNdviIg = tempNdviIgual.size
					if tamTempNdviIg > (self.valores.qtdPontos - posUlt):
						tamTempNdviIg = self.valores.qtdPontos - posUlt
					hotTemp = numpy.append(hotTemp,tempNdviIgual[:tamTempNdviIg])
					for j in xrange(tamTempNdviIg-1):
						coldNdvi = numpy.append(coldNdvi,coldNdvi[posUlt])
				else:
					hotTemp = numpy.append(hotTemp,tempNdviIgual[0])
				tempNdviIgual = None
		ndvi_aux = None
		tempSuperficie = None
		hotTemp = numpy.sort(hotTemp)
		coldTemp = numpy.sort(coldTemp)
		TH = numpy.mean(hotTemp[-3:])
		TC = numpy.mean(coldTemp[:3])
		self.fracaoEvaporativa = numpy.choose(self.mask, (self.valores.noValue, (TH - self.temperaturaSuperficie) / (TH - TC)))
		
		
class SSEBI():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'S-SEBI','self.fracaoEvaporativaSSEBI(i, j, lerLinhas, lerColunas)\nself.fracao()')
		self.a.setFullSize()
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
		
class SSEBI_Block():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'S-SEBI_Block','self.fracaoEvaporativaSSEBI(i, j, lerLinhas, lerColunas)\nself.fracao()')
		self.a.setBlockSize(256,256)
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
		
class SSEB():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'SSEB', 'self.fracaoEvaporativaSSEB()')
		self.a.setFullSize()
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
			

if __name__== '__main__': 
	inicio = time.time()
	#Instancia-se o algoritmo desejado e passa parâmetros

	Ta = 32.74
	UR = 36.46
	Z = 50.24
	julianDay = 248.0
	
	a = SSEBI('empilhada1000x1000.tif', Ta, UR, Z, julianDay)
	fim = time.time()
	print 'Tempo total: '+str(fim - inicio)+' segundos.'
	
	inicio = time.time()
	a = SSEBI_Block('empilhada1000x1000.tif', Ta, UR, Z, julianDay)
	fim = time.time()
	print 'Tempo total: '+str(fim - inicio)+' segundos.'
	
	inicio = time.time()
	a = SSEB('empilhada1000x1000.tif', Ta, UR, Z, julianDay)
	fim = time.time()
	print 'Tempo total: '+str(fim - inicio)+' segundos.'
