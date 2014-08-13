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

bandaEntrada = numpy.empty([NBandas+1],dtype=osgeo.gdal.Band)

p1 = numpy.zeros([NBandas+1],dtype=numpy.float32)

#----------

for k in xrange(1,NBandas+1):
    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr)

    bandaEntrada[k] = entrada.GetRasterBand(k)

#----------

pastaSaida = 'SSEB-Block__'+nomeArquivoEntrada+'/'

try:
    os.mkdir(pastaSaida)
except:
    print 'Diretorio: ' + pastaSaida + ' Já existe.'
    print 'Recriando arquivos, se existir.'

#----------

def criarImagem(nome):
    saida = driver.Create(pastaSaida+nome+extensao,colunas,linhas,1,GDT_Float32)
    if saida is None:
        print 'Erro ao criar o arquivo: ' + nome+extensao
        sys.exit(1)
    saida.SetProjection(projecao)

    return saida, saida.GetRasterBand(1)

#----------

def fecharImagem(nome, banda):
    banda.SetNoDataValue(noValue)

    print nome+' - Pronto!'

    return None, None

#----------

saidaNDVI, bandaNDVI = criarImagem('ndvi')

saidaSAVI, bandaSAVI = criarImagem('savi')

saidaIAF, bandaIAF = criarImagem('iaf')

saidaAlbedoSuper, bandaAlbedoSuper = criarImagem('albedoSuperficie')

saidaTempSuper, bandaTempSuper = criarImagem('temperaturaSuperficie')

saidaSaldoRad, bandaSaldoRad = criarImagem('saldoRadiacao')

saidaFluxoCalSolo, bandaFluxoCalSolo = criarImagem('fluxoCalorSolo')

#----------

hotNdvi = numpy.array([],dtype=numpy.float32)
coldTemp = numpy.array([],dtype=numpy.float32)

coldNdvi = numpy.array([],dtype=numpy.float32)
hotTemp = numpy.array([],dtype=numpy.float32)

#----------

numpy.seterr(all='ignore')

#----------

xBlockSize = 256
yBlockSize = 256

#----------

for i in xrange(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in xrange(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        dados = numpy.empty([NBandas+1],dtype=numpy.ndarray)

        albedoPlanetario = 0

        for k in xrange(1,NBandas+1):
            dados[k] = bandaEntrada[k].ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float32)
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

        mask = numpy.choose(mask,(True,False))

        #----------

        valueOff = None
        dados = None

        #----------

        ndvi = numpy.choose(mask, (noValue, (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)))
        bandaNDVI.WriteArray(ndvi,j,i)

        #----------

        savi = numpy.choose(mask, (noValue, ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))))
        bandaSAVI.WriteArray(savi,j,i)

        reflectanciaB4 = None
        reflectanciaB3 = None

        #----------

        mask1 = numpy.logical_and(((0.69 - savi) / 0.59) > 0, mask)

        iaf = numpy.choose(mask1, (noValue, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))
        bandaIAF.WriteArray(iaf,j,i)

        mask1 = None

        #----------

        albedoSuperficie = numpy.choose(mask, (noValue, (albedoPlanetario - ap) * p2))
        bandaAlbedoSuper.WriteArray(albedoSuperficie,j,i)

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
        bandaTempSuper.WriteArray(temperaturaSuperficie,j,i)

        radianciaB6 = None
        ENB = None

        #----------

        radOndaLongaEmi = (E0 * constSB) * numpy.power(temperaturaSuperficie,4)

        saldoRadiacao = numpy.choose(mask, (noValue, ((1.0 - albedoSuperficie) * radOndaCurtaInci) +\
                                    (E0 * radOndaLongaInci - radOndaLongaEmi)))

        bandaSaldoRad.WriteArray(saldoRadiacao,j,i)

        E0 = None
        radOndaLongaEmi = None

        #----------

        mask1 = ndvi < 0

        fluxoCalSolo = numpy.choose(mask1, (((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1.0 - (0.98 * numpy.power(ndvi,4)))) * saldoRadiacao, G))

        mask1 = None

        fluxoCalSolo = numpy.choose(mask, (noValue, fluxoCalSolo))
        bandaFluxoCalSolo.WriteArray(fluxoCalSolo,j,i)

        albedoSuperficie = None
        saldoRadiacao = None
        fluxoCalSolo = None

        #----------

        temperaturaSuperficie.reshape(-1)
        ndvi.reshape(-1)

        temperaturaSuperficie = temperaturaSuperficie[mask]

        ndviHot = ndvi[mask]
        ndviCold = ndvi[mask]

        mask = None
        ndvi = None

        if(temperaturaSuperficie.size > 0):
            hotNdviAux = numpy.array([],dtype=numpy.float32)
            coldTempAux = numpy.array([],dtype=numpy.float32)

            coldNdviAux = numpy.array([],dtype=numpy.float32)
            hotTempAux = numpy.array([],dtype=numpy.float32)

            qtdPontosPegar = qtdPontos

            if(temperaturaSuperficie.size < qtdPontos):
                qtdPontosPegar = temperaturaSuperficie.size

            for n in xrange(qtdPontosPegar):
                if hotNdviAux.size < qtdPontosPegar:
                    tempNdviIgual = numpy.array([])

                    hotNdviAux = numpy.append(hotNdviAux,ndviHot[numpy.nanargmax(ndviHot)])
                    tempNdviIgual = numpy.append(tempNdviIgual,temperaturaSuperficie[numpy.nanargmax(ndviHot)])
                    ndviHot[numpy.nanargmax(ndviHot)] = numpy.nan
                    tamNdvi = ndviHot.size - 1

                    if(tamNdvi > 0):
                        prox = numpy.nanargmax(ndviHot)

                        posUlt = hotNdviAux.size-1

                        while(tamNdvi > 0 and hotNdviAux[posUlt] == ndviHot[prox]):
                            tempNdviIgual = numpy.append(tempNdviIgual,temperaturaSuperficie[prox])

                            ndviHot[prox] = numpy.nan
                            tamNdvi = tamNdvi-1

                            if(tamNdvi > 0):
                                prox = numpy.nanargmax(ndviHot)

                    if tempNdviIgual.size > 1:
                        tempNdviIgual = numpy.sort(tempNdviIgual)

                        tamTempNdviIg = tempNdviIgual.size
                        if tamTempNdviIg > (qtdPontosPegar - posUlt):
                            tamTempNdviIg = qtdPontosPegar - posUlt

                        coldTempAux = numpy.append(coldTempAux,tempNdviIgual[:tamTempNdviIg])

                        for j in xrange(tamTempNdviIg-1):
                            hotNdviAux = numpy.append(hotNdviAux,hotNdviAux[posUlt])

                    else:
                        coldTempAux = numpy.append(coldTempAux,tempNdviIgual[0])

                    tempNdviIgual = None

                if coldNdviAux.size < qtdPontosPegar:
                    tempNdviIgual = numpy.array([])

                    coldNdviAux = numpy.append(coldNdviAux,ndviCold[numpy.nanargmin(ndviCold)])
                    tempNdviIgual = numpy.append(tempNdviIgual,temperaturaSuperficie[numpy.nanargmin(ndviCold)])
                    ndviCold[numpy.nanargmin(ndviCold)] = numpy.nan
                    tamNdvi = ndviCold.size - 1

                    if(tamNdvi > 0):
                        prox = numpy.nanargmin(ndviCold)

                        posUlt = coldNdviAux.size-1

                        while(tamNdvi > 0 and coldNdviAux[posUlt] == ndviCold[prox]):
                            tempNdviIgual = numpy.append(tempNdviIgual,temperaturaSuperficie[prox])

                            ndviCold[prox] = numpy.nan
                            tamNdvi = tamNdvi-1

                            if(tamNdvi > 0):
                                prox = numpy.nanargmin(ndviCold)

                    if tempNdviIgual.size > 1:
                        tempNdviIgual = numpy.sort(tempNdviIgual)[::-1]

                        tamTempNdviIg = tempNdviIgual.size
                        if tamTempNdviIg > (qtdPontosPegar - posUlt):
                            tamTempNdviIg = qtdPontosPegar - posUlt

                        hotTempAux = numpy.append(hotTempAux,tempNdviIgual[:tamTempNdviIg])

                        for j in xrange(tamTempNdviIg-1):
                            coldNdviAux = numpy.append(coldNdviAux,coldNdviAux[posUlt])

                    else:
                        hotTempAux = numpy.append(hotTempAux,tempNdviIgual[0])

                    tempNdviIgual = None

            if(hotNdvi.size > 0):
                for n in xrange(hotNdvi.size):
                    for m in xrange(hotNdviAux.size):
                        if(hotNdvi[n] < hotNdviAux[m]):
                            hotNdvi = numpy.insert(hotNdvi,0,hotNdviAux[m])
                            coldTemp = numpy.insert(coldTemp,0,coldTempAux[m])

                            hotNdviAux = numpy.delete(hotNdviAux,m)
                            coldTempAux = numpy.delete(coldTempAux,m)

                            if(hotNdvi.size > qtdPontos):
                                hotNdvi = numpy.delete(hotNdvi,qtdPontos)
                                coldTemp = numpy.delete(coldTemp,qtdPontos)

                        elif(hotNdvi[n] == hotNdviAux[m]):
                            if(coldTemp[n] > coldTempAux[m]):
                                coldTemp[n] = coldTempAux[m]

                                hotNdviAux = numpy.delete(hotNdviAux,m)
                                coldTempAux = numpy.delete(coldTempAux,m)
                        break
            else:
                hotNdvi = hotNdviAux
                coldTemp = coldTempAux

            if(coldNdvi.size > 0):
                for n in xrange(coldNdvi.size):
                    for m in xrange(coldNdviAux.size):
                        if(coldNdvi[n] > coldNdviAux[m]):
                            coldNdvi = numpy.insert(coldNdvi,0,coldNdviAux[m])
                            hotTemp = numpy.insert(hotTemp,0,hotTempAux[m])

                            coldNdviAux = numpy.delete(coldNdviAux,m)
                            hotTempAux = numpy.delete(hotTempAux,m)

                            if(coldNdvi.size > qtdPontos):
                                coldNdvi = numpy.delete(coldNdvi,qtdPontos)
                                hotTemp = numpy.delete(hotTemp,qtdPontos)

                        elif(coldNdvi[n] == coldNdviAux[m]):
                            if(hotTemp[n] < hotTempAux[m]):
                                hotTemp[n] = hotTempAux[m]

                                coldNdviAux = numpy.delete(coldNdviAux,m)
                                hotTempAux = numpy.delete(hotTempAux,m)
                        break
            else:
                coldNdvi = coldNdviAux
                hotTemp = hotTempAux

        ndviHot = None
        ndviCold = None
        temperaturaSuperficie = None

        #----------

#----------

numpy.seterr(all='warn')

#----------

bandaEntrada = None
entrada = None

#----------

saidaNDVI, bandaNDVI = fecharImagem('ndvi',bandaNDVI)

#----------

saidaSAVI, bandaSAVI = fecharImagem('savi',bandaSAVI)

#----------

saidaIAF, bandaIAF = fecharImagem('iaf',bandaIAF)

#----------

TH = numpy.mean(hotTemp)
TC = numpy.mean(coldTemp)

#----------

saidaFracEvapo, bandaFracEvapo = criarImagem('fracaoEvaporativa')

saidaFluxCalSensi, bandaFluxCalSensi = criarImagem('fluxoCalorSensivel')

saidaFluxCalLaten, bandaFluxCalLaten = criarImagem('fluxoCalorLatente')

saidaEvapoTrans24h, bandaEvapoTrans24h = criarImagem('evapotranspiracao24h')

#----------

for i in xrange(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in xrange(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        temperaturaSuperficie = bandaTempSuper.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        mask = temperaturaSuperficie != noValue

        #----------

        fracaoEvaporativa = numpy.choose(mask, (noValue, (TH - temperaturaSuperficie) / (TH - TC)))
        bandaFracEvapo.WriteArray(fracaoEvaporativa,j,i)

        temperaturaSuperficie = None

        #----------

        saldoRadiacao = bandaSaldoRad.ReadAsArray(j,i,lerColunas,lerLinhas)
        fluxoCalSolo = bandaFluxoCalSolo.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        fluxoCalorSensivel = numpy.choose(mask, (noValue, (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)))
        bandaFluxCalSensi.WriteArray(fluxoCalorSensivel,j,i)

        fluxoCalorSensivel = None

        #----------

        fluxoCalorLatente = numpy.choose(mask, (noValue, fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)))
        bandaFluxCalLaten.WriteArray(fluxoCalorLatente,j,i)

        #----------

        albedoSuperficie = bandaAlbedoSuper.ReadAsArray(j,i,lerColunas,lerLinhas)

        #----------

        evapotranspiracao24h = numpy.choose(mask, (noValue, (fracaoEvaporativa * (Rg24h * (1.0 - albedoSuperficie)\
                                                    - 110.0 * Tao24h) * 86.4) / 2450.0))
        bandaEvapoTrans24h.WriteArray(evapotranspiracao24h,j,i)

        #----------

        mask = None
        evapotranspiracao24h = None
        fluxoCalorLatente = None
        fracaoEvaporativa = None
        fluxoCalSolo = None
        saldoRadiacao = None
        albedoSuperficie = None

        #----------

#----------

saidaAlbedoSuper, bandaAlbedoSuper = fecharImagem('albedoSuperficie',bandaAlbedoSuper)

saidaTempSuper, bandaTempSuper = fecharImagem('temperaturaSuperficie',bandaTempSuper)

saidaSaldoRad, bandaSaldoRad = fecharImagem('saldoRadiacao',bandaSaldoRad)

saidaFluxoCalSolo, bandaFluxoCalSolo = fecharImagem('fluxoCalSolo',bandaFluxoCalSolo)

saidaFracEvapo, bandaFracEvapo = fecharImagem('fracaoEvaporativa',bandaFracEvapo)

saidaFluxCalSensi, bandaFluxCalSensi = fecharImagem('fluxoCalorSensivel',bandaFluxCalSensi)

saidaFluxCalLaten, bandaFluxCalLaten = fecharImagem('fluxoCalorLatente',bandaFluxCalLaten)

saidaEvapoTrans24h, bandaEvapoTrans24h = fecharImagem('evapotranspiracao24h',bandaEvapoTrans24h)

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
