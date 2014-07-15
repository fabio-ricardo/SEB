import gdal
from gdalconst import *
import sys,os,math,time
import numpy

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
Ea = 0.85 * math.pow(-1*math.log((0.75 +0.00002*z)),0.09)
Rol_atm = Ea * 0.0000000567 * Ta*Ta*Ta*Ta

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
	outDataSet = driver.Create('ResultadosProcessamento-'+nomeFile+'/'+nome,colunas,linhas,1,GDT_Float64)
	outBand = outDataSet.GetRasterBand(1)
	outBand.WriteArray(arq,0,0)
	outDataSet = None

#Radiancia e reflectancia
banda = img.GetRasterBand(1).ReadAsArray().astype(numpy.float64)
L1 = a1 + ((b1 - a1)/255)* banda
P1 = (math.pi * L1)/(k1 * math.cos(angle)*d)
banda = None
AlPlan = 0.293461814725*P1
L1 = None
P1 = None

banda = img.GetRasterBand(2).ReadAsArray().astype(numpy.float64)
L2 = a2 + ((b2 - a2)/255)* banda
P2 = (math.pi * L2)/(k2 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.273817717776*P2
L2 = None
P2 = None

banda = img.GetRasterBand(3).ReadAsArray().astype(numpy.float64)
L3 = a3 + ((b3 - a3)/255)* banda
P3 = (math.pi * L3)/(k3 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.233029974493*P3
L3 = None

banda = img.GetRasterBand(4).ReadAsArray().astype(numpy.float64)
L4 = a4 + ((b4 - a4)/255)* banda
P4 = (math.pi * L4)/(k4 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan+ 0.155353316328*P4
L4 = None

banda = img.GetRasterBand(5).ReadAsArray().astype(numpy.float64)
L5 = a5 + ((b5 - a5)/255)* banda
P5 = (math.pi * L5)/(k5 * math.cos(angle)*d)
banda = None
AlPlan = AlPlan + 0.0322403117863*P5
L5 = None
P5 = None

banda = img.GetRasterBand(6).ReadAsArray().astype(numpy.float64)
L6 = a6 + ((b6 - a6)/255)* banda
banda = None

banda = img.GetRasterBand(7).ReadAsArray().astype(numpy.float64)
L7 = a7 + ((b7 - a7)/255)* banda
P7 = (math.pi * L7)/(k7 * math.cos(angle)*d)
banda = None
img = None
AlPlan = AlPlan+ 0.0120968648921*P7
L7 = None
P7 = None

#Albedo superficie(deve-se imprimir em porcentagem)
AlSuper = (AlPlan - 0.03)* (1/((0.75 +0.00002*z)*(0.75 +0.00002*z)))
AlPlan = None
EscreveResult(AlSuper,'AlbedoSuperficie.tif')

#indice de Vegetacao da Diferenca Normalizada
NDVI = (P4 - P3) / (P4+ P3)
EscreveResult(NDVI,'NDVI.tif')

#indice de Vegetacao Ajustado para os Efeitos do Solo
SAVI = ((1+0.5)*(P4-P3))/(0.5+P4+P3)
EscreveResult(SAVI,'SAVI.tif')
P4 = None
P3 = None

numpy.seterr(all='ignore')

#Indice area foliar
mask = ((0.69 - SAVI) / 0.59) > 0
IAF = numpy.choose(mask, (0.0, (numpy.log((0.69 - SAVI)/0.59))/0.91 * (-1)))
EscreveResult(IAF,'IAF.tif')
SAVI = None

numpy.seterr(all='warn')

#Emissividade
Enb = 0.97 + 0.00331* IAF
E0 = 0.95 + 0.01 * IAF
IAF = None

#Temperatura satelite (K)
T = 1260.56/(numpy.log((Enb*607.76/L6) +1))
L6 = None
EscreveResult(T,'Temperatura.tif')
Enb = None

#fluxo radiacao termal emitida
Frt_emit= E0*0.0000000567*T*T*T*T

#Radiacao onda curta incidente
Rs = 1367 * math.cos(angle)*(0.75 +0.00002*z) * d

#Saldo da radiacao
Rn = (1 - AlSuper)*Rs + Rol_atm - Frt_emit - (1 - E0)*Rol_atm
Frt_emit = None
EscreveResult(Rn,'SaldoRadiacao.tif')

#Fluxo de calor no solo
G = ((T - 273.15)*(0.0038 + (0.0074*AlSuper))*(1-0.98*numpy.power(NDVI,4)))*Rn
EscreveResult(G,'FluxoDeCalorNoSolo.tif')
NDVI = None

x1 = 0.1
x2 = 0.9

#Pontos p/ lim superior e inferior
maskAlbedoSuper = AlSuper <= 0.2
limiteLadoEsq = T[maskAlbedoSuper]

maskAlbedoSuper = AlSuper >= 0.75
limiteLadoDir = T[maskAlbedoSuper]

limiteLadoEsq = numpy.sort(limiteLadoEsq)
limiteLadoDir = numpy.sort(limiteLadoDir)

limSupEsqAux = limiteLadoEsq[::-1][0:20]
limInfEsqAux = limiteLadoEsq[0:20]

limSupDirAux = limiteLadoDir[::-1][0:20]
limInfDirAux = limiteLadoDir[0:20]

y1 = numpy.sum(limSupEsqAux)/20
y3 = numpy.sum(limInfEsqAux)/20
y2 = numpy.sum(limSupDirAux)/20
y4 = numpy.sum(limInfDirAux)/20

#Coeficientes das retas
m1 = (y2-y1)/(x2-x1)
m2 = (y4-y3)/(x2-x1)
c1 = (x2*y1 - x1*y2)/(x2-x1)
c2 = (x2*y3 - x1*y4)/(x2-x1)

#fracao evaporativa
V_virado = ((c1 + m1*AlSuper) - T)/(c1 - c2 + (m1 - m2)*AlSuper)
T = None
AlSuper = None
EscreveResult(V_virado,'FracaoEvaporativa.tif')

#Fluxo calor sensivel
H = (1- V_virado)*(Rn - G)
EscreveResult(H,'FluxoCalorSensivel.tif')
H = None

#Fluxo calor latente
LE = V_virado * (Rn - G)
EscreveResult(LE,'FluxoCalorLatente.tif')

G = None
Rn = None
V_virado = None

fim = time.time()
print 'Tempo total: '+str(fim - inicio)
