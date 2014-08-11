
#coding: utf-8
import gdal
from gdalconst import *
import sys,os,math,time, random
import numpy as np
from constantes import *

gdal.AllRegister()
driver = gdal.GetDriverByName('GTiff')
a = open('resultados.txt','w+')
#Radiancias espectrais min. e max. em cada banda(surface albedo)
a1 = -1.52
b1 = 193.0

a2 = -2.84
b2 = 365.0

a3 = -1.17
b3 = 264.0

a4 = -1.51
b4 = 221.0

a5 = -0.37
b5 = 30.2

a6 = 1.2378
b6 = 15.303

a7 = -0.15
b7 = 16.5

#Irradiancia solar espectral em cada banda
k1 = 1957
k2 = 1826
k3 = 1554
k4 = 1036
k5 = 215.0

k7 = 80.67

#Angulo zenital
angle = (90 -56.98100422)*math.pi/180

#Razao Dist. entre Terra-Sol (272 dia sequencial)
d = 1+0.033*math.cos((2*math.pi*272)/365)

#altitude do pixel(m)
z = 200

#Temperatura do ar(K)
Ta = 295

#radiacao de onda longa incidente
tsw = (0.75 +0.00002*z)
Ea = 0.85 * math.pow(-1*math.log(tsw),0.09)
Rol_atm = Ea * 0.0000000567 * math.pow(Ta,4)

#Radiacao onda curta incidente
Rs = 1367 * math.cos(angle)*tsw * d

Tao_24h=0.63
Rg_24h=243.95

def semNumpy(imagem):
	inicio = time.time()
	
	#Abrindo imagem empilhada e separando as bandas
	nomeFile = imagem
	img = gdal.Open(nomeFile,GA_ReadOnly)
	if img is None:
		print 'Nao foi possivel abrir a imagem.'
		sys.exit(1)



	colunas = img.RasterXSize #pega o numero de colunas
	linhas = img.RasterYSize #pega o numero de linhas
	
	#Cria pasta para os resultados
	try:
		os.mkdir('ResultadosProcessamento-'+nomeFile)
	except:
		print 'Diretorio Já existe.'
		print 'Recriando arquivos.'
	

	#Funcao para escrever imagem
	def EscreveResult(arq, nome):
		outDataSet = driver.Create('ResultadosProcessamento-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float32)
		outBand = outDataSet.GetRasterBand(1)
		vet = np.array(arq)
		outBand.WriteArray(vet,0,0)
		outDataSet = None

	#Radiancia e reflectancia

	banda3 = img.GetRasterBand(3).ReadAsArray()
	banda4 = img.GetRasterBand(4).ReadAsArray()

	L3 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P3 = [[0 for x in range(colunas)] for x in range(linhas)] 
	L4 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P4 = [[0 for x in range(colunas)] for x in range(linhas)] 
	NDVI = [[0 for x in range(colunas)] for x in range(linhas)] 
	SAVI = [[0 for x in range(colunas)] for x in range(linhas)] 
	AlPlan = [[0 for x in range(colunas)] for x in range(linhas)] 
	IAF =[[0 for x in range(colunas)] for x in range(linhas)] 


	for i in xrange(0,linhas):
		for j in xrange(0,colunas):
			if banda3[i][j] != 0 and banda4[i][j] != 0:		
				L3[i][j] = a3 + ((b3 - a3)/255)* banda3[i][j]
				L4[i][j] = a4 + ((b4 - a4)/255)* banda4[i][j]
			
				P3[i][j] = (math.pi * L3[i][j])/(k3 * math.cos(angle)*d)		
				P4[i][j] = (math.pi * L4[i][j])/(k4 * math.cos(angle)*d)
	
				#indice de Vegetacao da Diferenca Normalizada
				NDVI[i][j] = (P4[i][j] - P3[i][j]) / (P4[i][j]+ P3[i][j])

				#indice de Vegetacao Ajustado para os Efeitos do Solo
				SAVI[i][j] = ((1+0.5)*(P4[i][j]-P3[i][j]))/(0.5+P4[i][j]+P3[i][j])
				AlPlan[i][j] = 0.233*P3[i][j] + 0.157*P4[i][j]
			
				#Indice area foliar
				if (0.69 - SAVI[i][j])/0.59 > 0:
					IAF[i][j]= (math.log((0.69 - SAVI[i][j])/0.59))/0.91 * (-1)
				else:
					IAF[i][j] = None


	L3 = None
	P3 = None
	L4 = None
	P4 = None	
	EscreveResult(NDVI,'NDVI.tif')
	EscreveResult(SAVI,'SAVI.tif')
	EscreveResult(IAF,'IAF.tif')
	SAVI = None

	Enb = [[0 for x in xrange(colunas)] for x in xrange(linhas)] 
	E0 = [[0 for x in xrange(colunas)] for x in xrange(linhas)] 

	for i in xrange(0,linhas):
		for j in xrange(0,colunas):
			if banda3[i][j] != 0 and banda4[i][j] != 0:

				#Emissividade
				if IAF[i][j] != None:
					if NDVI[i][j] >0 and IAF[i][j] <3:
							Enb[i][j] = 0.97 + 0.00331* IAF[i][j]
							E0[i][j] = 0.95 + 0.01 * IAF[i][j]
					elif IAF[i][j] >=3:
						Enb[i][j] = 0.98
						E0[i][j] = 0.98
					elif NDVI[i][j] <0:
						Enb[i][j] = 0.99
						E0[i][j] = 0.985	
					else:
						Enb[i][j] = None
						E0[i][j] = None
			


	L1 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P1 = [[0 for x in range(colunas)] for x in range(linhas)] 
	L2 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P2 = [[0 for x in range(colunas)] for x in range(linhas)] 
	L6 = [[0 for x in range(colunas)] for x in range(linhas)] 
	T = [[0 for x in range(colunas)] for x in range(linhas)] 

	banda1 = img.GetRasterBand(1).ReadAsArray()
	banda2 = img.GetRasterBand(2).ReadAsArray()
	banda6 = img.GetRasterBand(6).ReadAsArray()

	for i in xrange(0,linhas):
		for j in xrange(0,colunas):
			if banda1[i][j] != 0 and banda2[i][j] != 0 and banda6[i][j] != 0:		
				L1[i][j] = a1 + ((b1 - a1)/255)* banda1[i][j]
				P1[i][j] = (math.pi * L1[i][j])/(k1 * math.cos(angle)*d)

				L2[i][j] = a2 + ((b2 - a2)/255)* banda2[i][j]
				P2[i][j] = (math.pi * L2[i][j])/(k2 * math.cos(angle)*d)
						
				L6[i][j] = a6 + ((b6 - a6)/255)* banda6[i][j]
			
				#Temperatura satelite (K)
				if Enb[i][j] != None and L6[i][j] != 0 and (Enb[i][j]*607.76/L6[i][j]) +1 > 0 and (math.log((Enb[i][j]*607.76/L6[i][j]) +1) != 0) :
					T[i][j] = 1260.56/(math.log((Enb[i][j]*607.76/L6[i][j]) +1))
				else:
					T[i][j] = None
				AlPlan[i][j] = AlPlan[i][j] + 0.293*P1[i][j] + 0.274*P2[i][j] 
	banda1 = None
	banda2 = None
	banda6 = None
	L1 = None
	P1 = None
	L2 = None
	P2 = None
	L6 = None
	Enb = None

	L5 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P5 = [[0 for x in range(colunas)] for x in range(linhas)] 
	AlSuper = [[0 for x in range(colunas)] for x in range(linhas)] 	
	L7 = [[0 for x in range(colunas)] for x in range(linhas)] 
	P7 = [[0 for x in range(colunas)] for x in range(linhas)] 

	banda5 = img.GetRasterBand(5).ReadAsArray()
	banda7 = img.GetRasterBand(7).ReadAsArray()
	img = None
	x2 = -99
	for i in xrange(0,linhas):
		for j in xrange(0,colunas):
			if banda5[i][j]!= 0 and banda7[i][j] != None:				
						
				L5[i][j] = a5 + ((b5 - a5)/255)* banda5[i][j]
				P5[i][j] =(math.pi * L5[i][j])/(k5 * math.cos(angle)*d)
			
				L7[i][j] = a7 + ((b7 - a7)/255)* banda7[i][j]		
				P7[i][j] = (math.pi * L7[i][j])/(k7 * math.cos(angle)*d)
			
				AlPlan[i][j] = AlPlan[i][j] + 0.033*P5[i][j] +  0.011*P7[i][j]
			
				#Albedo superficie(deve-se imprimir em porcentagem)
				AlSuper[i][j] = (AlPlan[i][j] - 0.03)/(tsw*tsw)
			
				#Pegar o maior albedo p/ o limite
				if (AlSuper[i][j] > x2):
					x2 = AlSuper[i][j]
			else:
				AlSuper[i][j] = None
	banda5 = None
	banda7 = None
	L5 = None
	P5 = None				
	L7 = None
	P7 = None
	AlPlan = None

	Rn = [[0 for x in range(colunas)] for x in range(linhas)] 
	G = [[0 for x in range(colunas)] for x in range(linhas)] 
	Frt_emit = [[0 for x in range(colunas)] for x in range(linhas)] 

	for i in xrange(0,linhas):
		for j in xrange(0,colunas):
			if AlSuper[i][j] != None:	
			
				#fluxo radiacao termal emitida
				if E0[i][j] != None and T[i][j] != None:
					Frt_emit[i][j] = E0[i][j]*0.0000000567*math.pow(T[i][j],4)
				else:
					Frt_emit[i][j] = None
			
				#Saldo da radiacao
				if AlSuper[i][j] != None and Frt_emit[i][j] != None :
					Rn[i][j] = (1 - AlSuper[i][j])*Rs + Rol_atm - Frt_emit[i][j] - (1 - E0[i][j])*Rol_atm
				else:
					Rn[i][j] = None

				#Fluxo de calor no solo
				if AlSuper[i][j] != None and T[i][j] != None and Rn[i][j] != None and NDVI[i][j] != None:
					G[i][j] = ((T[i][j] - 273.15)*(0.0038 + (0.0074*AlSuper[i][j]))*(1-0.98*math.pow(NDVI[i][j],4)))*Rn[i][j]
				else:
					G[i][j] = None

	E0 = None
	NDVI = None

	EscreveResult(AlSuper,'AlbedoSuperficie.tif')
	EscreveResult(T,'Temperatura.tif')
	EscreveResult(Rn,'SaldoRadiacao.tif')
	EscreveResult(G,'FluxoDeCalorNoSolo.tif')
	Frt_emit = None

	x1 = 0.1

	limLadoEsq = []
	limLadoDir = []

	for i in xrange(0,linhas):
		for i in xrange(0,colunas):
			if AlSuper[i][j] != None and T[i][j] != None:
				if AlSuper[i][j] <= (x2*0.2) :
					limLadoEsq.append(T[i][j])
				elif AlSuper[i][j] >= (x2*0.8):
					limLadoDir.append(T[i][j])

	#Pontos p/ lim superior e inferior
	limLadoEsq.sort()
	limLadoDir.sort()

	y1 = y2 = y3 = y4 =0
	if len(limLadoDir) > 20:
		for i in xrange(0,20):
			y4 += limLadoDir[i]
		for i in xrange(len(limLadoDir) -20, len(limLadoDir)):
			y2 += limLadoDir[i]
		y2 /= 5
		y4 /= 5
	else:
		if len(limLadoDir) >0:
			y2 =limLadoDir[-1]
			y4 =limLadoDir[0]
		else:
			y2 = 320
			y4 = 260
	if len(limLadoEsq) >20:	
		for i in xrange(0,20):
			y3 += limLadoEsq[i]
		for i in xrange(len(limLadoEsq) -20, len(limLadoEsq)):
			y1 += limLadoEsq[i]
	
		y1 /= 5
		y3 /= 5
	else:	
		if len(limLadoEsq) >0:
			y1 = limLadoEsq[-1]
			y3 = limLadoEsq[0]
		else:
			y1 = 300
			y3 = 290
			
	LE = [[0 for x in range(colunas)] for x in range(linhas)] 
	Rn_24h = [[0 for x in range(colunas)] for x in range(linhas)] 
	H = [[0 for x in range(colunas)] for x in range(linhas)] 
	V_virado = [[0 for x in range(colunas)] for x in range(linhas)] 
	LE_24h = [[0 for x in range(colunas)] for x in range(linhas)] 
	ET_24h = [[0 for x in range(colunas)] for x in range(linhas)] 

	#Coeficientes das retas
	m1 = (y2-y1)/(x2-x1)
	m2 = (y4-y3)/(x2-x1)
	c1 = (x2*y1 - x1*y2)/(x2-x1)
	c2 = (x2*y3 - x1*y4)/(x2-x1)

	for i in xrange(0,linhas):
		for i in xrange(0,colunas):
			if AlSuper[i][j] != None :
				#fracao evaporativa
				if T[i][j] != None:
					V_virado[i][j] = ((c1 + m1*AlSuper[i][j]) - T[i][j])/(c1 - c2 + (m1 - m2)*AlSuper[i][j])
				else:
					V_virado[i][j] = None
				if V_virado[i][j] != None and Rn[i][j] != None and G[i][j] != None:
					#Fluxo calor sensivel
					H[i][j] = (1- V_virado[i][j])*(Rn[i][j] - G[i][j])

					#Fluxo calor latente
					LE[i][j] = V_virado[i][j] * (Rn[i][j] - G[i][j])
				else:
					H[i][j] = None
					LE[i][j] = None
			
				#Saldo radiação diário
				Rn_24h[i][j] = Rg_24h * (1.0 - AlSuper[i][j]) - 110.0 * Tao_24h
				if V_virado[i][j] != None:
					LE_24h[i][j] = V_virado[i][j] * Rn_24h[i][j]
					ET_24h[i][j] = (V_virado[i][j] * Rn_24h[i][j] * 86.4) / 2450.0
				else:
					LE_24h[i][j] = None
					ET_24h[i][j] = None

	AlSuper = None
	T = None	
	G = None
	Rn = None
		
	EscreveResult(V_virado,'FracaoEvaporativa.tif')
	EscreveResult(H,'FluxoCalorSensivel.tif')
	EscreveResult(LE,'FluxoCalorLatente.tif')
	EscreveResult(Rn_24h,'RN24H.tif')
	EscreveResult(LE_24h,'LE24h.tif')
	EscreveResult(ET_24h,'EvapotranspiraçãoDiaria.tif')

	V_virado = None
	H = None
	LE = None
	Rn_24h = None
	LE_24h = None
	ET_24h = None
	fim = time.time()
	a.write(str(fim - inicio)+'/n')


def comNumpy(nomeArquivoEntrada):
	inicio = time.time()

	entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)
	if  entrada is None:
		print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
		sys.exit(1)

	linhas = entrada.RasterYSize
	colunas = entrada.RasterXSize
	NBandas = entrada.RasterCount
	driverEntrada = entrada.GetDriver()
	projecao = entrada.GetProjection()

	print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driverEntrada.ShortName

#----------

	extensao = '.tif'

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

	p1 = numpy.empty([NBandas+1],dtype=numpy.float32)
	p1[0] = 0
	p1[6] = 0

	#----------

	for k in range(1,NBandas+1):
		if (k != 6):
			p1[k] = pi / (descBandas[k][5] * cosZ * dr)

#----------

	pastaSaida = 'S-SEBI__'+nomeArquivoEntrada+'/'

	try:
		os.mkdir(pastaSaida)
	except:
		print 'Diretorio: ' + pastaSaida + ' Já existe.'
		print 'Recriando arquivos, se existir.'

#----------

	dados = numpy.zeros([NBandas+1,linhas,colunas],dtype=numpy.float32)

#----------

	albedoPlanetario = 0

	for k in range(1,NBandas+1):
		dados[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
		radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])

		if(k >= 2):
			if(k == 2):
				noDataValue = entrada.GetRasterBand(k-1).GetNoDataValue()

				#valueOff = 
				valueOff = 0.0
				print valueOff

				#if(valueOff.size > 0):
				mask = numpy.logical_and(dados[k-1] != valueOff, dados[k-1] != noDataValue)
				#else:
				#    mask = dados[k-1] != noDataValue

				dados[k-1] = None

			noDataValue = entrada.GetRasterBand(k).GetNoDataValue()

			#if(valueOff.size > 0):
			mask = numpy.logical_and(mask, dados[k] != valueOff)

			mask = numpy.logical_and(mask, dados[k] != noDataValue)

			dados[k] = None

		if(k != 6):
			reflectancia = p1[k] * radiancia

			albedoPlanetario += descBandas[k][7] * reflectancia

			radiancia = None

			if(k == 3):
				reflectanciaB3 = reflectancia
			elif(k == 4):
				reflectanciaB4 = reflectancia

			reflectancia = None
		else:
			radianciaB6 = radiancia
			radiancia = None

#----------

	dados = None
	entrada = None

#----------

	def saidaImagem(nome, calculo):
		saida = driver.Create(pastaSaida+nome+extensao,colunas,linhas,1,GDT_Float32)
		if saida is None:
			print 'Erro ao criar o arquivo: ' + nome+extensao
			sys.exit(1)

		saida.SetProjection(projecao)
		banda = saida.GetRasterBand(1)

		banda.WriteArray(calculo,0,0)

		banda.SetNoDataValue(noValue)

		banda = None
		saida = None

		print nome + ' - Pronto!'

#----------

	ndvi = numpy.choose(mask, (noValue, (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)))

	saidaImagem('ndvi',ndvi)

#----------

	savi = numpy.choose(mask, (noValue, ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))))
	
	saidaImagem('savi',savi)

	reflectanciaB4 = None
	reflectanciaB3 = None

#----------

	numpy.seterr(all='ignore')

#----------

	mask1 = numpy.logical_and(((0.69 - savi) / 0.59) > 0, mask)

	iaf = numpy.choose(mask1, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))

	saidaImagem('iaf',iaf)

	mask1 = None

#----------

	numpy.seterr(all='warn')

#----------

	albedoSuperficie = numpy.choose(mask, (noValue, (albedoPlanetario - ap) * p2))

	saidaImagem('albedoSuperficie',albedoSuperficie)

	albedoPlanetario = None

#----------

	mask1 = savi <= 0.1

	iaf = numpy.choose(mask1,(iaf, 0.0))

	mask1 = savi >= 0.687

	iaf = numpy.choose(mask1,(iaf, 6.0))

	ENB = 0.97 + 0.0033 * iaf
	E0 = 0.95 + 0.01 * iaf

	mask1 = iaf >= 3

	ENB = numpy.choose(mask1, (ENB, 0.98))
	E0 = numpy.choose(mask1, (E0, 0.98))

	mask1 = ndvi <= 0

	ENB = numpy.choose(mask1, (ENB, 0.99))
	E0 = numpy.choose(mask1, (E0, 0.985))

	mask1 = None
	savi = None
	iaf = None

#----------

	temperaturaSuperficie = numpy.choose(mask, (noValue, K2 / numpy.log(((ENB * K1) / radianciaB6) + 1.0)))

	saidaImagem('temperaturaSuperficie',temperaturaSuperficie)

	radianciaB6 = None
	ENB = None

	#----------

	radOndaLongaEmi = (E0 * constSB) * numpy.power(temperaturaSuperficie,4)

	saldoRadiacao = numpy.choose(mask, (noValue, ((1.0 - albedoSuperficie) * radOndaCurtaInci) +\
                                    (E0 * radOndaLongaInci - radOndaLongaEmi)))

	saidaImagem('saldoRadiacao',saldoRadiacao)

	E0 = None
	radOndaLongaEmi = None

	#----------

	mask1 = ndvi < 0

	fluxoCalSolo = numpy.choose(mask1, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1.0 - (0.98 * numpy.power(ndvi,4)))) * saldoRadiacao, G))

	mask1 = None

	fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))

	saidaImagem('fluxoCalSolo',fluxoCalSolo)

	ndvi = None

	#----------

	albedoSupMax = numpy.amax(albedoSuperficie)

	maskAlbedoSuper = numpy.logical_and(albedoSuperficie <= (albedoSupMax * 0.2), albedoSuperficie != noValue)
	limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]

	maskAlbedoSuper = albedoSuperficie >= (albedoSupMax * 0.8)
	limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]

	maskAlbedoSuper = None

	mask1 = limiteLadoEsq != noValue
	limiteLadoEsq = limiteLadoEsq[mask1]

	mask1 = limiteLadoDir != noValue
	limiteLadoDir = limiteLadoDir[mask1]

	mask1 = None

	limiteLadoEsq = numpy.sort(limiteLadoEsq)
	limiteLadoDir = numpy.sort(limiteLadoDir)

	limSupEsq = limiteLadoEsq[::-1][0:qtdPontos]
	limInfEsq = limiteLadoEsq[0:qtdPontos]

	limSupDir = limiteLadoDir[::-1][0:qtdPontos]
	limInfDir = limiteLadoDir[0:qtdPontos]

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

	fracaoEvaporativa = numpy.choose(mask, (noValue, (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie)\
										/ ((c1 - c2) + ((m1 - m2) * albedoSuperficie))))

	saidaImagem('fracaoEvaporativa',fracaoEvaporativa)

	temperaturaSuperficie = None

	#----------

	fluxoCalorSensivel = numpy.choose(mask, (noValue, (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)))

	saidaImagem('fluxoCalorSensivel',fluxoCalorSensivel)

	fluxoCalorSensivel = None

	#----------

	fluxoCalorLatente = numpy.choose(mask, (noValue, fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)))

	saidaImagem('fluxoCalorLatente',fluxoCalorLatente)

	#----------

	evapotranspiracao24h = numpy.choose(mask, (noValue, (fracaoEvaporativa * (Rg24h * (1.0 - albedoSuperficie)\
                                                    - 110.0 * Tao24h) * 86.4) / 2450.0))

	saidaImagem('evapotranspiracao24h',evapotranspiracao24h)

	mask = None
	evapotranspiracao24h = None
	fluxoCalorLatente = None
	fracaoEvaporativa = None
	fluxoCalSolo = None
	saldoRadiacao = None
	albedoSuperficie = None
	fim = time.time()
	a.write(str(fim - inicio)+'/n')


	#----------
l = ['empilhada1000x1000.tif','empilhada2000x2000.tif','empilhada3000x3000.tif','empilhada4000x4000.tif','empilhada5000x5000.tif','empilhada6000x6000.tif','empilhada7001x8001.tif']
for i in range(0,6):
		semNumpy(l[i]);
		comNumpy(l[i]);
		print l[i] + ' - PRONTO'
a.close()
