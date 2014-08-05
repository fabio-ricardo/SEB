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
qtdPontos = 20

p1 = numpy.empty([NBandas+1],dtype=numpy.float32)
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

dados = numpy.zeros([NBandas+1,linhas,colunas],dtype=numpy.float32)

#----------

albedoPlanetario = 0

for k in range(1,NBandas+1):
    dados[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)
    radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])

    if(k >= 2):
        if(k == 2):
            noDataValue = entrada.GetRasterBand(k-1).GetNoDataValue()

            valueOff = dados[k-1][dados[k-1] == dados[k]]
            valueOff = dados[k-1][valueOff != noDataValue][0]

            if(valueOff.size > 0):
                mask = numpy.logical_and(dados[k-1] != valueOff, dados[k-1] != noDataValue)
            else:
                mask = dados[k-1] != noDataValue

            dados[k-1] = None

        noDataValue = entrada.GetRasterBand(k).GetNoDataValue()

        if(valueOff.size > 0):
            mask = numpy.logical_and(mask, dados[k] != valueOff)

        mask = numpy.logical_and(mask, dados[k] != noDataValue)

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

numpy.seterr(all='ignore')

#----------

ndvi = numpy.choose(mask, (noValue, (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)))

saidaImagem('ndvi',ndvi)

#----------

savi = numpy.choose(mask, (noValue, ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))))

saidaImagem('savi',savi)

reflectanciaB4 = None
reflectanciaB3 = None

#----------

mask1 = numpy.logical_and(((0.69 - savi) / 0.59) > 0, mask)

iaf = numpy.choose(mask1, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))

saidaImagem('iaf',iaf)

mask1 = None
savi = None

#----------

albedoSuperficie = numpy.choose(mask, (noValue, (albedoPlanetario - ap) * p2))

saidaImagem('albedoSuperficie',albedoSuperficie)

albedoPlanetario = None

#----------

ENB = 0.97 + 0.00331 * iaf
E0 = 0.95 + 0.01 * iaf

mask1 = iaf >= 3

ENB = numpy.choose(mask1, (ENB, 0.98))
E0 = numpy.choose(mask1, (E0, 0.98))

mask1 = ndvi < 0

ENB = numpy.choose(mask1, (ENB, 0.99))
E0 = numpy.choose(mask1, (E0, 0.985))

mask1 = None
iaf = None

#----------

mask1 = numpy.logical_and((((ENB * K1) / radianciaB6) + 1) > 0, mask)

temperaturaSuperficie = numpy.choose(mask1, (noValue, K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)))

saidaImagem('temperaturaSuperficie',temperaturaSuperficie)

mask1 = None
radianciaB6 = None
ENB = None

#----------

numpy.seterr(all='warn')

#----------

radOndaLongaEmi = (E0 * constSB) * numpy.power(temperaturaSuperficie,4)

saldoRadiacao = numpy.choose(mask, (noValue, radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci))

saidaImagem('saldoRadiacao',saldoRadiacao)

E0 = None
radOndaLongaEmi = None

#----------

mask1 = ndvi < 0

fluxoCalSolo = numpy.choose(mask1, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * numpy.power(ndvi,4)))) * saldoRadiacao, G))

mask1 = None

fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))

saidaImagem('fluxoCalSolo',fluxoCalSolo)

ndvi = None

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

#----------

limSupEsq = numpy.mean(limSupEsq)
limInfEsq = numpy.mean(limInfEsq)

limSupDir = numpy.mean(limSupDir)
limInfDir = numpy.mean(limInfDir)

x1 = 0.1
x2 = albedoSupMax
x2x1 = x2 - x1

m1 = (limSupDir - limSupEsq) / x2x1
m2 = (limInfDir - limInfEsq) / x2x1

c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1

#----------

fracaoEvaporativa = numpy.choose(mask, (noValue, (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie)\
                                        / ((c1 - c2) + ((m1 - m2) * albedoSuperficie))))

saidaImagem('fracaoEvaporativa',fracaoEvaporativa)

albedoSuperficie = None
temperaturaSuperficie = None

#----------

fluxoCalorSensivel = numpy.choose(mask, (noValue, (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)))

saidaImagem('fluxoCalorSensivel',fluxoCalorSensivel)

fluxoCalorSensivel = None

#----------

fluxoCalorLatente = numpy.choose(mask, (noValue, fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)))

saidaImagem('fluxoCalorLatente',fluxoCalorLatente)

mask = None
fluxoCalorLatente = None
saldoRadiacao = None
fluxoCalSolo = None
fracaoEvaporativa = None

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
