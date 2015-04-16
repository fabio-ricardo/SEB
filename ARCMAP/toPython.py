#coding:utf-8

import analisadorSintatico as analisador

#----------

from math import *
import numpy

#----------
from numpy.core.umath import arccos


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
                aux = '    '+tokens[i][2:len(tokens[i])-1]+' = '+'numpy.choose('+'___mask'\
                    +',('+tokens[i][2:len(tokens[i])-1]+','

                retorno = retorno + tokens[i][2:len(tokens[i])-1] + ','
                nomesRet.append(tokens[i][2:len(tokens[i])-1])

                i = i + 1+1

                aux2 = ''
                while(tokens[i] != '='):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux2 = aux2 + tokens[i]
                    i = i + 1

                aux2 = '    '+'___mask = '+aux2[:len(aux2)-1]

                i = i + 1
                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux2+'\n'+aux+'))'

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
                aux = '    '+tokens[i][:len(tokens[i])-1]+' = '+'numpy.choose('+'___mask'\
                    +',('+tokens[i][:len(tokens[i])-1]+','

                i = i + 1+1

                aux2 = ''
                while(tokens[i] != '='):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux2 = aux2 + tokens[i]
                    i = i + 1

                aux2 = '    '+'___mask = '+aux2[:len(aux2)-1]

                i = i + 1
                while(tokens[i] != '\n'):
                    if(tokensTipos[i] == '<identificador>' and tokensTipos[i+1] == '('):
                        funcoes.append(tokens[i])

                    aux = aux + tokens[i]
                    i = i + 1

                textoPy = textoPy+'\n'+aux2+'\n'+aux+'))'

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
    exec codigo[1]

    return eval(codigo[2]+'('+parametros+')')

    #----------

#----------