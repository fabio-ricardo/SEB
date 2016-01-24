#coding:utf-8

import analisadorSintatico as analisador

#----------

from numpy import *

#----------
def fgeo_ssebi(albedoSuperficie, temperaturaSuperficie):
    qtdPontos = 10

    albedoSupMax = amax(albedoSuperficie)

    limiteLadoEsq = temperaturaSuperficie[albedoSuperficie <= (albedoSupMax * 0.2)]

    limiteLadoDir = temperaturaSuperficie[albedoSuperficie >= (albedoSupMax * 0.8)]

    limiteLadoEsq = sort(limiteLadoEsq)
    limiteLadoDir = sort(limiteLadoDir)

    limSupEsq = limiteLadoEsq[::-1][0:qtdPontos]
    limInfEsq = limiteLadoEsq[0:qtdPontos]

    limSupDir = limiteLadoDir[::-1][0:qtdPontos]
    limInfDir = limiteLadoDir[0:qtdPontos]

    limiteLadoEsq = None
    limiteLadoDir = None

    #----------

    limSupEsq = mean(limSupEsq)
    limInfEsq = mean(limInfEsq)

    limSupDir = mean(limSupDir)
    limInfDir = mean(limInfDir)

    x1 = 0.1
    x2 = albedoSupMax
    x2x1 = x2 - x1

    m1 = (limSupDir - limSupEsq) / x2x1
    m2 = (limInfDir - limInfEsq) / x2x1

    c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
    c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1

    return (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie)/((c1 - c2) + ((m1 - m2) * albedoSuperficie))

#----------

def fgeo_sseb(ndvi, temperaturaSuperficie):
    qtdPontos = 100

    hotNdvi = array([],dtype=float32)
    coldTemp = array([],dtype=float32)

    coldNdvi = array([],dtype=float32)
    hotTemp = array([],dtype=float32)

    tempSuperficie = temperaturaSuperficie

    tempSuperficie.reshape(-1)
    ndvi.reshape(-1)

    for i in xrange(qtdPontos):
        if hotNdvi.size < qtdPontos:
            tempNdviIgual = array([])

            hotNdvi = append(hotNdvi,ndvi[nanargmax(ndvi)])
            tempNdviIgual = append(tempNdviIgual,tempSuperficie[nanargmax(ndvi)])
            ndvi[nanargmax(ndvi)] = nan

            prox = nanargmax(ndvi)
            posUlt = hotNdvi.size-1

            while hotNdvi[posUlt] == ndvi[prox]:
                tempNdviIgual = append(tempNdviIgual,tempSuperficie[prox])

                ndvi[prox] = nan
                prox = nanargmax(ndvi)

            if tempNdviIgual.size > 1:
                tempNdviIgual = sort(tempNdviIgual)

                tamTempNdviIg = tempNdviIgual.size
                if tamTempNdviIg > (qtdPontos - posUlt):
                    tamTempNdviIg = qtdPontos - posUlt

                coldTemp = append(coldTemp,tempNdviIgual[:tamTempNdviIg])

                for j in xrange(tamTempNdviIg-1):
                    hotNdvi = append(hotNdvi,hotNdvi[posUlt])

            else:
                coldTemp = append(coldTemp,tempNdviIgual[0])

            tempNdviIgual = None

        if coldNdvi.size < qtdPontos:
            tempNdviIgual = array([])

            coldNdvi = append(coldNdvi,ndvi[nanargmin(ndvi)])
            tempNdviIgual = append(tempNdviIgual,tempSuperficie[nanargmin(ndvi)])
            ndvi[nanargmin(ndvi)] = nan

            prox = nanargmin(ndvi)
            posUlt = coldNdvi.size-1

            while coldNdvi[posUlt] == ndvi[prox]:
                tempNdviIgual = append(tempNdviIgual,tempSuperficie[prox])

                ndvi[prox] = nan
                prox = nanargmin(ndvi)

            if tempNdviIgual.size > 1:
                tempNdviIgual = sort(tempNdviIgual)[::-1]

                tamTempNdviIg = tempNdviIgual.size
                if tamTempNdviIg > (qtdPontos - posUlt):
                    tamTempNdviIg = qtdPontos - posUlt

                hotTemp = append(hotTemp,tempNdviIgual[:tamTempNdviIg])

                for j in xrange(tamTempNdviIg-1):
                    coldNdvi = append(coldNdvi,coldNdvi[posUlt])

            else:
                hotTemp = append(hotTemp,tempNdviIgual[0])

            tempNdviIgual = None

    ndvi = None
    tempSuperficie = None

    #----------

    hotTemp = sort(hotTemp)
    coldTemp = sort(coldTemp)

    TH = mean(hotTemp[-3:])
    TC = mean(coldTemp[:3])

    #----------

    return (TH - temperaturaSuperficie) / (TH - TC)

#----------

def transformar(tokens,tokensTipos):
    textoPy = 'def '+tokens[0]
    funcoes = []

    parametros = []

    aux = ''
    i = 1
    while(tokens[i] != '\n'):
        if(not (tokens[i] in [',','(',')'])):
            parametros.append(tokens[i])

        aux = aux + tokens[i]
        i = i + 1

    textoPy = textoPy+aux+':'

    retorno = 'return '
    nomesRet = []

    i = i + 1
    while(i < len(tokens)):
        if(tokens[i][0] == 'O' and tokens[i][1] == '_'):
            if(tokens[i][len(tokens[i])-1] == '_' and tokens[i+1][0] == '('):
                aux = '    '+tokens[i][2:len(tokens[i])-1]+' = '+'choose('

                retorno = retorno + tokens[i][2:len(tokens[i])-1] + ','
                nomesRet.append(tokens[i][2:len(tokens[i])-1])

                i = i + 1+1

                aux2 = ''
                while(tokens[i] != '='):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux2 = aux2 + tokens[i]
                    i = i + 1

                j = len(aux2)-1
                falso = ''
                while(aux2[j] != ','):
                    falso = falso + aux2[j]

                    j = j - 1

                aux2 = aux2[:j]
                falso = falso[::-1]
                falso = falso[:len(falso)-1]

                aux = aux + aux2 + ',(' + falso + ','

                i = i + 1
                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux+'))'

            else:
                aux = '    '+tokens[i][2:]+' = '

                aux2 = tokens[i][2:]

                i = i + 1+1
                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux
                retorno = retorno + aux2 + ','
                nomesRet.append(aux2)

        else:
            if(tokens[i][len(tokens[i])-1] == '_' and tokens[i+1][0] == '('):
                aux = '    '+tokens[i][:len(tokens[i])-1]+' = '+'choose('

                i = i + 1+1

                aux2 = ''
                while(tokens[i] != '='):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux2 = aux2 + tokens[i]
                    i = i + 1

                j = len(aux2)-1
                falso = ''
                while(aux2[j] != ','):
                    falso = falso + aux2[j]

                    j = j - 1

                aux2 = aux2[:j]
                falso = falso[::-1]
                falso = falso[:len(falso)-1]

                aux = aux + aux2 + ',(' + falso + ','

                i = i + 1
                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux+'))'

            else:
                aux = '    '+tokens[i]+' = '
                i = i + 1+1

                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux

        i = i + 1

    return textoPy+'\n    '+retorno[0:len(retorno)-1], funcoes, nomesRet, parametros

#----------

#---------- ANALISAR E TRANSFORMAR ----------#

def analisarETransformar(endArquivo,nomeFunc):
    analisado = analisador.analisar(endArquivo+nomeFunc)

    if(analisado[0] == False):
        try:
            if(eval(nomeFunc)):
                return True,''
        except:
            aux = analisado[1] + ' da funcao \''+nomeFunc+'\''
            return False,aux
    else:
        FuncExecutar = analisado[1][0]

        transformado = transformar(analisado[1],analisado[2])
        codigo = transformado[0]

        for i in xrange(len(transformado[1])):
            verifica = analisarETransformar(endArquivo,transformado[1][i])
            if(verifica[0] == False):
                return verifica
            else:
                if(verifica[1] != ''):
                    codigo = codigo + '\n' + verifica[1]

        return True,codigo,FuncExecutar,transformado[2],transformado[3]

#----------

#---------- EXECUTADOR ----------#

#----------

def executar(codigo,bandas,parametros): # EXECUTA O CODIGO GERADO
    exec(codigo[1],globals())

    return eval(codigo[2]+'('+parametros+')')

    #----------

#----------