#coding: utf-8
import gdal, time, numpy, sys, math
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
driver = entrada.GetDriver()

print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driver.ShortName

#----------
pi = math.pi
cosZ = math.cos((pi/2)-56.98100422) # pego do cabeçalho da imagem - SUN_ELEVATION
dr = 1+0.033*math.cos((272*2*pi)/365) # 29 de setembro de 2011
#----------

xBlockSize = 256
yBlockSize = 256

for k in range(1,NBandas+1):
    saidaRadiancia = driver.Create('radiancia_espectral_B'+str(k)+'.tif',colunas,linhas,1,GDT_Float64)
    if saidaRadiancia is None:
        print 'Erro ao criar o arquivo: ' + 'radiancia_espectral_B'+str(k)+'.tif'
        sys.exit(1)

    if (k != 6):
        p1 = pi / descBandas[k][5] * cosZ * dr # pi / (ki * cosZ * dr)

        saidaReflectancia = driver.Create('reflectancia_B'+str(k)+'.tif',colunas,linhas,1,GDT_Float64)
        if saidaReflectancia is None:
            print 'Erro ao criar o arquivo: ' + 'reflectancia_B'+str(k)+'.tif'
            sys.exit(1)

        bandaReflectancia = saidaReflectancia.GetRasterBand(1)

    bandaEntrada = entrada.GetRasterBand(k)
    bandaRadiancia = saidaRadiancia.GetRasterBand(1)

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
            radiancia = bandaEntrada.ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float64)
            #----------

            radiancia = descBandas[k][3] + (descBandas[k][6] * radiancia) # ai + (bi-ai/255) * ND - radiância espectral

            if (k != 6):
                reflectancia = p1 * radiancia

                bandaReflectancia.WriteArray(reflectancia,j,i)


            bandaRadiancia.WriteArray(radiancia,j,i)
            #----------

    bandaEntrada = None
    bandaRadiancia = None
    bandaReflectancia = None
    saidaRadiancia = None
    saidaReflectancia = None

entrada = None

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos'
