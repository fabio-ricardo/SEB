import gdal
from gdalconst import *
import sys,os,math,time
import numpy
from numpy import *

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
k2 = 1896
k3 = 1554
k4 = 1036
k5 = 215.0

k7 = 80.67

#Angulo zenital (90 graus - elevacao)
angle = (43*math.pi)/180

#Razao Dist. entre Terra-Sol (212 dia sequencial)
d = 1+0.033*math.cos((2*math.pi*212)/365)

#altitude do pixel(m)
z = 250

#Temperatura do ar(K)
Ta = 280

#radiacao de onda curta incidente
Rsol_inc = 1367*math.cos(angle)*(0.75 +0.00002*z)*d

#radiacao de onda longa incidente
Ea = 0.85 * math.pow(-1*math.log((0.75 +0.00002*z)),0.09)
Rol_atm = Ea * 0.0000000567 * Ta*Ta*Ta*Ta

#Abrindo imagem empilhada e separando as bandas
nomeFile = 'mergido.tiff'
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
	outDataSet = driver.Create('ResultadosProcessamento-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float64)
	outBand = outDataSet.GetRasterBand(1)
	outBand.WriteArray(arq,0,0)
	outDataSet = None
	
#Pontos p/ lim superior e inferior
l1 =[]
l2 =[]
x1 = 0.1
x2 = 0.9
y1 =0
y2 =0

y3 =0
y4 =0

	
#Radiancia e reflectancia
banda = img.GetRasterBand(1).ReadAsArray()
L1 = a1 + ((b1 - a1)/255)* banda
P1 = (math.pi * L1)/(k1 * math.cos(angle)*d)
banda = None
AlPlan = 0.293*P1
L1 = None
P1 = None

banda = img.GetRasterBand(2).ReadAsArray()
L2 = a2 + ((b2 - a2)/255)* banda
P2 = (math.pi * L2)/(k2 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.274*P2
L2 = None
P2 = None

banda = img.GetRasterBand(3).ReadAsArray()
L3 = a3 + ((b3 - a3)/255)* banda
P3 = (math.pi * L3)/(k3 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.233*P3
L3 = None

banda = img.GetRasterBand(4).ReadAsArray()		
L4 = a4 + ((b4 - a4)/255)* banda
P4 = (math.pi * L4)/(k4 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan+ 0.157*P4
L4 = None


banda = img.GetRasterBand(5).ReadAsArray()
L5 = a5 + ((b5 - a5)/255)* banda
P5 = (math.pi * L5)/(k5 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.033*P5
L5 = None
P5 = None

banda = img.GetRasterBand(6).ReadAsArray()
L6 = a6 + ((b6 - a6)/255)* banda
banda = None

banda = img.GetRasterBand(7).ReadAsArray()
L7 = a7 + ((b7 - a7)/255)* banda
P7 = (math.pi * L7)/(k7 * math.cos(angle)*d)
banda = None
img = None
AlPlan = AlPlan+ 0.011*P7
L7 = None
P7 = None

#Albedo superficie(deve-se imprimir em porcentagem)
AlSuper = (AlPlan - 0.03)* (1/((0.75 +0.00002*z)*(0.75 +0.00002*z)))
AlPlan = None
EscreveResult(AlSuper,'AlbedoSuperficie.tif')

#Temperatura satelite (K)
T = 1260.56/(numpy.log((607.76/L6) +1))
EscreveResult(T,'Temperatura.tif')

'''
#Teste para limites
rows, cols = AlSuper.shape
for i in range(0,rows):
	for j in range(0,cols):
		if AlSuper[i,j] <= 0.2:
			l1.append(T[i,j])
				
		elif AlSuper[i,j] >= 0.75:
			l2.append(T[i,j])

#Encontrando pontos lSup(x1,y1) (x2,y2) e lInf(x1,y3) (x2,y4)
l1.sort()
l2.sort()
for i in range(len(l1) -10, len(l1)):
	y1 += l1[i] 
y1 /= 10

for i in range(0,10):
	y3 += l1[i]
y3 /= 10

for i in range(len(l2) -10, len(l2)):
	y2 += l2[i]
y2 /= 10

for i in range(0,10):
	y4 += l2[i]
y4 /= 10

#Coeficientes das retas
m1 = (y2-y1)/(x2-x1)
m2 = (y4-y3)/(x2-x1)
c1 = (x2*y1 - x1*y2)/(x2-x1)
c2 = (x2*y3 - x1*y4)/(x2-x1)'''

#indice de Vegetacao da Diferenca Normalizada
NDVI = (P4 - P3) / (P4+ P3)	
EscreveResult(NDVI,'NDVI.tif')
	
#indice de Vegetacao Ajustado para os Efeitos do Solo
SAVI = ((1+0.5)*(P4-P3))/(0.5+P4+P3)
EscreveResult(SAVI,'SAVI.tif')
P4 = None
P3 = None

#Indice area foliar
IAF = ((numpy.log((0.69 - SAVI)/0.59))/0.91) * (-1) #MUDARR!!!!
EscreveResult(IAF,'IAF.tif')
SAVI = None
IAF = None
'''	
#radiacao de onda longa emitida 
Rol_emit= 0.0000000567*T*T*T*T		
L = 0.607 * Rol_emit + 170.405

#temperatura radiativa da superficie
T0_R  = math.sqrt(math.sqrt(L/0.0000000567))	#MUDARR!!!

#Correcao da temperatura radiativa
Pv = (NDVI - 0.1)/(0.8 - 0.1) 					#MUDARR!!
E0 = 0.99 * Pv + 0.91*(1 - Pv) + 4*0.02*Pv*(1 - Pv)
T0 = math.pow(math.pow(T0_R,4)/E0,0.25)
		
#radiacao de onda longa emitida atualizado
Rol_emit= E0*0.0000000567*T0*T0*T0*T0
		
#Saldo da radiacao
Rn = Rsol_inc*(1-AlSuper) + Rol_atm - Rol_emit	
		
#Fluxo de calor no solo	
G = ((T0 - 273.15)*(0.32 + (0.62*AlSuper))*(1-0.978*math.pow(NDVI,2)))*Rn
		
#fracao evaporativa
V_virado = (c1 + m1*AlSuper) - T0/(c1 - c2 + (m1 - m2)*AlSuper)
#Fluxo calor sensivel
H = (1- V_virado)*(Rn - G)
		
#Fluxo calor latente
LE = V_virado * (Rn - G)'''

fim = time.time()
print 'Tempo total: '+str(fim - inicio)
