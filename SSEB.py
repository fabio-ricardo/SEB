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

noValue = -9999.0
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
G = 0.5
qtdPontos = 3

u2 = 2.77
UR = 50
delta = (2504 * math.exp((17.27 * Ta) / (Ta + 237.3))) / ((Ta + 237.3) * (Ta + 237.3))
l = 2.501 - 0.002361 * Ta
P = 101.3 * math.pow((273.15 + Ta - 0.0065 * z) / (273.15 + Ta), 5.26)
gama = 0.00163 * P / l
es = 6.1078 * math.pow(10, (7.5 * Ta) / (237.3 + Ta))
Td = 100 - ((100 - UR) / 5)
ea = 6.1078 * math.pow(10, (7.5 * Td) / (237.3 + Td))

p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
p1[0] = 0
p1[6] = 0

#----------

for k in range(1,NBandas+1):
    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr)

#----------

pastaSaida = 'SSEB__'+nomeArquivoEntrada+'/'

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

maskAlbPlan = dados > 0

dados = None
radiancia = None
reflectancia = None

#----------

dados = entrada.GetRasterBand(2).ReadAsArray().astype(numpy.float64)

radiancia = descBandas[2][3] + (descBandas[2][6] * dados)
reflectancia = p1[2] * radiancia

albedoPlanetario += descBandas[2][7] * reflectancia

maskAlbPlan = numpy.logical_and(maskAlbPlan, dados > 0)

dados = None
radiancia = None
reflectancia = None

#----------

dados3 = entrada.GetRasterBand(3).ReadAsArray().astype(numpy.float64)

radiancia = descBandas[3][3] + (descBandas[3][6] * dados3)
reflectancia = p1[3] * radiancia

albedoPlanetario += descBandas[3][7] * reflectancia

maskAlbPlan = numpy.logical_and(maskAlbPlan, dados3 > 0)

radiancia = None
reflectancia = None

#----------

dados4 = entrada.GetRasterBand(4).ReadAsArray().astype(numpy.float64)

radiancia = descBandas[4][3] + (descBandas[4][6] * dados4)
reflectancia = p1[4] * radiancia

albedoPlanetario += descBandas[4][7] * reflectancia

maskAlbPlan = numpy.logical_and(maskAlbPlan, dados4 > 0)

radiancia = None
reflectancia = None

#----------

numpy.seterr(all='ignore')

#----------

saidaNDVI = driver.Create(pastaSaida+'ndvi.tif',colunas,linhas,1,GDT_Float64)
if saidaNDVI is None:
    print 'Erro ao criar o arquivo: ' + 'ndvi.tif'
    sys.exit(1)

saidaNDVI.SetProjection(projecao)
bandaNDVI = saidaNDVI.GetRasterBand(1)

mask = numpy.logical_and(dados3 > 0, dados4 > 0)

ndvi = numpy.choose(mask, (noValue, (dados4 - dados3) / (dados4 + dados3)))
bandaNDVI.WriteArray(ndvi,0,0)

bandaNDVI.SetNoDataValue(noValue)

bandaNDVI = None
saidaNDVI = None

print 'NDVI - Pronto'

#----------

saidaSAVI = driver.Create(pastaSaida+'savi.tif',colunas,linhas,1,GDT_Float64)
if saidaSAVI is None:
    print 'Erro ao criar o arquivo: ' + 'savi.tif'
    sys.exit(1)

saidaSAVI.SetProjection(projecao)
bandaSAVI = saidaSAVI.GetRasterBand(1)

savi = numpy.choose(mask, (noValue, ((1 + L) * (dados4 - dados3)) / (L + (dados4 + dados3))))

bandaSAVI.WriteArray(savi,0,0)

bandaSAVI.SetNoDataValue(noValue)

bandaSAVI = None
saidaSAVI = None

mask = None
dados4 = None
dados3 = None

print 'SAVI - Pronto'

#----------

saidaIAF = driver.Create(pastaSaida+'iaf.tif',colunas,linhas,1,GDT_Float64)
if saidaIAF is None:
    print 'Erro ao criar o arquivo: ' + 'iaf.tif'
    sys.exit(1)

saidaIAF.SetProjection(projecao)
bandaIAF = saidaIAF.GetRasterBand(1)

mask = numpy.logical_and(((0.69 - savi) / 0.59) > 0, savi != noValue)

iaf = numpy.choose(mask, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))

bandaIAF.WriteArray(iaf,0,0)

bandaIAF.SetNoDataValue(noValue)

bandaIAF = None
saidaIAF = None

mask = None
savi = None

print 'IAF - Pronto'

#----------

dados = entrada.GetRasterBand(5).ReadAsArray().astype(numpy.float64)

radiancia = descBandas[5][3] + (descBandas[5][6] * dados)
reflectancia = p1[5] * radiancia

albedoPlanetario += descBandas[5][7] * reflectancia

maskAlbPlan = numpy.logical_and(maskAlbPlan, dados > 0)

dados = None
radiancia = None
reflectancia = None

#----------

dados = entrada.GetRasterBand(6).ReadAsArray().astype(numpy.float64)

radianciaB6 = descBandas[6][3] + (descBandas[6][6] * dados)

maskB6 = dados > 0

dados = None

#----------

dados = entrada.GetRasterBand(7).ReadAsArray().astype(numpy.float64)

radiancia = descBandas[7][3] + (descBandas[7][6] * dados)
reflectancia = p1[7] * radiancia

albedoPlanetario += descBandas[7][7] * reflectancia

maskAlbPlan = numpy.logical_and(maskAlbPlan, dados > 0)

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

albedoSuperficie = numpy.choose(maskAlbPlan, (noValue, (albedoPlanetario - ap) * p2))

mask = numpy.logical_and(albedoSuperficie < 0, albedoSuperficie != noValue)

albedoSuperficie = numpy.choose(mask, (albedoSuperficie, 0.0))

bandaAlbedoSuper.WriteArray(albedoSuperficie,0,0)

bandaAlbedoSuper.SetNoDataValue(noValue)

bandaAlbedoSuper = None
saidaAlbedoSuper = None

mask = None
maskAlbPlan = None
albedoPlanetario = None

print 'Albedo Superficie - Pronto'

#----------

ENB = 0.97 + 0.00331 * iaf
E0 = 0.95 + 0.01 * iaf

mask = iaf >= 3

ENB = numpy.choose(mask, (ENB, 0.98))
E0 = numpy.choose(mask, (E0, 0.98))

mask = ndvi < 0

ENB = numpy.choose(mask, (ENB, 0.99))
E0 = numpy.choose(mask, (E0, 0.985))

mask = numpy.logical_or(ndvi == noValue, iaf == noValue)

ENB = numpy.choose(mask, (ENB, noValue))
E0 = numpy.choose(mask, (E0, noValue))

mask = None
iaf = None

#----------

saidaTempSuper = driver.Create(pastaSaida+'temperaturaSuperficie.tif',colunas,linhas,1,GDT_Float64)
if saidaTempSuper is None:
    print 'Erro ao criar o arquivo: ' + 'temperaturaSuperficie.tif'
    sys.exit(1)

saidaTempSuper.SetProjection(projecao)
bandaTempSuper = saidaTempSuper.GetRasterBand(1)

mask = numpy.logical_and(ENB != noValue, maskB6)

temperaturaSuperficie = numpy.choose(mask, (noValue, K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)))
bandaTempSuper.WriteArray(temperaturaSuperficie,0,0)

bandaTempSuper.SetNoDataValue(noValue)

bandaTempSuper = None
saidaTempSuper = None

maskB6 = None
mask = None
radianciaB6 = None
ENB = None

print 'Temperatura Superficie - Pronto'

#----------

numpy.seterr(all='warn')

#----------

saidaSaldoRad = driver.Create(pastaSaida+'saldoRadiacao.tif',colunas,linhas,1,GDT_Float64)
if saidaSaldoRad is None:
    print 'Erro ao criar o arquivo: ' + 'saldoRadiacao.tif'
    sys.exit(1)

saidaSaldoRad.SetProjection(projecao)
bandaSaldoRad = saidaSaldoRad.GetRasterBand(1)

radOndaLongaEmi = ((E0 * constSB) * (temperaturaSuperficie*temperaturaSuperficie*temperaturaSuperficie*temperaturaSuperficie))

mask = numpy.logical_and(temperaturaSuperficie != noValue, albedoSuperficie != noValue)

saldoRadiacao = numpy.choose(mask, (noValue, radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci))

bandaSaldoRad.WriteArray(saldoRadiacao,0,0)

bandaSaldoRad.SetNoDataValue(noValue)

bandaSaldoRad = None
saidaSaldoRad = None

E0 = None
radOndaLongaEmi = None

print 'Saldo Radiação - Pronto'

#----------

saidaFluxoCalSolo = driver.Create(pastaSaida+'fluxoCalorSolo.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxoCalSolo is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSolo.tif'
    sys.exit(1)

saidaFluxoCalSolo.SetProjection(projecao)
bandaFluxoCalSolo = saidaFluxoCalSolo.GetRasterBand(1)

maska = ndvi < 0

fluxoCalSolo = numpy.choose(maska, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * (ndvi*ndvi*ndvi*ndvi)))) * saldoRadiacao, G))

maska = None

mask = numpy.logical_and(mask, ndvi != noValue)

fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))

bandaFluxoCalSolo.WriteArray(fluxoCalSolo,0,0)

bandaFluxoCalSolo.SetNoDataValue(noValue)

bandaFluxoCalSolo = None
saidaFluxoCalSolo = None

mask = None
albedoSuperficie = None

print 'Fluxo Calor no Solo - Pronto'

#----------

hotTemp = numpy.array([],dtype=numpy.float64)
coldNdvi = numpy.array([],dtype=numpy.float64)

coldTemp = numpy.array([],dtype=numpy.float64)
hotNdvi = numpy.array([],dtype=numpy.float64)

tempSuperficie = numpy.copy(temperaturaSuperficie)

tempSuperficie.reshape(-1)
ndvi.reshape(-1)

mask = numpy.logical_and(tempSuperficie != noValue, ndvi != noValue)

tempSuperficie = tempSuperficie[mask]
ndvi = ndvi[mask]

mask = None

for i in range(qtdPontos):
    if hotTemp.size < qtdPontos:
        ndviTempIgual = numpy.array([])

        hotTemp = numpy.append(hotTemp,tempSuperficie[numpy.nanargmax(tempSuperficie)])
        ndviTempIgual = numpy.append(ndviTempIgual,ndvi[numpy.nanargmax(tempSuperficie)])
        tempSuperficie[numpy.nanargmax(tempSuperficie)] = numpy.nan

        prox = numpy.nanargmax(tempSuperficie)
        posUlt = hotTemp.size-1

        while hotTemp[posUlt] == tempSuperficie[prox]:
            ndviTempIgual = numpy.append(ndviTempIgual,ndvi[prox])

            tempSuperficie[prox] = numpy.nan
            prox = numpy.nanargmax(tempSuperficie)

        if ndviTempIgual.size > 1:
            ndviTempIgual = numpy.sort(ndviTempIgual)

            tamNdviTeIg = ndviTempIgual.size
            if tamNdviTeIg > (qtdPontos - posUlt):
                tamNdviTeIg = qtdPontos - posUlt

            coldNdvi = numpy.append(coldNdvi,ndviTempIgual[:tamNdviTeIg])

            for j in range(tamNdviTeIg-1):
                hotTemp = numpy.append(hotTemp,hotTemp[posUlt])

        else:
            coldNdvi = numpy.append(coldNdvi,ndviTempIgual[0])

        ndviTempIgual = None

    if coldTemp.size < qtdPontos:
        ndviTempIgual = numpy.array([])

        coldTemp = numpy.append(coldTemp,tempSuperficie[numpy.nanargmin(tempSuperficie)])
        ndviTempIgual = numpy.append(ndviTempIgual,ndvi[numpy.nanargmin(tempSuperficie)])
        tempSuperficie[numpy.nanargmin(tempSuperficie)] = numpy.nan

        prox = numpy.nanargmin(tempSuperficie)
        posUlt = coldTemp.size-1

        while coldTemp[posUlt] == tempSuperficie[prox]:
            ndviTempIgual = numpy.append(ndviTempIgual,ndvi[prox])

            tempSuperficie[prox] = numpy.nan
            prox = numpy.nanargmin(tempSuperficie)

        if ndviTempIgual.size > 1:
            ndviTempIgual = numpy.sort(ndviTempIgual)[::-1]

            tamNdviTeIg = ndviTempIgual.size
            if tamNdviTeIg > (qtdPontos - posUlt):
                tamNdviTeIg = qtdPontos - posUlt

            hotNdvi = numpy.append(hotNdvi,ndviTempIgual[:tamNdviTeIg])

            for j in range(tamNdviTeIg-1):
                coldTemp = numpy.append(coldTemp,coldTemp[posUlt])

        else:
            hotNdvi = numpy.append(hotNdvi,ndviTempIgual[0])

        ndviTempIgual = None

ndvi = None
tempSuperficie = None

#----------

TH = numpy.mean(hotTemp)
TC = numpy.mean(coldTemp)

#----------

saidaFracEvapo = driver.Create(pastaSaida+'fracaoEvaporativa.tif',colunas,linhas,1,GDT_Float64)
if saidaFracEvapo is None:
    print 'Erro ao criar o arquivo: ' + 'fracaoEvaporativa.tif'
    sys.exit(1)

saidaFracEvapo.SetProjection(projecao)
bandaFracEvapo = saidaFracEvapo.GetRasterBand(1)

mask = temperaturaSuperficie != noValue

fracaoEvaporativa = numpy.choose(mask, (noValue, (TH - temperaturaSuperficie) / (TH - TC)))

bandaFracEvapo.WriteArray(fracaoEvaporativa,0,0)

bandaFracEvapo.SetNoDataValue(noValue)

bandaFracEvapo = None
saidaFracEvapo = None

mask = None
temperaturaSuperficie = None

print 'Fração Evaporativa - Pronto'

#----------

saidaEvapotransAtual = driver.Create(pastaSaida+'evapotranspiracaoAtual.tif',colunas,linhas,1,GDT_Float64)
if saidaEvapotransAtual is None:
    print 'Erro ao criar o arquivo: ' + 'evapotranspiracaoAtual.tif'
    sys.exit(1)

saidaEvapotransAtual.SetProjection(projecao)
bandaEvapotransAtual = saidaEvapotransAtual.GetRasterBand(1)

mask = fluxoCalSolo != noValue

evapotranspiracaoAtual = numpy.choose(mask, (noValue, ((0.408 * delta * (saldoRadiacao - fluxoCalSolo)\
    + gama * (900 / (Ta + 273.15)) * u2 * (es - ea)) / (delta + gama * (1 + 0.34 * u2))) * fracaoEvaporativa))

bandaEvapotransAtual.WriteArray(evapotranspiracaoAtual,0,0)

bandaEvapotransAtual.SetNoDataValue(noValue)

bandaEvapotransAtual = None
saidaEvapotransAtual = None

mask = None
evapotranspiracaoAtual = None
saldoRadiacao = None
fluxoCalSolo = None
fracaoEvaporativa = None

print 'Evapotranspiracao Atual - Pronto'

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
