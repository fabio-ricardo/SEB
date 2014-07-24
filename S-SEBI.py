#coding: utf-8
import gdal, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

inicio = time.time()

driver = gdal.GetDriverByName('GTiff')
driver.Register()

nomeArquivoEntrada = 'empilhada.tif'

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

pi = math.pi
cosZ = math.cos((90 - 56.98100422)*pi/180) # pego do metadata da imagem - SUN_ELEVATION
dr = 1+0.033*math.cos((272*2*pi)/365) # 29 de setembro de 2011
ap = 0.03
z = 200
tsw = 0.75 + 2*0.00001 * z
p2 = 1 / (tsw * tsw)
L = 0.5
K1 = 607.76
K2 = 1260.56
constSB = 0.0000000567
S = 1367
radOndaCurtaInci = S * cosZ * dr * tsw
Ea = 0.85 * math.pow(-1 * math.log(tsw),0.09)
Ta = 295
radOndaLongaInci = Ea * constSB * math.pow(Ta,4)
qtdPontos = 20
x1 = 0.1
x2 = 0.9
x2x1 = x2 - x1

p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
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

dados = entrada.GetRasterBand(1).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[1][3] + (descBandas[1][6] * dados)
reflectancia = p1[1] * radiancia

albedoPlanetario = descBandas[1][7] * reflectancia

dados = None
radiancia = None
reflectancia = None

#----------

dados = entrada.GetRasterBand(2).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[2][3] + (descBandas[2][6] * dados)
reflectancia = p1[2] * radiancia

albedoPlanetario += descBandas[2][7] * reflectancia

dados = None
radiancia = None
reflectancia = None

#----------

dados = entrada.GetRasterBand(3).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[3][3] + (descBandas[3][6] * dados)
reflectanciaB3 = p1[3] * radiancia

albedoPlanetario += descBandas[3][7] * reflectanciaB3

dados = None
radiancia = None

#----------

dados = entrada.GetRasterBand(4).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[4][3] + (descBandas[4][6] * dados)
reflectanciaB4 = p1[4] * radiancia

albedoPlanetario += descBandas[4][7] * reflectanciaB4

dados = None
radiancia = None

#----------

saidaNDVI = driver.Create(pastaSaida+'ndvi.tif',colunas,linhas,1,GDT_Float64)
if saidaNDVI is None:
    print 'Erro ao criar o arquivo: ' + 'ndvi.tif'
    sys.exit(1)

saidaNDVI.SetProjection(projecao)
bandaNDVI = saidaNDVI.GetRasterBand(1)

ndvi = (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)
bandaNDVI.WriteArray(ndvi,0,0)

bandaNDVI = None
saidaNDVI = None

#----------

saidaSAVI = driver.Create(pastaSaida+'savi.tif',colunas,linhas,1,GDT_Float64)
if saidaSAVI is None:
    print 'Erro ao criar o arquivo: ' + 'savi.tif'
    sys.exit(1)

saidaSAVI.SetProjection(projecao)
bandaSAVI = saidaSAVI.GetRasterBand(1)

savi = ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))
bandaSAVI.WriteArray(savi,0,0)

bandaSAVI = None
saidaSAVI = None

reflectanciaB4 = None
reflectanciaB3 = None

#----------

saidaIAF = driver.Create(pastaSaida+'iaf.tif',colunas,linhas,1,GDT_Float64)
if saidaIAF is None:
    print 'Erro ao criar o arquivo: ' + 'iaf.tif'
    sys.exit(1)

saidaIAF.SetProjection(projecao)
bandaIAF = saidaIAF.GetRasterBand(1)

numpy.seterr(all='ignore')

maskLog = ((0.69 - savi) / 0.59) > 0

iaf = numpy.choose(maskLog, (0.0, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))
bandaIAF.WriteArray(iaf,0,0)

numpy.seterr(all='warn')

bandaIAF = None
saidaIAF = None

savi = None

#----------

dados = entrada.GetRasterBand(5).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[5][3] + (descBandas[5][6] * dados)
reflectancia = p1[5] * radiancia

albedoPlanetario += descBandas[5][7] * reflectancia

dados = None
radiancia = None
reflectancia = None

#----------

dados = entrada.GetRasterBand(6).ReadAsArray().astype(numpy.float64)
radianciaB6 = descBandas[6][3] + (descBandas[6][6] * dados)

dados = None

#----------

dados = entrada.GetRasterBand(7).ReadAsArray().astype(numpy.float64)
radiancia = descBandas[7][3] + (descBandas[7][6] * dados)
reflectancia = p1[7] * radiancia

albedoPlanetario += descBandas[7][7] * reflectancia

dados = None
radiancia = None
reflectancia = None

#----------

entrada = None

#----------

saidaAlbedoSuper = driver.Create(pastaSaida+'albedoSuperficie.tif',colunas,linhas,1,GDT_Float64)
if saidaAlbedoSuper is None:
    print 'Erro ao criar o arquivo: ' + 'albedoSuperficie.tif'
    sys.exit(1)

saidaAlbedoSuper.SetProjection(projecao)
bandaAlbedoSuper = saidaAlbedoSuper.GetRasterBand(1)

albedoSuperficie = (albedoPlanetario - ap) * p2
bandaAlbedoSuper.WriteArray(albedoSuperficie,0,0)

bandaAlbedoSuper = None
saidaAlbedoSuper = None

albedoPlanetario = None

#----------

ENB = 0.97 + 0.00331 * iaf
E0 = 0.95 + 0.01 * iaf

iaf = None

#----------

saidaTempSuper = driver.Create(pastaSaida+'temperatura_superficie.tif',colunas,linhas,1,GDT_Float64)
if saidaTempSuper is None:
    print 'Erro ao criar o arquivo: ' + 'temperatura_superficie.tif'
    sys.exit(1)

saidaTempSuper.SetProjection(projecao)
bandaTempSuper = saidaTempSuper.GetRasterBand(1)

temperaturaSuperficie = K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)
a = open('temp.txt','w+')
b = open('albe.txt','w+')
for i in range(0, linhas):
	for j in range(0,colunas):
		a.write(str(temperaturaSuperficie[i,j])+'\n')
		b.write(str(albedoSuperficie[i,j])+'\n')
	print i

'''bandaTempSuper.WriteArray(temperaturaSuperficie,0,0)

bandaTempSuper = None
saidaTempSuper = None

radianciaB6 = None
ENB = None

#----------

saidaSaldoRad = driver.Create(pastaSaida+'saldoRadiacao.tif',colunas,linhas,1,GDT_Float64)
if saidaSaldoRad is None:
    print 'Erro ao criar o arquivo: ' + 'saldoRadiacao.tif'
    sys.exit(1)

saidaSaldoRad.SetProjection(projecao)
bandaSaldoRad = saidaSaldoRad.GetRasterBand(1)

radOndaLongaEmi = (E0 * constSB) * (temperaturaSuperficie*temperaturaSuperficie*\
                                    temperaturaSuperficie*temperaturaSuperficie)

saldoRadiacao = radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci
bandaSaldoRad.WriteArray(saldoRadiacao,0,0)

bandaSaldoRad = None
saidaSaldoRad = None

E0 = None
radOndaLongaEmi = None

#----------

saidaFluxoCalSolo = driver.Create(pastaSaida+'fluxoCalorSolo.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxoCalSolo is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSolo.tif'
    sys.exit(1)

saidaFluxoCalSolo.SetProjection(projecao)
bandaFluxoCalSolo = saidaFluxoCalSolo.GetRasterBand(1)

fluxoCalSolo = ((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * (ndvi*ndvi*ndvi*ndvi)))) * saldoRadiacao
bandaFluxoCalSolo.WriteArray(fluxoCalSolo,0,0)

bandaFluxoCalSolo = None
saidaFluxoCalSolo = None

ndvi = None

#----------

maskAlbedoSuper = albedoSuperficie <= 0.2
limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]

maskAlbedoSuper = albedoSuperficie >= 0.75
limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]

maskAlbedoSuper = None

limiteLadoEsq = numpy.sort(limiteLadoEsq)
limiteLadoDir = numpy.sort(limiteLadoDir)

limSupEsq = limiteLadoEsq[::-1][0:qtdPontos]
limInfEsq = limiteLadoEsq[0:qtdPontos]

limSupDir = limiteLadoDir[::-1][0:qtdPontos]
limInfDir = limiteLadoDir[0:qtdPontos]

limiteLadoEsq = None
limiteLadoDir = None

#----------

limSupEsq = numpy.sum(limSupEsq) / qtdPontos
limInfEsq = numpy.sum(limInfEsq) / qtdPontos

limSupDir = numpy.sum(limSupDir) / qtdPontos
limInfDir = numpy.sum(limInfDir) / qtdPontos

m1 = (limSupDir - limSupEsq) / x2x1
m2 = (limInfDir - limInfEsq) / x2x1

c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1


#----------

saidaFracEvapo = driver.Create(pastaSaida+'fracaoEvaporativa.tif',colunas,linhas,1,GDT_Float64)
if saidaFracEvapo is None:
    print 'Erro ao criar o arquivo: ' + 'fracaoEvaporativa.tif'
    sys.exit(1)

saidaFracEvapo.SetProjection(projecao)
bandaFracEvapo = saidaFracEvapo.GetRasterBand(1)

fracaoEvaporativa = (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie) / ((c1 - c2) + ((m1 - m2) * albedoSuperficie))
bandaFracEvapo.WriteArray(fracaoEvaporativa,0,0)

bandaFracEvapo = None
saidaFracEvapo = None

albedoSuperficie = None
temperaturaSuperficie = None

#----------

saidaFluxCalSensi = driver.Create(pastaSaida+'fluxoCalorSensivel.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxCalSensi is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSensivel.tif'
    sys.exit(1)

saidaFluxCalSensi.SetProjection(projecao)
bandaFluxCalSensi = saidaFluxCalSensi.GetRasterBand(1)

fluxoCalorSensivel = (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)
bandaFluxCalSensi.WriteArray(fluxoCalorSensivel,0,0)

bandaFluxCalSensi = None
saidaFluxCalSensi = None

fluxoCalorSensivel = None

#----------

saidaFluxCalLaten = driver.Create(pastaSaida+'fluxoCalorLatente.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxCalLaten is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorLatente.tif'
    sys.exit(1)

saidaFluxCalLaten.SetProjection(projecao)
bandaFluxCalLaten = saidaFluxCalLaten.GetRasterBand(1)

fluxoCalorLatente = fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)
bandaFluxCalLaten.WriteArray(fluxoCalorLatente,0,0)

bandaFluxCalLaten = None
saidaFluxCalLaten = None

fluxoCalorLatente = None
saldoRadiacao = None
fluxoCalSolo = None
fracaoEvaporativa = None

#----------'''

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
