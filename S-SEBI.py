#coding: utf-8
import gdal, time, numpy, sys, math, os
from gdalconst import *
from constantes import *

inicio = time.time()

driver = gdal.GetDriverByName('GTiff')
driver.Register()

nomeArquivoEntrada = 'cambarazal.tif'

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
Z = 40.647
cosZ = math.cos((90 - Z) * pi / 180)
julianDay = 205.0
dr = 1.0 + 0.033 * math.cos((julianDay * 2 * pi) / 365)
ap = 0.03
Ta = 25.27
UR = 67.98
ea = (0.61078 * math.exp(17.269 * Ta / (237.3 + Ta))) * UR / 100.0
P = 99.9
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
qtdPontos = 10
Rg24h = 183.8756158
Tao24h = 0.575066923

p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)

#----------

for k in xrange(1,NBandas+1):
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

dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)

#----------
#----------

albedoPlanetario = 0

for k in xrange(1,NBandas+1):
    dados[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
    radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])
    print str(k)+ ' ' + str(dados[k][3964][3418])

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

#saidaImagem('ndvi',ndvi)

#----------

savi = numpy.choose(mask, (noValue, ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))))

#saidaImagem('savi',savi)

reflectanciaB4 = None
reflectanciaB3 = None

#----------

numpy.seterr(all='ignore')

#----------

mask1 = numpy.logical_and(((0.69 - savi) / 0.59) > 0, mask)

iaf = numpy.choose(mask1, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))

#saidaImagem('iaf',iaf)

mask1 = None

#----------

numpy.seterr(all='warn')

#----------
albedoSuperficie = numpy.choose(mask, (noValue, (albedoPlanetario - ap) * p2))

#saidaImagem('albedoSuperficie',albedoSuperficie)

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
#numpy.savetxt('temperaturaSuperficie.txt', temperaturaSuperficie, delimiter='\n')
#numpy.savetxt('albedoSuperficie.txt', albedoSuperficie, delimiter='\n')
saidaImagem('temperaturaSuperficie',temperaturaSuperficie)

radianciaB6 = None
ENB = None

#----------
'''
radOndaLongaEmi = (E0 * constSB) * numpy.power(temperaturaSuperficie,4)

saldoRadiacao = numpy.choose(mask, (noValue, ((1.0 - albedoSuperficie) * radOndaCurtaInci) +\
                                    (E0 * radOndaLongaInci - radOndaLongaEmi)))

print radOndaLongaEmi[3964][3418]
print temperaturaSuperficie[3964][3418]
print albedoSuperficie[3964][3418]
print radOndaCurtaInci
print radOndaLongaInci
print saldoRadiacao[3964][3418]

saidaImagem('saldoRadiacao',saldoRadiacao)

E0 = None
radOndaLongaEmi = None
'''
#----------
'''
mask1 = ndvi < 0

fluxoCalSolo = numpy.choose(mask1, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1.0 - (0.98 * numpy.power(ndvi,4)))) * saldoRadiacao, G*saldoRadiacao))

mask1 = None

fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))

saidaImagem('fluxoCalSolo',fluxoCalSolo)

ndvi = None
'''
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
ifinal=time.time()

#----------

print limSupEsq
print limInfEsq

print limSupDir
print limInfDir

limSupEsq = numpy.mean(limSupEsq)
limInfEsq = numpy.mean(limInfEsq)

limSupDir = numpy.mean(limSupDir)
limInfDir = numpy.mean(limInfDir)

x1 = 0.1
x2 = albedoSupMax
x2x1 = x2 - x1

print limSupEsq
print limInfEsq

print limSupDir
print limInfDir

print x2

m1 = (limSupDir - limSupEsq) / x2x1
m2 = (limInfDir - limInfEsq) / x2x1

c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1

print str(m1)+'x + '+str(c1)
print str(m2)+'x + '+str(c2)

#----------
'''
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
'''
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
