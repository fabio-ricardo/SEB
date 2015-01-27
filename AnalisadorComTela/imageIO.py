#coding:utf-8

import gdal, numpy
from gdalconst import *

#----------

def abrir(endArquivo,nomeImagem):
    gdal.AllRegister()

    entrada = gdal.Open(endArquivo+nomeImagem,GA_ReadOnly)
    if entrada is None:
       return False,'Erro ao abrir o arquivo: ' + endArquivo+nomeImagem

    return True,entrada

#----------

def ler(entrada,bSelecionadas):
    nBandas = entrada.RasterCount

    bandas = numpy.empty([nBandas+1],dtype=numpy.ndarray)

    for k in xrange(1,nBandas+1):
        if(k in bSelecionadas):
            bandas[k] = entrada.GetRasterBand(k).ReadAsArray().astype(numpy.float32)

    return bandas

#----------

def salvar(entrada,retorno,nomesRet,endArquivo,extensaoImg):
    linhas = entrada.RasterYSize
    colunas = entrada.RasterXSize
    driverEntrada = entrada.GetDriver()
    projecao = entrada.GetProjection()

    noValue = -9999.0

    driverEntrada.Register()

    def salvarImagem(nome,calculo):
        saida = driverEntrada.Create(endArquivo+nome+extensaoImg,colunas,linhas,1,GDT_Float32)
        if saida is None:
            return False,'Erro ao criar o arquivo: ' + nome+extensaoImg

        saida.SetProjection(projecao)
        banda = saida.GetRasterBand(1)

        banda.WriteArray(calculo,0,0)

        banda.SetNoDataValue(noValue)

        banda = None
        saida = None

        return True,1

    if(type(retorno) == tuple):
        for i in xrange(len(retorno)):
            terminado = salvarImagem(nomesRet[i],retorno[i])

            if(terminado[0] == False):
                return terminado

    elif(type(retorno) == numpy.ndarray):
        terminado = salvarImagem(nomesRet[0],retorno)

        if(terminado[0] == False):
            return terminado

    return True,1

#----------