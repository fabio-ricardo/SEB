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
k2 = 1826
k3 = 1554
k4 = 1036
k5 = 215.0

k7 = 80.67

#Angulo zenital (90 graus - elevacao)
angle = (90 - 43)*math.pi/180

#Razao Dist. entre Terra-Sol (212 dia sequencial)
d = 1+0.033*math.cos((2*math.pi*212)/365)

#altitude do pixel(m)
z = 250

#Temperatura do ar()
Ta = 25

#Velocidade do vento(m/s)
u2 = 2.77

#Umidade relativa (%)
UR = 50

#radiacao de onda longa incidente
Ea = 0.85 * math.pow(-1*math.log((0.75 +0.00002*z)),0.09)
Rol_atm = Ea * 0.0000000567 * math.pow(Ta +273.15,4)

#Abrindo imagem empilhada
nomeFile = 'empilhada.tif'
img = gdal.Open(nomeFile,GA_ReadOnly)
if img is None:
	print 'Nao foi possivel abrir a imagem.'
	sys.exit(1)

colunas = img.RasterXSize #pega o numero de colunas
linhas = img.RasterYSize #pega o numero de linhas

#Cria pasta para os resultados
os.mkdir('SSEB Resultados-'+nomeFile)

#Funcao para escrever imagem
def EscreveResult(arq, nome):
	outDataSet = driver.Create('SSEB Resultados-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float64)
	outBand = outDataSet.GetRasterBand(1)
	outBand.WriteArray(arq,0,0)
	outDataSet = None
	
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

#indice de Vegetacao da Diferenca Normalizada
NDVI = (P4 - P3) / (P4+ P3)	
EscreveResult(NDVI,'NDVI.tif')
	
#indice de Vegetacao Ajustado para os Efeitos do Solo
SAVI = ((1+0.5)*(P4-P3))/(0.5+P4+P3)
P4 = None
P3 = None

#Indice area foliar
IAF = (numpy.log((0.69 - SAVI)/ 0.59)/0.91) * (-1) 
SAVI = None

#Emissividade
Enb = 0.97 + 0.00331* IAF
E0 = 0.95 + 0.01 * IAF
IAF = None

#Temperatura satelite (K)
T = 1260.56/(numpy.log((Enb*607.76/L6) +1))
L6 = None
Enb = None
EscreveResult(T,'Temperatura.tif')

#fluxo radiacao termal emitida 
Frt_emit= E0*0.0000000567*T*T*T*T		

#Radiacao onda curta incidente
Rs = 1367 * math.cos(angle)*(0.75 +0.00002*z)*d
		
#Saldo da radiacao
Rn = (1 - AlSuper)*Rs + Rol_atm - Frt_emit - (1 - E0)*Rol_atm
Frt_emit = None
E0 = None
EscreveResult(Rn,'SaldoRadiacao.tif')

#Fluxo de calor no solo	
G = ((T - 273.15)*(0.0038 + (0.0074*AlSuper))*(1-0.98*numpy.power(NDVI,4)))*Rn
AlSuper = None
EscreveResult(G,'FluxoDeCalorNoSolo.tif')

#Encontrando 3 pixels ancoras quentes e frios

THot1 = np.amin(T)
THot2 = np.amin(T)
THot3 = np.amin(T)

TCold1 = np.amax(T)
TCold2 = np.amax(T)
TCold3 = np.amax(T)

NDVIHot1 = np.amax(NDVI)
NDVIHot2 = np.amax(NDVI)
NDVIHot3 = np.amax(NDVI)

NDVICold1 = np.amin(NDVI)
NDVICold2 = np.amin(NDVI)
NDVICold3 = np.amin(NDVI)


for i in range(0,linhas):
	for j in range(0,colunas):
		if not(NDVI[i,j] == None):
			if NDVI[i,j] <= NDVIHot1 and T[i,j] >= THot1:
				THot3 = THot2
				NDVIHot3 = NDVIHot2
				
				THot2 = THot1
				NDVIHot2 = NDVIHot1
				
				THot1 = T[i,j]
				NDVIHot1 = NDVI[i,j]
				
				NDVI[i,j] = None
			
			if not(NDVI[i,j] == None) and NDVI[i,j] >= NDVICold1	and T[i,j] <= TCold1:
				TCold3 = TCold2
				NDVICold3 = NDVICold2
				
				TCold2 = TCold1
				NDVICold2 = NDVICold1
				
				TCold1 = T[i,j]
				NDVICold1 = NDVI[i,j]
				
				NDVI[i,j] = None


TH = (THot1 + THot2 + THot3)/3
TC = (TCold1 + TCold2 + TCold3)/3
NDVI = None

#Fracao de evapotranspiracao
ETf = (TH - T)/(TH - TC)
EscreveResult(ETf,'FracaoEvapotranspiracao.tif')
T = None

#Slope Vapour Pressure Curve 
delta = (2504 * numpy.exp((17.27* Ta)/(Ta + 237.3)))/((Ta + 237.3)*(Ta + 237.3))

#Calor latente de vaporizacao
l = 2.501 - (0.002361)*Ta


#Pressao atmosferica
P = 101.3* math.pow((273.15 + Ta - 0.0065*z)/(273.15 + Ta), 5.26)

#Psychrometric constant
gama = 0.00163*P/l

#Pressao saturada e atual do vapor
es = 6.1078 * math.pow(10,(7.5*Ta)/(237.3 + Ta))
Td = 100 - ((100- UR)/5)
ea = 6.1078 * math.pow(10,(7.5*Td)/(237.3 + Td))

#Evapotranspiracao atual
ET0 = (0.408 * delta * (Rn - G) + gama * (900/(Ta + 273.15))*u2*(es - ea)) /(delta + gama*(1 + 0.34*u2))
ETa = ETf * ET0
EscreveResult(ETa,'EvapotranspiracaoAtual.tif')
ET0 = None
ETf = None
ETa = None

fim = time.time()
print 'Tempo total: '+str(fim - inicio)

