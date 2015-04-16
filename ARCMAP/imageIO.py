#coding:utf-8

import arcpy
import numpy

#----------

def abrirELer(endArquivo,nomeImagem):
    return arcpy.RasterToNumPyArray(endArquivo+nomeImagem)

#----------

def salvar(nomeImagem,retorno,nomesRet,endArquivo,extensaoImg):
    projecao = arcpy.Describe(endArquivo+nomeImagem).spatialReference
    noValue = -9999.0

    def salvarImagem(nome,calculo):
        imagem = arcpy.NumPyArrayToRaster(calculo,value_to_nodata=noValue)
        imagem.save(r''+endArquivo+nome+extensaoImg)

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