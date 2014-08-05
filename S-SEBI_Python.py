#coding: utf-8
import gdal
from gdalconst import *
import sys,os,math,time
import numpy as np
inicio = time.time()

gdal.AllRegister()
driver = gdal.GetDriverByName('GTiff')

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

#Abrindo imagem empilhada e separando as bandas
nomeFile = 'empilhada.tif'
img = gdal.Open(nomeFile,GA_ReadOnly)
if img is None:
	print 'Nao foi possivel abrir a imagem.'
	sys.exit(1)



colunas = img.RasterXSize #pega o numero de colunas
linhas = img.RasterYSize #pega o numero de linhas
colunas = linhas = 1000
#Cria pasta para os resultados
os.mkdir('ResultadosProcessamento-'+nomeFile)

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



print ('Parte 1')
a = time.time()

L3 = [[0 for x in range(colunas)] for x in range(linhas)] 
P3 = [[0 for x in range(colunas)] for x in range(linhas)] 
L4 = [[0 for x in range(colunas)] for x in range(linhas)] 
P4 = [[0 for x in range(colunas)] for x in range(linhas)] 
NDVI = [[0 for x in range(colunas)] for x in range(linhas)] 
SAVI = [[0 for x in range(colunas)] for x in range(linhas)] 
AlPlan = [[0 for x in range(colunas)] for x in range(linhas)] 
IAF =[[0 for x in range(colunas)] for x in range(linhas)] 
b = time.time()

print str(b-a)
colunas = linhas = 5000
for i in xrange(4000,linhas):
	for j in xrange(4000,colunas):
		if banda3[i][j] != 0 and banda4[i][j] != 0:		
			L3[i-4000][j-4000] = a3 + ((b3 - a3)/255)* banda3[i][j]
			L4[i-4000][j-4000] = a4 + ((b4 - a4)/255)* banda4[i][j]
			
			P3[i-4000][j-4000] = (math.pi * L3[i-4000][j-4000])/(k3 * math.cos(angle)*d)		
			P4[i-4000][j-4000] = (math.pi * L4[i-4000][j-4000])/(k4 * math.cos(angle)*d)
	
			#indice de Vegetacao da Diferenca Normalizada
			NDVI[i-4000][j-4000] = (P4[i-4000][j-4000] - P3[i-4000][j-4000]) / (P4[i-4000][j-4000]+ P3[i-4000][j-4000])

			#indice de Vegetacao Ajustado para os Efeitos do Solo
			SAVI[i-4000][j-4000] = ((1+0.5)*(P4[i-4000][j-4000]-P3[i-4000][j-4000]))/(0.5+P4[i-4000][j-4000]+P3[i-4000][j-4000])
			AlPlan[i-4000][j-4000] = 0.233*P3[i-4000][j-4000] + 0.157*P4[i-4000][j-4000]
			
			#Indice area foliar
			if (0.69 - SAVI[i-4000][j-4000])/0.59 > 0:
				IAF[i-4000][j-4000]= (math.log((0.69 - SAVI[i-4000][j-4000])/0.59))/0.91 * (-1)
			else:
				IAF[i-4000][j-4000] = None


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

for i in xrange(4000,linhas):
	for j in xrange(4000,colunas):
		if banda3[i][j] != 0 and banda4[i][j] != 0:

			#Emissividade
			if IAF[i-4000][j-4000] != None:
				if NDVI[i-4000][j-4000] >0 and IAF[i-4000][j-4000] <3:
						Enb[i-4000][j-4000] = 0.97 + 0.00331* IAF[i-4000][j-4000]
						E0[i-4000][j-4000] = 0.95 + 0.01 * IAF[i-4000][j-4000]
				elif IAF[i-4000][j-4000] >=3:
					Enb[i-4000][j-4000] = 0.98
					E0[i-4000][j-4000] = 0.98
				elif NDVI[i-4000][j-4000] <0:
					Enb[i-4000][j-4000] = 0.99
					E0[i-4000][j-4000] = 0.985	
				else:
					Enb[i-4000][j-4000] = None
					E0[i-4000][j-4000] = None
			


L1 = [[0 for x in range(colunas)] for x in range(linhas)] 
P1 = [[0 for x in range(colunas)] for x in range(linhas)] 
L2 = [[0 for x in range(colunas)] for x in range(linhas)] 
P2 = [[0 for x in range(colunas)] for x in range(linhas)] 
L6 = [[0 for x in range(colunas)] for x in range(linhas)] 
T = [[0 for x in range(colunas)] for x in range(linhas)] 

banda1 = img.GetRasterBand(1).ReadAsArray()
banda2 = img.GetRasterBand(2).ReadAsArray()
banda6 = img.GetRasterBand(6).ReadAsArray()

for i in xrange(4000,linhas):
	for j in xrange(4000,colunas):
		if banda1[i][j] != 0 and banda2[i][j] != 0 and banda6[i][j] != 0:		
			L1[i-4000][j-4000] = a1 + ((b1 - a1)/255)* banda1[i][j]
			P1[i-4000][j-4000] = (math.pi * L1[i-4000][j-4000])/(k1 * math.cos(angle)*d)

			L2[i-4000][j-4000] = a2 + ((b2 - a2)/255)* banda2[i][j]
			P2[i-4000][j-4000] = (math.pi * L2[i-4000][j-4000])/(k2 * math.cos(angle)*d)
						
			L6[i-4000][j-4000] = a6 + ((b6 - a6)/255)* banda6[i][j]
			
			#Temperatura satelite (K)
			if Enb[i-4000][j-4000] != None and L6[i-4000][j-4000] != 0 and (Enb[i-4000][j-4000]*607.76/L6[i-4000][j-4000]) +1 > 0 and (math.log((Enb[i-4000][j-4000]*607.76/L6[i-4000][j-4000]) +1) != 0) :
				T[i-4000][j-4000] = 1260.56/(math.log((Enb[i-4000][j-4000]*607.76/L6[i-4000][j-4000]) +1))
			else:
				T[i-4000][j-4000] = None
			AlPlan[i-4000][j-4000] = AlPlan[i-4000][j-4000] + 0.293*P1[i-4000][j-4000] + 0.274*P2[i-4000][j-4000] 
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
x2 = -1
for i in xrange(4000,linhas):
	for j in xrange(4000,colunas):
		if banda5[i][j]!= 0 and banda7[i][j] != None:				
						
			L5[i-4000][j-4000] = a5 + ((b5 - a5)/255)* banda5[i][j]
			P5[i-4000][j-4000] =(math.pi * L5[i-4000][j-4000])/(k5 * math.cos(angle)*d)
			
			L7[i-4000][j-4000] = a7 + ((b7 - a7)/255)* banda7[i][j]		
			P7[i-4000][j-4000] = (math.pi * L7[i-4000][j-4000])/(k7 * math.cos(angle)*d)
			
			AlPlan[i-4000][j-4000] = AlPlan[i-4000][j-4000] + 0.033*P5[i-4000][j-4000] +  0.011*P7[i-4000][j-4000]
			
			#Albedo superficie(deve-se imprimir em porcentagem)
			AlSuper[i-4000][j-4000] = (AlPlan[i-4000][j-4000] - 0.03)/(tsw*tsw)
			
			#Pegar o maior albedo p/ o limite
			if (AlSuper[i-4000][j-4000] > x2):
				x2 = AlSuper[i-4000][j-4000]
		else:
			AlSuper[i-4000][j-4000] = None
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

for i in xrange(4000,linhas):
	for j in xrange(4000,colunas):
		if AlSuper[i-4000][j-4000] != None:	
			
			#fluxo radiacao termal emitida
			if E0[i-4000][j-4000] != None and T[i-4000][j-4000] != None:
				Frt_emit[i-4000][j-4000] = E0[i-4000][j-4000]*0.0000000567*math.pow(T[i-4000][j-4000],4)
			else:
				Frt_emit[i-4000][j-4000] = None
			
			#Saldo da radiacao
			if AlSuper[i-4000][j-4000] != None and Frt_emit[i-4000][j-4000] != None :
				Rn[i-4000][j-4000] = (1 - AlSuper[i-4000][j-4000])*Rs + Rol_atm - Frt_emit[i-4000][j-4000] - (1 - E0[i-4000][j-4000])*Rol_atm
			else:
				Rn[i-4000][j-4000] = None

			#Fluxo de calor no solo
			if AlSuper[i-4000][j-4000] != None and T[i-4000][j-4000] != None and Rn[i-4000][j-4000] != None and NDVI[i-4000][j-4000] != None:
				G[i-4000][j-4000] = ((T[i-4000][j-4000] - 273.15)*(0.0038 + (0.0074*AlSuper[i-4000][j-4000]))*(1-0.98*math.pow(NDVI[i-4000][j-4000],4)))*Rn[i-4000][j-4000]
			else:
				G[i-4000][j-4000] = None

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
print ('Parte 3')
for i in xrange(4000,linhas):
	for i in xrange(4000,colunas):
		if AlSuper[i-4000][j-4000] != None and T[i-4000][j-4000] != None:
			if AlSuper[i-4000][j-4000] <= (x2*0.2) :
				limLadoEsq.append(T[i-4000][j-4000])
			elif AlSuper[i-4000][j-4000] >= (x2*0.8):
				limLadoDir.append(T[i-4000][j-4000])

#Pontos p/ lim superior e inferior
limLadoEsq.sort()
limLadoDir.sort()

y1 = y2 = y3 = y4 =0

for i in xrange(0,5):
	y3 += limLadoEsq[i]
	y4 += limLadoDir[i]
	
for i in xrange(len(limLadoDir) -5, len(limLadoDir)):
	y2 += limLadoDir[i]
for i in xrange(len(limLadoEsq) -5, len(limLadoEsq)):
	y1 += limLadoEsq[i]
	
y1 /= 5
y3 /= 5
y2 /= 5
y4 /= 5



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
print ('Parte 4')

for i in xrange(4000,linhas):
	for i in xrange(4000,colunas):
		if AlSuper[i-4000][j-4000] != None :
			#fracao evaporativa
			if T[i-4000][j-4000] != None:
				V_virado[i-4000][j-4000] = ((c1 + m1*AlSuper[i-4000][j-4000]) - T[i-4000][j-4000])/(c1 - c2 + (m1 - m2)*AlSuper[i-4000][j-4000])
			else:
				V_virado[i-4000][j-4000] = None
			if V_virado[i-4000][j-4000] != None and Rn[i-4000][j-4000] != None and G[i-4000][j-4000] != None:
				#Fluxo calor sensivel
				H[i-4000][j-4000] = (1- V_virado[i-4000][j-4000])*(Rn[i-4000][j-4000] - G[i-4000][j-4000])

				#Fluxo calor latente
				LE[i-4000][j-4000] = V_virado[i-4000][j-4000] * (Rn[i-4000][j-4000] - G[i-4000][j-4000])
			else:
				H[i-4000][j-4000] = None
				LE[i-4000][j-4000] = None
			
			#Saldo radiação diário
			Rn_24h[i-4000][j-4000] = Rg_24h * (1.0 - AlSuper[i-4000][j-4000]) - 110.0 * Tao_24h
			if V_virado[i-4000][j-4000] != None:
				LE_24h[i-4000][j-4000] = V_virado[i-4000][j-4000] * Rn_24h[i-4000][j-4000]
				ET_24h[i-4000][j-4000] = (V_virado[i-4000][j-4000] * Rn_24h[i-4000][j-4000] * 86.4) / 2450.0
			else:
				LE_24h[i-4000][j-4000] = None
				ET_24h[i-4000][j-4000] = None
print ('Parte 5')
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
print 'Tempo total: '+str(fim - inicio)
