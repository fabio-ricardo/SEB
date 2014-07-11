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
tsw = (0.75 + 2*0.00001 * z) * (0.75 + 2*0.00001 * z)
p2 = 1 / tsw
L = 0.5
#----------

saidaAlbedoSuperficie = driver.Create('albedoSuperficie.tif',colunas,linhas,1,GDT_Float64)
if saidaAlbedoSuperficie is None:
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

bandaEntrada = numpy.empty([NBandas+1],dtype=osgeo.gdal.Band)
bandaEntrada[0] = 0
p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
p1[0] = 0

for k in range(1,NBandas+1):
    bandaEntrada[k] = entrada.GetRasterBand(k)

    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr) # pi / (ki * cosZ * dr)

bandaAlbedoSuper = saidaAlbedoSuperficie.GetRasterBand(1)
bandaNDVI = saidaNDVI.GetRasterBand(1)
bandaSAVI = saidaSAVI.GetRasterBand(1)
bandaIAF = saidaIAF.GetRasterBand(1)

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

        dados = numpy.empty([NBandas+1,lerLinhas,lerColunas],dtype=numpy.float64)
        dados[0] = 0

        for k in range(1,NBandas+1):
            dados[k] = bandaEntrada[k].ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float64)

        #----------

        albedoPlanetrio = 0

        for k in range(1,NBandas+1):
            if (k != 6):
                radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k]) # ai+(bi-ai/255)*ND-radiância espectral
                reflectancia = p1[k] * radiancia

                if (k == 3):
                    reflectanciaB3 = reflectancia
                if (k == 4):
                    reflectanciaB4 = reflectancia

                albedoPlanetrio = albedoPlanetrio + (descBandas[k][7] * reflectancia)

        albedoSuperficie = (albedoPlanetrio - ap) * p2

        bandaAlbedoSuper.WriteArray(albedoSuperficie,j,i)

        ndvi = (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)

        bandaNDVI.WriteArray(ndvi,j,i)

        savi = ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))

        bandaSAVI.WriteArray(savi,j,i)

        mask = ((0.69 - savi) / 0.59) > 0

        iaf = numpy.choose(mask, (0, -1 * (numpy.log(((0.69 - savi) / 0.59) +(((0.69 - savi) / 0.59) <= 0)) / 0.91)))

        bandaIAF.WriteArray(iaf,j,i)
        #----------

bandaEntrada = None
entrada = None
bandaAlbedoSuper = None
saidaAlbedoSuperficie = None
bandaNDVI = None
saidaNDVI = None
bandaSAVI = None
saidaSAVI = None
bandaIAF = None
saidaIAF = None

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
