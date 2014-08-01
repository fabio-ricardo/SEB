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

#Cria pasta para os resultados
os.mkdir('ResultadosProcessamento-'+nomeFile)

#Funcao para escrever imagem
def EscreveResult(arq, nome):
	outDataSet = driver.Create('ResultadosProcessamento-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float32)
	outBand = outDataSet.GetRasterBand(1)
	outBand.WriteArray(arq,0,0)
	outDataSet = None

#Radiancia e reflectancia

banda1 = img.GetRasterBand(1).ReadAsArray()
banda2 = img.GetRasterBand(2).ReadAsArray()
banda3 = img.GetRasterBand(3).ReadAsArray()
banda4 = img.GetRasterBand(4).ReadAsArray()
banda5 = img.GetRasterBand(5).ReadAsArray()
banda6 = img.GetRasterBand(6).ReadAsArray()
banda7 = img.GetRasterBand(7).ReadAsArray()
img = None


print ('Parte 1')


L3 = [[] for x in xrange(colunas)] 
P3 = [[] for x in xrange(colunas)] 
L4 = [[] for x in xrange(colunas)] 
P4 = [[] for x in xrange(colunas)] 
NDVI = [[] for x in xrange(colunas)] 
SAVI = [[] for x in xrange(colunas)] 
AlPlan = [[] for x in xrange(colunas)] 
IAF =[[] for x in xrange(colunas)] 


for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i][j] == banda2[i][j] == banda3[i][j] == banda4[i][j] == banda5[i][j] == banda6[i][j] == banda7[i][j]):		
			L3[i].append( a3 + ((b3 - a3)/255)* banda3[i][j])
			P3[i].append( (math.pi * L3[i][j])/(k3 * math.cos(angle)*d))

			L4[i].append( a4 + ((b4 - a4)/255)* banda4[i][j])
			P4[i].append( (math.pi * L4[i][j])/(k4 * math.cos(angle)*d))	
	
			#indice de Vegetacao da Diferenca Normalizada
			NDVI[i].append( (P4[i][j] - P3[i][j]) / (P4[i][j]+ P3[i][j]))

			#indice de Vegetacao Ajustado para os Efeitos do Solo
			SAVI[i].append( ((1+0.5)*(P4[i][j]-P3[i][j]))/(0.5+P4[i][j]+P3[i][j]))
			AlPlan[i].append( 0,233*P3[i][j] + 0,157*P4[i][j])
			
			#Indice area foliar
			if (0.69 - SAVI[i][j])/0.59 > 0:
				IAF[i].append((math.log((0.69 - SAVI[i][j])/0.59))/0.91 * (-1))
			else:
				IAF[i].append(None)
L3 = None
P3 = None
L4 = None
P4 = None	
EscreveResult(NDVI,'NDVI.tif')
EscreveResult(SAVI,'SAVI.tif')
EscreveResult(IAF,'IAF.tif')
IAF = None
SAVI = None
	
Enb = [[] for x in xrange(colunas)] 
E0 = [[] for x in xrange(colunas)] 

for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i][j] == banda2[i][j] == banda3[i][j] == banda4[i][j] == banda5[i][j] == banda6[i][j] == banda7[i][j]):		

			#Emissividade
			if IAF[i][j] != None:
				if NDVI[i][j] >0 and IAF[i][j] <3:
					Enb[i].append(0.97 + 0.00331* IAF[i][j])
					E0[i].append( 0.95 + 0.01 * IAF[i][j])
				elif IAF >=3:
					Enb[i].append(0.98)
					E0[i].append(0.98)
				elif NDVI <0:
					Enb[i].append(0.99)
					E0[i].append(0.985)  	
			else:
				Enb[i].append(None)
				E0[i].append(None)
			




L1 = [[] for x in xrange(colunas)] 
P1 = [[] for x in xrange(colunas)] 
L2 = [[] for x in xrange(colunas)] 
P2 = [[] for x in xrange(colunas)] 
L6 = [[] for x in xrange(colunas)] 
T = [[] for x in xrange(colunas)] 

for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i][j] == banda2[i][j] == banda3[i][j] == banda4[i][j] == banda5[i][j] == banda6[i][j] == banda7[i][j]):		
			L1[i].append(a1 + ((b1 - a1)/255)* banda1[i][j])
			P1[i].append((math.pi * L1[i][j])/(k1 * math.cos(angle)*d))

			L2[i].append(a2 + ((b2 - a2)/255)* banda2[i][j])
			P2[i].append((math.pi * L2[i][j])/(k2 * math.cos(angle)*d))
						
			L6[i].append(a6 + ((b6 - a6)/255)* banda6[i][j])
			
			#Temperatura satelite (K)
			if Enb[i][j] != None and (Enb[i][j]*607.76/L6[i][j]) +1 >0 :
				T[i].append(1260.56/(math.log((Enb[i][j]*607.76/L6[i][j]) +1)))
			else:
				T[i].append(None)
			AlPlan[i][j] = AlPlan + 0,293*P1[i][j] + 0,274*P2[i][j] 

	print i
L1 = None
P1 = None
L2 = None
P2 = None
L6 = None
Enb = None

L5 = [[] for x in xrange(colunas)] 
P5 = [[] for x in xrange(colunas)] 
AlSuper = [[] for x in xrange(colunas)] 	
L7 = [[] for x in xrange(colunas)] 
P7 = [[] for x in xrange(colunas)] 

for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i][j] == banda2[i][j] == banda3[i][j] == banda4[i][j] == banda5[i][j] == banda6[i][j] == banda7[i][j]):				
						
			L5[i].append(a5 + ((b5 - a5)/255)* banda5[i][j])
			P5[i].append((math.pi * L5[i][j])/(k5 * math.cos(angle)*d))
			
			L7[i].append( a7 + ((b7 - a7)/255)* banda7[i][j])		
			P7[i].append((math.pi * L7[i][j])/(k7 * math.cos(angle)*d))
			
			AlPlan[i][j] = AlPlan + 0,033*P5[i][j] +  0,011*P7[i][j]
			
			#Albedo superficie(deve-se imprimir em porcentagem)
			AlSuper[i].append((AlPlan[i][j] - 0.03)/(tsw*tsw))
			
			#Pegar o maior albedo p/ o limite
			if AlSuper[i][j] > x2 :
				x2 = AlSuper[i][j]
		else:
			AlSuper[i].append(None)
L5 = None
P5 = None				
L7 = None
P7 = None
AlPlan = None

Rn = [[] for x in xrange(colunas)] 
G = [[] for x in xrange(colunas)] 
Frt_emit = [[] for x in xrange(colunas)] 

for i in range(0,linhas):
	for j in range(0,colunas):
		if not(banda1[i][j] == banda2[i][j] == banda3[i][j] == banda4[i][j] == banda5[i][j] == banda6[i][j] == banda7[i][j]):	
			
			#fluxo radiacao termal emitida
			if E0[i][j] != None and T[i][j] != None:
				Frt_emit[i].append(E0[i][j]*0.0000000567*math.pow(T[i][j],4))
			else:
				Frt_emit[i].append(None)
			
			#Saldo da radiacao
			if AlSuper[i][j] != None and Frt_emit[i][j] != None :
				Rn[i].append((1 - AlSuper[i][j])*Rs + Rol_atm - Frt_emit[i][j] - (1 - E0[i][j])*Rol_atm)
			else:
				Rn[i].append(None)

			#Fluxo de calor no solo
			if AlSuper[i][j] != None and T[i][j] != None and Rn[i][j] != None and NDVI[i][j] != None:
				G[i].append(((T[i][j] - 273.15)*(0.0038 + (0.0074*AlSuper))*(1-0.98*math.pow(NDVI[i][j],4)))*Rn[i][j])
			else:
				G[i].append(None)

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
for i in range(0, linhas):
	for i in range(0, colunas):
		if AlSuper[i][j] != None and T[i][j] != None:
			if AlSuper[i][j] <= (x2*0.2) :
				limLadoEsq.append(T[i][j])
			elif AlSuper[i][j] >= (x2*0.8):
				limLadoDir.append(T[i][j])

#Pontos p/ lim superior e inferior
limLadoEsq.sort()
limLadoDir.sort()

y1 = y2 = y3 = y4 =0

for i in range(0,20):
	y3 += limLadoEsq[i][j]
	y4 += limLadoDir[i][j]
	
for i in range(len(limiteLadoDir) -20, len(limiteLadoDir)):
	y2 += limLadoDir[i][j]
for i in range(len(limiteLadoEsq) -20, len(limiteLadoEsq)):
	y1 += limiteLadoEsq
	
y1 /= 20
y3 /= 20
y2 /= 20
y4 /= 20



LE = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 
Rn_24h = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 
H = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 
V_virado = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 
LE_24h = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 
ET_24h = [[0 for x in xrange(linhas)] for x in xrange(colunas)] 

#Coeficientes das retas
m1 = (y2-y1)/(x2-x1)
m2 = (y4-y3)/(x2-x1)
c1 = (x2*y1 - x1*y2)/(x2-x1)
c2 = (x2*y3 - x1*y4)/(x2-x1)
print ('Parte 4')

for i in range(0, linhas):
	for i in range(0,colunas):
		if AlSuper[i][j] != None :
			#fracao evaporativa
			if T[i][j] != None:
				V_virado[i].append(((c1 + m1*AlSuper[i][j]) - T[i][j])/(c1 - c2 + (m1 - m2)*AlSuper[i][j]))
			else:
				V_virado[i].append(None)
			if V_virado[i][j] != None and Rn[i][j] != None and G[i][j] != None:
				#Fluxo calor sensivel
				H[i].append((1- V_virado[i][j])*(Rn[i][j] - G[i][j]))

				#Fluxo calor latente
				LE[i].append(V_virado[i][j] * (Rn[i][j] - G[i][j]))
			else:
				H[i].append(None)
				LE[i].append(None)
			
			#Saldo radiação diário
			Rn_24h[i].append(Rg_24h * (1.0 - AlSuper[i][j]) - 110.0 * Tao_24h)
			if V_virado[i][j] != None:
				LE_24h[i].append(V_virado[i][j] * Rn_24h[i][j])
				ET_24h[i].append((V_virado[i][j] * Rn_24h[i][j] * 86.4) / 2450.0)
			else:
				LE_24h[i].append(None)
				ET_24h[i].append(None)
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
