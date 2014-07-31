#coding: utf-8
import gdal
from gdalconst import *
import sys,os,math,time

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

#Abrindo imagem empilhada e separando as bandas
nomeFile = 'empilhada.tif'
img = gdal.Open(nomeFile,GA_ReadOnly)
if img is None:
	print 'Nao foi possivel abrir a imagem.'
	sys.exit(1)


colunas = img.RasterXSize #pega o numero de colunas
linhas = img.RasterYSize #pega o numero de linhas

#Cria pasta para os resultados
os.mkdir('ResultadosProcessamento-'+nomeFile)

#Funcao para escrever imagem
def EscreveResult(arq, nome):
	outDataSet = driver.Create('ResultadosProcessamento-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float32)
	outBand = outDataSet.GetRasterBand(1)
	outBand.WriteArray(arq,0,0)
	outDataSet = None

#Radiancia e reflectancia

banda1 = img.GetRasterBand(1)
banda2 = img.GetRasterBand(2)
banda3 = img.GetRasterBand(3)
banda4 = img.GetRasterBand(4)
banda5 = img.GetRasterBand(5)
banda6 = img.GetRasterBand(6)
banda7 = img.GetRasterBand(7)
img = None
print ('Parte 1')
for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i,j] = banda2[i,j] = banda3[i,j] = banda4[i,j] = banda5[i,j] = banda6[i,j] = banda7[i,j]):		
			L1[i,j] = a1 + ((b1 - a1)/255)* banda1[i,j]
			P1[i,j] = (math.pi * L1)/(k1 * math.cos(angle)*d)

			L2[i,j] = a2 + ((b2 - a2)/255)* banda2[i,j]
			P2[i,j] = (math.pi * L2)/(k2 * math.cos(angle)*d)

			L3[i,j] = a3 + ((b3 - a3)/255)* banda3[i,j]
			P3[i,j] = (math.pi * L3)/(k3 * math.cos(angle)*d)

			L4[i,j] = a4 + ((b4 - a4)/255)* banda4[i,j]
			P4[i,j] = (math.pi * L4)/(k4 * math.cos(angle)*d)

			L5[i,j] = a5 + ((b5 - a5)/255)* banda5[i,j]
			P5[i,j] = (math.pi * L5)/(k5 * math.cos(angle)*d)

			L6[i,j] = a6 + ((b6 - a6)/255)* banda6[i,j]

			L7[i,j] = a7 + ((b7 - a7)/255)* banda7[i,j]
			P7[i,j] = (math.pi * L7)/(k7 * math.cos(angle)*d)

			AlPlan[i,j] = 0,293*P1[i,j] + 0,274*P2[i,j] + 0,233*P3[i,j] + 0,157*P4[i,j]+ 0,033*P5[i,j] + 0,011*P7[i,j]

			#Albedo superficie(deve-se imprimir em porcentagem)
			AlSuper[i,j] = (AlPlan[i,j] - 0.03)/(tsw*tsw)
			
			#Pegar o maior albedo p/ o limite
			if AlSuper[i,j] > x2 :
				x2 = AlSuper[i,j]

			#indice de Vegetacao da Diferenca Normalizada
			NDVI[i,j] = (P4[i,j] - P3[i,j]) / (P4[i,j]+ P3[i,j])

			#indice de Vegetacao Ajustado para os Efeitos do Solo
			SAVI[i,j] = ((1+0.5)*(P4[i,j]-P3[i,j]))/(0.5+P4[i,j]+P3[i,j])

			#Indice area foliar
			IAF[i,j] = (math.log((0.69 - SAVI[i,j])/0.59))/0.91 * (-1)
		
			#Emissividade
			if NDVI[i,j] >0 and IAF[i,j] <3:
				Enb[i,j] = 0.97 + 0.00331* IAF[i,j]
				E0[i,j] = 0.95 + 0.01 * IAF[i,j]
			elif IAF >=3:
				Enb[i,j] = 0.98
				E0[i,j] = 0.98
			elif NDVI <0:
				Enb[i,j] = 0.99
				E0[i,j] = 0.985  

			#Temperatura satelite (K)
			T[i,j] = 1260.56/(math.log((Enb[i,j]*607.76/L6[i,j]) +1))
		
			#fluxo radiacao termal emitida
			Frt_emit[i,j]= E0[i,j]*0.0000000567*math.pow(T[i,j],4)

			#Saldo da radiacao
			Rn[i,j] = (1 - AlSuper[i,j])*Rs + Rol_atm - Frt_emit[i,j] - (1 - E0[i,j])*Rol_atm
			
			#Fluxo de calor no solo
			G[i,j] = ((T[i,j] - 273.15)*(0.0038 + (0.0074*AlSuper))*(1-0.98*math.pow(NDVI[i,j],4)))*Rn[i,j]
		else:
			AlSuper = None
print ('Parte 2')
L1 = None
P1 = None
L2 = None
P2 = None
L3 = None
P3 = None
L4 = None
P4 = None
L5 = None
P5 = None
L6 = None
L7 = None
P7 = None
AlPlan = None
Enb = None
E0 = None
Frt_emit = None

EscreveResult(AlSuper,'AlbedoSuperficie.tif')
EscreveResult(NDVI,'NDVI.tif')
EscreveResult(SAVI,'SAVI.tif')
EscreveResult(IAF,'IAF.tif')
EscreveResult(T,'Temperatura.tif')
EscreveResult(Rn,'SaldoRadiacao.tif')
EscreveResult(G,'FluxoDeCalorNoSolo.tif')

NDVI = None
IAF = None
SAVI = None

x1 = 0.1

limLadoEsq = []
limLadoDir = []
print ('Parte 3')
for i in range(0, linhas):
	for i in range(0, colunas):
		if AlSuper != None:
			if AlSuper[i,j] <= (x2*0.2) :
				limLadoEsq.append(T[i,j])
			elif AlSuper[i,j] >= (x2*0.8):
				limLadoDir.append(T[i,j])

#Pontos p/ lim superior e inferior
limLadoEsq.sort()
limLadoDir.sort()

y1 = y2 = y3 = y4 =0

for i in range(0,20):
	y3 += limLadoEsq[i,j]
	y4 += limLadoDir[i,j]
	
for i in range(limiteLadoDir.length -20, limiteLadoDir.length):
	y2 += limLadoDir[i,j]
for i in range(limiteLadoEsq.length -20, limiteLadoEsq.length):
	y1 += limiteLadoEsq
	
y1 /= 20
y3 /= 20
y2 /= 20
y4 /= 20

#Coeficientes das retas
m1 = (y2-y1)/(x2-x1)
m2 = (y4-y3)/(x2-x1)
c1 = (x2*y1 - x1*y2)/(x2-x1)
c2 = (x2*y3 - x1*y4)/(x2-x1)
print ('Parte 4')
for i in range(0, linhas):
	for i in range(0,colunas):
		if AlSuper != None :
			#fracao evaporativa
			V_virado[i,j] = ((c1 + m1*AlSuper[i,j]) - T[i,j])/(c1 - c2 + (m1 - m2)*AlSuper[i,j])

			#Fluxo calor sensivel
			H[i,j] = (1- V_virado[i,j])*(Rn[i,j] - G[i,j])

			#Fluxo calor latente
			LE[i,j] = V_virado[i,j] * (Rn[i,j] - G[i,j])
print ('Parte 5')
AlSuper = None
T = None			
EscreveResult(V_virado,'FracaoEvaporativa.tif')
EscreveResult(H,'FluxoCalorSensivel.tif')
EscreveResult(LE,'FluxoCalorLatente.tif')
G = None
Rn = None
V_virado = None
H = None
LE = None

fim = time.time()
print 'Tempo total: '+str(fim - inicio)
