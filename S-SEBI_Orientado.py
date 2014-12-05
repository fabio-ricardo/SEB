#coding: utf-8
import gdal, osgeo, time, numpy, sys, math, os
from gdalconst import *
from constantes_MODIS import *
#Pega os dados da imagem
class AbreImagem():
	
	def tif(self):
		self.entrada = gdal.Open(self.nomeArquivoEntrada,GA_ReadOnly)
		self.setLinhas(self.entrada.RasterYSize)
		self.setColunas(self.entrada.RasterXSize)
	
	def hdf(self):
		aux = gdal.Open(self.nomeArquivoEntrada)
		subdatasets = numpy.array(aux.GetSubDatasets())
		a1, a2 = subdatasets.shape
		
		for n in xrange(a1):
			if '1km Surface Reflectance Band' in subdatasets[n][0]:
				b = gdal.Open(subdatasets[n][0], GA_ReadOnly)
				b = b.GetRasterBand(1).ReadAsArray().astype(numpy.float32)
				rows, cols = b.shape
				self.setLinhas(rows)
				self.setColunas(cols)
				b = None
				break
		self.entrada = self.driver.Create(self.pastaSaida+self.nomeArquivoEntrada,cols,rows,self.NBandas+6,GDT_Float32)
		for k in xrange(n,n+7):
			#print 'Extraindo banda: ',k-n+1
			banda = self.entrada.GetRasterBand(k-n+1)
			saida = gdal.Open(subdatasets[k][0], GA_ReadOnly)
			banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
			saida = None
			banda = None
		for n in xrange(a1):
			if subdatasets[n][0][-3:] == ':31':
				#print 'Extraindo banda: 31'
				banda = self.entrada.GetRasterBand(8)
				saida = gdal.Open(subdatasets[n][0], GA_ReadOnly)
				banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
				#print 'Extraindo banda: 32'
				banda = self.entrada.GetRasterBand(9)
				saida = gdal.Open(subdatasets[n+1][0], GA_ReadOnly)
				banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
				break
			elif subdatasets[n][0][-3:] == ':17':
				#print 'Extraindo banda: 17'
				banda = self.entrada.GetRasterBand(10)
				saida = gdal.Open(subdatasets[n][0], GA_ReadOnly)
				banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
				#print 'Extraindo banda: 18'
				banda = self.entrada.GetRasterBand(11)
				saida = gdal.Open(subdatasets[n+1][0], GA_ReadOnly)
				banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
				#print 'Extraindo banda: 19'
				banda = self.entrada.GetRasterBand(12)
				saida = gdal.Open(subdatasets[n+2][0], GA_ReadOnly)
				banda.WriteArray(saida.GetRasterBand(1).ReadAsArray().astype(numpy.float32),0,0)
				n += 3
			
	def __init__(self,nomeArquivoEntrada, algNome):
		self.nomeArquivoEntrada = nomeArquivoEntrada
		self.pastaSaida = algNome+'__'+nomeArquivoEntrada+'/'
		
		try:
			os.mkdir(self.pastaSaida)
		except:
			print 'Diretorio: ' + self.pastaSaida + ' Já existe.'
			print 'Recriando arquivos, se existir.'
		self.NBandas = 7
		self.driver = gdal.GetDriverByName('GTiff')
		self.driver.Register()
		self.extensao = '.tif'
		
		exec('self.'+nomeArquivoEntrada[-3:]+'()')
		
		if  self.entrada is None:
			print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
			sys.exit(1)
		
		print 'linhas:',self.getLinhas(),' colunas:',self.getColunas(),'bandas:',self.getBandas(),'driver:',self.getDriverEntrada().ShortName
	
	def getEntrada(self):
		return self.entrada
	
	
	def setLinhas(self, rows):
		self.rows = rows
	
	def setColunas(self, cols):
		self.cols = cols
	
	def getLinhas(self):
		return self.rows
	
	def getColunas(self):
		return self.cols
	
	def getDriverEntrada(self):
		return self.entrada.GetDriver()
	
	def getBandas(self):
		return self.NBandas
	
	def getProjecao(self):	
		return self.entrada.GetProjection()
	
	def criaImagem(self,nome, linhas, colunas):
		saida = self.driver.Create(self.pastaSaida+nome+self.extensao,colunas, linhas,1,GDT_Float32)
		if saida is None:
			print 'Erro ao criar o arquivo: ' + nome+self.extensao
			sys.exit(1)
		saida.SetProjection(self.getProjecao())
		return saida, saida.GetRasterBand(1)
	
	def saidaImagem(self,nome, banda, saida, calculo,i, j):
		'''
		saida2 = self.driver.Create(self.pastaSaida+nome+'_'+self.extensao,self.getColunas(), self.getLinhas(),1,GDT_Float32)
		saida2.SetProjection(self.getProjecao())
		band2 = saida2.GetRasterBand(1)
			
		band2.WriteArray(calculo, j , i)
		band2.SetNoDataValue(Valores.noValue)
		if os.path.exists(self.pastaSaida+nome+self.extensao):
			os.remove(self.pastaSaida+nome+self.extensao)
		'''
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
	def __init__(self, nome, algNome,fracao, fracao2):
		self.img = AbreImagem(nome, algNome)	
		self.linhas = self.img.getLinhas()
		self.colunas = self.img.getColunas()
		self.fracao = fracao
		self.fracao2 = fracao2
		
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
		formulas = Formulas( Ta, UR, Z, julianDay, self.img)
		formulas.setBandasSaida(self.saidaNDVI,self.bandaNDVI, self.saidaSAVI, self.bandaSAVI, self.saidaIAF,self.bandaIAF, self.saidaAlbedo, 
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
				formulas.fazCalculos(self.fracao, self.fracao2, i, j, lerLinhas, lerColunas)
				self.img.saidaImagem('ndvi', self.bandaNDVI, self.saidaNDVI,formulas.getNDVI(), i, j)
				self.img.saidaImagem('savi', self.bandaSAVI, self.saidaSAVI,formulas.getSAVI(), i, j)
				self.img.saidaImagem('iaf', self.bandaIAF, self.saidaIAF, formulas.getIAF(), i, j)
				self.img.saidaImagem('albedoSuperficie', self.bandaAlbedoSuper, self.saidaAlbedo, formulas.getAlbedoSuper(), i, j)
				
				self.img.saidaImagem('temperaturaSuperficie',self.bandaTempSuper,self.saidaTemp, formulas.getTemperaturaSuperficie(), i, j)
				self.img.saidaImagem('saldoRadiacao', self.bandaSaldoRad, self.saidaRad, formulas.getSaldoRadiacao(), i, j)
				self.img.saidaImagem('fluxoCalSolo', self.bandaFluxo, self.saidaFluxo, formulas.getFluxoCalSolo(), i, j)
				
				self.img.saidaImagem('fracaoEvaporativa', self.bandaFracao, self.saidaFracao, formulas.getFracaoEvaporativa(), i, j)

				self.img.saidaImagem('fluxoCalorSensivel', self.bandaCalSen, self.saidaCalSen, formulas.getFluxoCalorSensivel(), i,j )
				self.img.saidaImagem('fluxoCalorLatente', self.bandaCalLat, self.saidaCalLat, formulas.getFluxoCalorLatente(), i,j)
				self.img.saidaImagem('evapotranspiração24h',self.bandaEvap,self.saidaEvap, formulas.getEvapotranspiracao24h(), i,j)
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
		if os.path.exists(self.img.pastaSaida+self.img.nomeArquivoEntrada):
			os.remove(self.img.pastaSaida+self.img.nomeArquivoEntrada)
		img = None
		formulas = None
		
	def setBlockSize(self, yBlockSize, xBlockSize):
		self.xBlockSize = xBlockSize
		self.yBlockSize = yBlockSize
		
	def setFullSize(self):
		self.xBlockSize = self.img.getColunas()
		self.yBlockSize = self.img.getLinhas()

#Todas as fórmulas utilizadas
class Formulas():
	def __init__(self, Ta, UR, Z, julianDay, img):
		 self.valores = Valores()
		 self.valores.setTa(Ta)
		 self.valores.setUR(UR)
		 self.valores.setZ(Z)
		 self.valores.setJulianDay(julianDay)
		 self.albedoSupMax = 0
		 self.img = img
		 
	
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
			if (k != 6) or self.img.nomeArquivoEntrada[-3:].lower() == 'hdf':
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

			if(k != 6) or self.img.nomeArquivoEntrada[-3:].lower()== 'hdf':
				reflectancia = self.p1[k] * radiancia

				self.albedoPlanetario += descBandas[k][7] * reflectancia

				radiancia = None

				if(k == 3):
					self.reflectanciaB3 = reflectancia
				elif(k == 4):
					self.reflectanciaB4 = reflectancia
				elif(k == 1):
					self.reflectanciaB1 = reflectancia
				elif (k==2):
					self.reflectanciaB2 = reflectancia
				reflectancia = None
			else:
				self.radianciaB6 = radiancia
				radiancia = None
			
		self.mask = numpy.choose(self.mask,(True,False))
		valueOff = None
		dados = None
		#self.entrada = None
	
	def fazCalculos(self, fracao, fracao2,i, j, lerLinhas, lerColunas):	

		exec('self.setNdvi'+self.img.nomeArquivoEntrada[-3:].lower()+'()')
		self.setSavi()
		self.setIaf()
		self.albedoSuper()
		self.enb_e_e0()
		exec('self.tempSuper'+self.img.nomeArquivoEntrada[-3:].lower()+'('+str(i)+','+str(j)+','+str(lerLinhas)+','+str(lerColunas)+')')
		self.setSaldoRadiacao()
		self.setFluxoCalSolo()
		exec(fracao+'('+str(i)+','+str(j)+','+str(lerLinhas)+','+str(lerColunas)+')')
		exec(fracao2)
	
	def setNdvihdf(self):
		self.ndvi = numpy.choose(self.mask, (self.valores.noValue, (self.reflectanciaB2 - self.reflectanciaB1) / (self.reflectanciaB2 + self.reflectanciaB1)))
	
	def setNdvitif(self):
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
		
	def tempSupertif(self, i, j,lerLinhas, lerColunas):
		self.temperaturaSuperficie = numpy.choose(self.mask, (self.valores.noValue, self.valores.K2 / numpy.log(((self.ENB * self.valores.K1) / self.radianciaB6) + 1.0)))
		self.radianciaB6 = None
		self.ENB = None
	
	def tempSuperhdf(self, i,j ,lerLinhas, lerColunas):
		numpy.seterr(all='ignore')
		#Radiancia
		T31 =  -1.3250003015 + ((26.2000005725+1.3250003015)/32767)*self.img.entrada.GetRasterBand(8).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		T32 =  -1.2099998176 + ((22.7000145484+1.2099998176)/32767)*self.img.entrada.GetRasterBand(9).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		G17 = -2.4265276381 + ((248.4159162245+2.4265276381)/32767)*self.img.entrada.GetRasterBand(10).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		G18 = -2.8239951529 + ((289.1066775101+2.8239951529)/32767)*self.img.entrada.GetRasterBand(11).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		G19 = -2.2822969783 + ((233.6502935587+2.2822969783)/32767)*self.img.entrada.GetRasterBand(12).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		G2  = 0 + ((326.828903877-0)/32767)*self.img.entrada.GetRasterBand(2).ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
		
		#Temperatura
		T31 = 1304.4/(numpy.log((self.ENB*729.57/T31)+1))
		T32 = 1197.0/(numpy.log((self.ENB*474.71/T32)+1))
		G17 = G17/G2
		G18 = G18/G2
		G19 = G19/G2
		
		self.driver = gdal.GetDriverByName('GTiff')
		self.driver.Register()
		'''
		saida = self.driver.Create('temp31.tif',1354,2030,1,GDT_Float32)
		banda = saida.GetRasterBand(1)
		banda.WriteArray(T31,0,0)
		
		saida = self.driver.Create('temp31.tif',1354,2030, 1,GDT_Float32)
		banda = saida.GetRasterBand(1)
		banda.WriteArray(T31,0,0)'''
		
		
		W17 = 26.314 - 54.434*G17 + 28.449*G17*G17
		W18 = 5.012 - 23.017*G18 + 27.884*G18*G18
		W19 = 9.446 - 26.887*G19 + 19.914*G19*G19
		
		W = 0.192*W17 + 0.453*W18 + 0.355*W19
		e = (0.989+0.988)/2
		de = 0.989 - 0.988
		
		#Split das temperaturas
		self.temperaturaSuperficie = 0.97 + 0.13*W + (1.0 + (0.112 + 0.006*W)*((1 - e)/e) + (-0.52 + 0.02*W)*(de/(e*e)))*((T31+T32)/2) + (9.98 -0.32*W + (-36.15 -0.42*W)*((1-e)/e) + (130.8 -10.72*W)*(de/(e*e)))*((T31-T32)/2)
		self.radianciaB6 = None
		self.ENB = None
		numpy.seterr(all='warn')
	
	def getTemperaturaSuperficie(self):
		return self.temperaturaSuperficie
	
	def radOndaLongaEmi(self):
		return numpy.power(self.temperaturaSuperficie,4)*(self.E0 * self.valores.constSB)
		
		
	def setSaldoRadiacao(self):
		self.saldoRadiacao = numpy.choose(self.mask, (self.valores.noValue, (self.E0 * self.valores.radOndaLongaInci - self.radOndaLongaEmi()) + ((1.0 - self.albedoSuperficie) * self.valores.radOndaCurtaInci)))
		
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
		albedoSuperficie = self.getAlbedoSuper()
		temperaturaSuperficie = self.getTemperaturaSuperficie()
		maskAlbedoSuper = numpy.logical_and(albedoSuperficie <= (self.albedoSupMax * 0.2), albedoSuperficie != self.valores.noValue)
		limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]
		maskAlbedoSuper = albedoSuperficie >= (self.albedoSupMax * 0.8)
		limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]
		maskAlbedoSuper = None
		albedoSuperficie = None
		temperaturaSuperficieSaida = None
		
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
		
		self.fracaoEvaporativa = numpy.choose(self.mask, (self.valores.noValue, (c1 + (m1 * self.getAlbedoSuper()) - self.getTemperaturaSuperficie())/((c1 - c2) + ((m1 - m2) * self.getAlbedoSuper()))))

	def fracaoEvaporativaSSEB(self, *args):
		hotNdvi = numpy.array([],dtype=numpy.float32)
		coldTemp = numpy.array([],dtype=numpy.float32)
		coldNdvi = numpy.array([],dtype=numpy.float32)
		hotTemp = numpy.array([],dtype=numpy.float32)
		tempSuperficie = self.getTemperaturaSuperficie()
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
		self.fracaoEvaporativa = numpy.choose(self.mask, (self.valores.noValue, (TH - self.getTemperaturaSuperficie()) / (TH - TC)))
		
		
class SSEBI():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'S-SEBI','self.fracaoEvaporativaSSEBI', 'self.fracao()')
		self.a.setFullSize()
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
		
class SSEBI_Block():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'S-SEBI_Block','self.fracaoEvaporativaSSEBI','self.fracao()')
		self.a.setBlockSize(256,256)
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
		
class SSEB():
	def __init__(self,nome, Ta, UR, Z, julianDay):
		self.a = SalvaImagens(nome, 'SSEB', 'self.fracaoEvaporativaSSEB', '\n')
		self.a.setFullSize()
		self.a.EscreveTudo(Ta, UR, Z, julianDay)
			

if __name__== '__main__': 
	inicio = time.time()
	#Instancia-se o algoritmo desejado e passa parâmetros
	numpy.seterr(all='ignore')
	
	Ta = 32.74
	UR = 36.46
	Z = 50.24
	julianDay = 248.0
	nome = 'MOD09.A2014332.0915.005.NRT.hdf'
	#nome = 'empilhada1000x1000.tif'
	a = SSEBI(nome, Ta, UR, Z, julianDay)
	fim = time.time()
	print 'Tempo total: '+str(fim - inicio)+' segundos.'
	'''
	inicio = time.time()
	a = SSEBI_Block(nome, Ta, UR, Z, julianDay)
	fim = time.time()
	print 'Tempo total: '+str(fim - inicio)+' segundos.'
	
	inicio = time.time()
	a = SSEB(nome, Ta, UR, Z, julianDay)
	fim = time.time()
	
	numpy.seterr(all='warn')
	print 'Tempo total: '+str(fim - inicio)+' segundos.'''
