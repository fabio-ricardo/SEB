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
qtdPontos = 3
Rg24h = 243.95
Tao24h = 0.63

p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)

#----------

for k in xrange(1,NBandas+1):
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

dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)

#----------

albedoPlanetario = 0

for k in xrange(1,NBandas+1):
    dados[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
    radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])

    if (k == 2):
        mask = dados[k-1] == dados[k]
        dados[k-1] = None
    elif(k > 2):
        mask = valueOff == dados[k]

    if(k != NBandas and k >= 2):
        valueOff = numpy.choose(mask,(numpy.nan, dados[k]))

    if(k >= 2):
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

mask = numpy.choose(mask,(True,False))

#----------

valueOff = None
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

#----------

hotNdvi = numpy.array([],dtype=numpy.float32)
coldTemp = numpy.array([],dtype=numpy.float32)

coldNdvi = numpy.array([],dtype=numpy.float32)
hotTemp = numpy.array([],dtype=numpy.float32)

tempSuperficie = temperaturaSuperficie

tempSuperficie.reshape(-1)
ndvi.reshape(-1)

tempSuperficie = tempSuperficie[mask]
ndvi = ndvi[mask]

for i in xrange(qtdPontos):
    if hotNdvi.size < qtdPontos:
        tempNdviIgual = numpy.array([])

        hotNdvi = numpy.append(hotNdvi,ndvi[numpy.nanargmax(ndvi)])
        tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[numpy.nanargmax(ndvi)])
        ndvi[numpy.nanargmax(ndvi)] = numpy.nan

        prox = numpy.nanargmax(ndvi)
        posUlt = hotNdvi.size-1

        while hotNdvi[posUlt] == ndvi[prox]:
            tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[prox])

            ndvi[prox] = numpy.nan
            prox = numpy.nanargmax(ndvi)

        if tempNdviIgual.size > 1:
            tempNdviIgual = numpy.sort(tempNdviIgual)

            tamTempNdviIg = tempNdviIgual.size
            if tamTempNdviIg > (qtdPontos - posUlt):
                tamTempNdviIg = qtdPontos - posUlt

            coldTemp = numpy.append(coldTemp,tempNdviIgual[:tamTempNdviIg])

            for j in xrange(tamTempNdviIg-1):
                hotNdvi = numpy.append(hotNdvi,hotNdvi[posUlt])

        else:
            coldTemp = numpy.append(coldTemp,tempNdviIgual[0])

        tempNdviIgual = None

    if coldNdvi.size < qtdPontos:
        tempNdviIgual = numpy.array([])

        coldNdvi = numpy.append(coldNdvi,ndvi[numpy.nanargmin(ndvi)])
        tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[numpy.nanargmin(ndvi)])
        ndvi[numpy.nanargmin(ndvi)] = numpy.nan

        prox = numpy.nanargmin(ndvi)
        posUlt = coldNdvi.size-1

        while coldNdvi[posUlt] == ndvi[prox]:
            tempNdviIgual = numpy.append(tempNdviIgual,tempSuperficie[prox])

            ndvi[prox] = numpy.nan
            prox = numpy.nanargmin(ndvi)

        if tempNdviIgual.size > 1:
            tempNdviIgual = numpy.sort(tempNdviIgual)[::-1]

            tamTempNdviIg = tempNdviIgual.size
            if tamTempNdviIg > (qtdPontos - posUlt):
                tamTempNdviIg = qtdPontos - posUlt

            hotTemp = numpy.append(hotTemp,tempNdviIgual[:tamTempNdviIg])

            for j in xrange(tamTempNdviIg-1):
                coldNdvi = numpy.append(coldNdvi,coldNdvi[posUlt])

        else:
            hotTemp = numpy.append(hotTemp,tempNdviIgual[0])

        tempNdviIgual = None

ndvi = None
tempSuperficie = None

#----------

TH = numpy.mean(hotTemp)
TC = numpy.mean(coldTemp)

#----------

fracaoEvaporativa = numpy.choose(mask, (noValue, (TH - temperaturaSuperficie) / (TH - TC)))

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

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
