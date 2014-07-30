#coding: utf-8
import gdal, osgeo, time, numpy, sys, math, os
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
albedoSupMax = 0
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

#----------

pastaSaida = 'S-SEBI-Block__'+nomeArquivoEntrada+'/'

try:
    os.mkdir(pastaSaida)
except:
    print 'Diretorio: ' + pastaSaida + ' Já existe.'
    print 'Recriando arquivos, se existir.'

#----------

saidaNDVI = driver.Create(pastaSaida+'ndvi.tif',colunas,linhas,1,GDT_Float32)
if saidaNDVI is None:
    print 'Erro ao criar o arquivo: ' + 'ndvi.tif'
    sys.exit(1)
saidaNDVI.SetProjection(projecao)

saidaSAVI = driver.Create(pastaSaida+'savi.tif',colunas,linhas,1,GDT_Float32)
if saidaSAVI is None:
    print 'Erro ao criar o arquivo: ' + 'savi.tif'
    sys.exit(1)
saidaSAVI.SetProjection(projecao)

saidaIAF = driver.Create(pastaSaida+'iaf.tif',colunas,linhas,1,GDT_Float32)
if saidaIAF is None:
    print 'Erro ao criar o arquivo: ' + 'iaf.tif'
    sys.exit(1)
saidaIAF.SetProjection(projecao)

saidaAlbedoSuper = driver.Create(pastaSaida+'albedoSuperficie.tif',colunas,linhas,1,GDT_Float32)
if saidaAlbedoSuper is None:
    print 'Erro ao criar o arquivo: ' + 'albedoSuperficie.tif'
    sys.exit(1)
saidaAlbedoSuper.SetProjection(projecao)

saidaTempSuper = driver.Create(pastaSaida+'temperaturaSuperficie.tif',colunas,linhas,1,GDT_Float32)
if saidaTempSuper is None:
    print 'Erro ao criar o arquivo: ' + 'temperaturaSuperficie.tif'
    sys.exit(1)
saidaTempSuper.SetProjection(projecao)

saidaSaldoRad = driver.Create(pastaSaida+'saldoRadiacao.tif',colunas,linhas,1,GDT_Float32)
if saidaSaldoRad is None:
    print 'Erro ao criar o arquivo: ' + 'saldoRadiacao.tif'
    sys.exit(1)
saidaSaldoRad.SetProjection(projecao)

saidaFluxoCalSolo = driver.Create(pastaSaida+'fluxoCalorSolo.tif',colunas,linhas,1,GDT_Float32)
if saidaFluxoCalSolo is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSolo.tif'
    sys.exit(1)
saidaFluxoCalSolo.SetProjection(projecao)

#----------

bandaEntrada = numpy.empty([NBandas+1],dtype=osgeo.gdal.Band)
bandaEntrada[0] = 0
p1 = numpy.empty([NBandas+1],dtype=numpy.float32)
p1[0] = 0
p1[6] = 0

limSupEsq = numpy.zeros([qtdPontos],dtype=numpy.float32)
limInfEsq = numpy.zeros([qtdPontos],dtype=numpy.float32)
limEsqPVez = True

limSupDir = numpy.zeros([qtdPontos],dtype=numpy.float32)
limInfDir = numpy.zeros([qtdPontos],dtype=numpy.float32)
limDirPVez = True

# ----------

for k in range(1,NBandas+1):
    bandaEntrada[k] = entrada.GetRasterBand(k)

    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr)

bandaAlbedoSuper = saidaAlbedoSuper.GetRasterBand(1)
bandaNDVI = saidaNDVI.GetRasterBand(1)
bandaSAVI = saidaSAVI.GetRasterBand(1)
bandaIAF = saidaIAF.GetRasterBand(1)
bandaTempSuper = saidaTempSuper.GetRasterBand(1)
bandaSaldoRad = saidaSaldoRad.GetRasterBand(1)
bandaFluxoCalSolo = saidaFluxoCalSolo.GetRasterBand(1)

#----------

numpy.seterr(all='ignore')

#----------

xBlockSize = 256
yBlockSize = 256

for i in range(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in range(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        dados = numpy.empty([NBandas+1,lerLinhas,lerColunas],dtype=numpy.float32)
        dados[0] = 0

        albedoPlanetario = 0
        maskAlbPlan = 1

        for k in range(1,NBandas+1):
            dados[k] = bandaEntrada[k].ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)

            if (k == 6):
                radianciaB6 = descBandas[k][3] + (descBandas[k][6] * dados[k])
                maskB6 = dados[k] > 0
            else:
                radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])
                reflectancia = p1[k] * radiancia

                if (k == 3):
                    dados3 = dados[k]
                if (k == 4):
                    dados4 = dados[k]

                albedoPlanetario += descBandas[k][7] * reflectancia

                maskAlbPlan = numpy.logical_and(maskAlbPlan,dados[k] > 0)

        dados = None
        radiancia = None
        reflectancia = None

        #----------

        mask = numpy.logical_and(dados3 > 0, dados4 > 0)

        ndvi = numpy.choose(mask, (noValue, (dados4 - dados3) / (dados4 + dados3)))
        bandaNDVI.WriteArray(ndvi,j,i)

        #----------

        savi = numpy.choose(mask, (noValue, ((1 + L) * (dados4 - dados3)) / (L + (dados4 + dados3))))
        bandaSAVI.WriteArray(savi,j,i)

        mask = None
        dados4 = None
        dados3 = None

        #----------

        mask = numpy.logical_and(((0.69 - savi) / 0.59) > 0, savi != noValue)

        iaf = numpy.choose(mask, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))
        bandaIAF.WriteArray(iaf,j,i)

        mask = None
        savi = None

        #----------

        albedoSuperficie = numpy.choose(maskAlbPlan, (noValue, (albedoPlanetario - ap) * p2))

        mask = numpy.logical_and(albedoSuperficie < 0, albedoSuperficie != noValue)

        albedoSuperficie = numpy.choose(mask, (albedoSuperficie, 0.0))

        bandaAlbedoSuper.WriteArray(albedoSuperficie,j,i)

        mask = None
        maskAlbPlan = None
        albedoPlanetario = None

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

        mask = numpy.logical_and(ENB != noValue, maskB6)

        temperaturaSuperficie = numpy.choose(mask, (noValue, K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)))
        bandaTempSuper.WriteArray(temperaturaSuperficie,j,i)

        maskB6 = None
        mask = None
        radianciaB6 = None
        ENB = None

        #----------

        radOndaLongaEmi = (E0 * constSB) * (temperaturaSuperficie*temperaturaSuperficie*\
                                            temperaturaSuperficie*temperaturaSuperficie)

        mask = numpy.logical_and(temperaturaSuperficie != noValue, albedoSuperficie != noValue)

        saldoRadiacao = numpy.choose(mask, (noValue, radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci))

        bandaSaldoRad.WriteArray(saldoRadiacao,j,i)

        E0 = None
        radOndaLongaEmi = None

        #----------

        maska = ndvi < 0

        fluxoCalSolo = numpy.choose(maska, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * (ndvi*ndvi*ndvi*ndvi)))) * saldoRadiacao, G))

        maska = None

        mask = numpy.logical_and(mask, ndvi != noValue)

        fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))
        bandaFluxoCalSolo.WriteArray(fluxoCalSolo,j,i)

        mask = None
        ndvi = None
        saldoRadiacao = None
        fluxoCalSolo = None

        #----------

        if numpy.amax(albedoSuperficie) > albedoSupMax:
            albedoSupMax = numpy.amax(albedoSuperficie)

        #----------

#----------

numpy.seterr(all='warn')

#----------

bandaEntrada = None
entrada = None

bandaNDVI.SetNoDataValue(noValue)
bandaNDVI = None
saidaNDVI = None

print 'NDVI - Pronto'

bandaSAVI.SetNoDataValue(noValue)
bandaSAVI = None
saidaSAVI = None

print 'SAVI - Pronto'

bandaIAF.SetNoDataValue(noValue)
bandaIAF = None
saidaIAF = None

print 'IAF - Pronto'

#----------

for i in range(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in range(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        albedoSuperficie = bandaAlbedoSuper.ReadAsArray(j,i,lerColunas,lerLinhas)
        temperaturaSuperficie = bandaTempSuper.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        maskAlbedoSuper = numpy.logical_and(albedoSuperficie <= (albedoSupMax * 0.2), albedoSuperficie != noValue)
        limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = albedoSuperficie >= (albedoSupMax * 0.8)
        limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = None
        albedoSuperficie = None
        temperaturaSuperficie = None

        mask = limiteLadoEsq != noValue
        limiteLadoEsq = limiteLadoEsq[mask]

        mask = limiteLadoDir != noValue
        limiteLadoDir = limiteLadoDir[mask]

        mask = None

        if (limiteLadoEsq.size > 0):
            if (limEsqPVez):
                limiteLadoEsq = numpy.sort(limiteLadoEsq)
                limSupEsq = limiteLadoEsq[::-1][0:qtdPontos]
                limInfEsq = limiteLadoEsq[0:qtdPontos]
                limEsqPVez = False
            else:
                limSupEsq = numpy.sort(numpy.concatenate((limSupEsq,limiteLadoEsq)))[::-1][0:qtdPontos]
                limInfEsq = numpy.sort(numpy.concatenate((limInfEsq,limiteLadoEsq)))[0:qtdPontos]

        if (limiteLadoDir.size > 0):
            if (limDirPVez):
                limiteLadoDir = numpy.sort(limiteLadoDir)
                limSupDir = limiteLadoDir[::-1][0:qtdPontos]
                limInfDir = limiteLadoDir[0:qtdPontos]
                limDirPVez = False
            else:
                limSupDir = numpy.sort(numpy.concatenate((limSupDir,limiteLadoDir)))[::-1][0:qtdPontos]
                limInfDir = numpy.sort(numpy.concatenate((limInfDir,limiteLadoDir)))[0:qtdPontos]

        limiteLadoEsq = None
        limiteLadoDir = None

        #----------

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

saidaFracEvapo = driver.Create(pastaSaida+'fracaoEvaporativa.tif',colunas,linhas,1,GDT_Float32)
if saidaFracEvapo is None:
    print 'Erro ao criar o arquivo: ' + 'fracaoEvaporativa.tif'
    sys.exit(1)
saidaFracEvapo.SetProjection(projecao)

saidaFluxCalSensi = driver.Create(pastaSaida+'fluxoCalorSensivel.tif',colunas,linhas,1,GDT_Float32)
if saidaFluxCalSensi is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSensivel.tif'
    sys.exit(1)
saidaFluxCalSensi.SetProjection(projecao)

saidaFluxCalLaten = driver.Create(pastaSaida+'fluxoCalorLatente.tif',colunas,linhas,1,GDT_Float32)
if saidaFluxCalLaten is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorLatente.tif'
    sys.exit(1)
saidaFluxCalLaten.SetProjection(projecao)

#----------

bandaFracEvapo = saidaFracEvapo.GetRasterBand(1)
bandaFluxCalSensi = saidaFluxCalSensi.GetRasterBand(1)
bandaFluxCalLaten = saidaFluxCalLaten.GetRasterBand(1)

#----------

for i in range(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in range(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        albedoSuperficie = bandaAlbedoSuper.ReadAsArray(j,i,lerColunas,lerLinhas)
        temperaturaSuperficie = bandaTempSuper.ReadAsArray(j,i,lerColunas,lerLinhas)
        saldoRadiacao = bandaSaldoRad.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        mask = saldoRadiacao != noValue

        fracaoEvaporativa = numpy.choose(mask, (noValue, (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie)\
                                        / ((c1 - c2) + ((m1 - m2) * albedoSuperficie))))
        bandaFracEvapo.WriteArray(fracaoEvaporativa,j,i)

        mask = None
        albedoSuperficie = None
        temperaturaSuperficie = None

        #----------

        fluxoCalSolo = bandaFluxoCalSolo.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        mask = fluxoCalSolo != noValue

        fluxoCalorSensivel = numpy.choose(mask, (noValue, (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)))
        bandaFluxCalSensi.WriteArray(fluxoCalorSensivel,j,i)

        fluxoCalorSensivel = None

        #----------

        fluxoCalorLatente = numpy.choose(mask, (noValue, fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)))
        bandaFluxCalLaten.WriteArray(fluxoCalorLatente,j,i)

        mask = None
        fluxoCalorLatente = None

        #----------

        saldoRadiacao = None
        fluxoCalSolo = None
        fracaoEvaporativa = None

        #----------

#----------

bandaAlbedoSuper.SetNoDataValue(noValue)
bandaAlbedoSuper = None
saidaAlbedoSuper = None

print 'Albedo Superficie - Pronto'

bandaTempSuper.SetNoDataValue(noValue)
bandaTempSuper = None
saidaTempSuper = None

print 'Temperatura Superficie - Pronto'

bandaSaldoRad.SetNoDataValue(noValue)
bandaSaldoRad = None
saidaSaldoRad = None

print 'Saldo Radiação - Pronto'

bandaFluxoCalSolo.SetNoDataValue(noValue)
bandaFluxoCalSolo = None
saidaFluxoCalSolo = None

print 'Fluxo Calor no Solo - Pronto'

bandaFracEvapo.SetNoDataValue(noValue)
bandaFracEvapo = None
saidaFracEvapo = None

print 'Fração Evaporativa - Pronto'

bandaFluxCalSensi.SetNoDataValue(noValue)
bandaFluxCalSensi = None
saidaFluxCalSensi = None

print 'Fluxo Calor Sensivel - Pronto'

bandaFluxCalLaten.SetNoDataValue(noValue)
bandaFluxCalLaten = None
saidaFluxCalLaten = None

print 'Fluxo Calor Latente - Pronto'

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
