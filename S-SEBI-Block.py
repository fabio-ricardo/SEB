#coding: utf-8
import gdal, osgeo, time, numpy, sys, math
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

print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driverEntrada.ShortName

#----------

pi = math.pi
cosZ = math.cos((pi/2)-56.98100422) # pego do cabeçalho da imagem - SUN_ELEVATION
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
Ea = 0.85 * numpy.power(-1 * numpy.log(tsw),0.09)
Ta = 295
radOndaLongaInci = Ea * constSB * (Ta*Ta*Ta*Ta)
x1 = 0.1
x2 = 0.9
x2x1 = x2 - x1

#----------

saidaAlbedoSuper = driver.Create('albedoSuperficie.tif',colunas,linhas,1,GDT_Float64)
if saidaAlbedoSuper is None:
    print 'Erro ao criar o arquivo: ' + 'albedoSuperficie.tif'
    sys.exit(1)

saidaNDVI = driver.Create('ndvi.tif',colunas,linhas,1,GDT_Float64)
if saidaNDVI is None:
    print 'Erro ao criar o arquivo: ' + 'ndvi.tif'
    sys.exit(1)

saidaSAVI = driver.Create('savi.tif',colunas,linhas,1,GDT_Float64)
if saidaSAVI is None:
    print 'Erro ao criar o arquivo: ' + 'savi.tif'
    sys.exit(1)

saidaIAF = driver.Create('iaf.tif',colunas,linhas,1,GDT_Float64)
if saidaIAF is None:
    print 'Erro ao criar o arquivo: ' + 'iaf.tif'
    sys.exit(1)

saidaTempSuper = driver.Create('temperatura_superficie.tif',colunas,linhas,1,GDT_Float64)
if saidaTempSuper is None:
    print 'Erro ao criar o arquivo: ' + 'temperatura_superficie.tif'
    sys.exit(1)

saidaSaldoRad = driver.Create('saldoRadiacao.tif',colunas,linhas,1,GDT_Float64)
if saidaSaldoRad is None:
    print 'Erro ao criar o arquivo: ' + 'saldoRadiacao.tif'
    sys.exit(1)

saidaFluxoCalSolo = driver.Create('fluxoCalorSolo.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxoCalSolo is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSolo.tif'
    sys.exit(1)

#----------

bandaEntrada = numpy.empty([NBandas+1],dtype=osgeo.gdal.Band)
bandaEntrada[0] = 0
p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
p1[0] = 0

# ----------

for k in range(1,NBandas+1):
    bandaEntrada[k] = entrada.GetRasterBand(k)

    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr) # pi / (ki * cosZ * dr)

bandaAlbedoSuper = saidaAlbedoSuper.GetRasterBand(1)
bandaNDVI = saidaNDVI.GetRasterBand(1)
bandaSAVI = saidaSAVI.GetRasterBand(1)
bandaIAF = saidaIAF.GetRasterBand(1)
bandaTempSuper = saidaTempSuper.GetRasterBand(1)
bandaSaldoRad = saidaSaldoRad.GetRasterBand(1)
bandaFluxoCalSolo = saidaFluxoCalSolo.GetRasterBand(1)

#----------

xBlockSize = 256
yBlockSize = 256

numpy.seterr(all='ignore')

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

        dados = numpy.empty([NBandas+1,lerLinhas,lerColunas],dtype=numpy.float64)
        dados[0] = 0

        for k in range(1,NBandas+1):
            dados[k] = bandaEntrada[k].ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float64)

        #----------

        albedoPlanetrio = 0

        for k in range(1,NBandas+1):
            if (k == 6):
                radianciaB6 = descBandas[k][3] + (descBandas[k][6] * dados[k])
            else:
                radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k]) # ai+(bi-ai/255)*ND-radiância espectral
                reflectancia = p1[k] * radiancia

                if (k == 3):
                    reflectanciaB3 = reflectancia
                if (k == 4):
                    reflectanciaB4 = reflectancia

                albedoPlanetrio = albedoPlanetrio + (descBandas[k][7] * reflectancia)

        dados = None
        radiancia = None
        reflectancia = None

        ndvi = (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)
        bandaNDVI.WriteArray(ndvi,j,i)

        albedoSuperficie = (albedoPlanetrio - ap) * p2
        bandaAlbedoSuper.WriteArray(albedoSuperficie,j,i)

        albedoPlanetrio = None

        savi = ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))
        bandaSAVI.WriteArray(savi,j,i)

        reflectanciaB4 = None
        reflectanciaB3 = None

        iaf = -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)
        bandaIAF.WriteArray(iaf,j,i)

        savi = None

        ENB = 0.97 + 0.00331 * iaf
        E0 = 0.95 + 0.01* iaf

        iaf = None

        temperaturaSuperficie = K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)
        bandaTempSuper.WriteArray(temperaturaSuperficie,j,i)

        radianciaB6 = None
        ENB = None

        radOndaLongaEmi = (E0 * constSB) * (temperaturaSuperficie*temperaturaSuperficie*\
                                            temperaturaSuperficie*temperaturaSuperficie)

        saldoRadiacao = radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci
        bandaSaldoRad.WriteArray(saldoRadiacao,j,i)

        E0 = None
        radOndaLongaEmi = None

        fluxoCalSolo = ((temperaturaSuperficie - 273.15) *\
                       (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * (ndvi*ndvi*ndvi*ndvi)))) * saldoRadiacao
        bandaFluxoCalSolo.WriteArray(fluxoCalSolo,j,i)

        ndvi = None

        #----------

        maskAlbedoSuper = albedoSuperficie <= 0.2
        limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = albedoSuperficie >= 0.75
        limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = None

        limSupEsq = 0.0
        limInfEsq = 0.0

        limSupDir = 0.0
        limInfDir = 0.0

        for l in range(20):
            aux = numpy.nanargmax(limiteLadoEsq)
            limSupEsq = limSupEsq + limiteLadoEsq[aux]
            limiteLadoEsq[aux] = numpy.nan

            aux = numpy.nanargmin(limiteLadoEsq)
            limInfEsq = limInfEsq + limiteLadoEsq[aux]
            limiteLadoEsq[aux] = numpy.nan

            #----------

            aux = numpy.nanargmax(limiteLadoDir)
            limSupDir = limSupDir + limiteLadoDir[aux]
            limiteLadoDir[aux] = numpy.nan

            aux = numpy.nanargmin(limiteLadoDir)
            limInfDir = limInfDir + limiteLadoDir[aux]
            limiteLadoDir[aux] = numpy.nan

        limiteLadoEsq = None
        limiteLadoDir = None

        limSupEsq = limSupEsq / 20
        limInfEsq = limInfEsq / 20

        limSupDir = limSupDir / 20
        limInfDir = limInfDir / 20

        #----------

        temperaturaSuperficie = None
        saldoRadiacao = None
        albedoSuperficie = None
        fluxoCalSolo = None

        #----------

numpy.seterr(all='warn')

#----------

bandaEntrada = None
entrada = None
bandaAlbedoSuper = None
saidaAlbedoSuper = None
bandaNDVI = None
saidaNDVI = None
bandaSAVI = None
saidaSAVI = None
bandaIAF = None
saidaIAF = None
bandaTempSuper = None
saidaTempSuper = None
bandaSaldoRad = None
saidaSaldoRad = None
bandaFluxoCalSolo = None
saidaFluxoCalSolo = None

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
