#coding:utf-8
import numpy
import time

inicio = time.time()

#----------

endArquivo = '/home/vini/projeto/AlgoritmoSebal/funcoes/'
extensao = '.jfrv'

#----------

numeros = list(['0','1','2','3','4','5','6','7','8','9'])
caracteresAlfabeto = list(map(chr,range(ord('a'), ord('z') + 1))) +\
                                   list(map(chr,range(ord('A'), ord('Z') + 1)))
operadoresAritmeticos = list(['*','/','-','+','%'])
operadoresLogicos = list(['=','<','>','!'])

#----------

def abrirELerFuncao(nomeArquivo):
    try:
        arquivo = open(endArquivo+nomeArquivo+extensao,'r')
    except:
        return 'abrir',endArquivo,nomeArquivo

    #----------

    dadosArq = arquivo.read().split('\n')
    dadosArq = dadosArq[:len(dadosArq)-1]

    arquivo.close()

    return dadosArq

    #----------

#----------

def tokenizar(dadosArq, separador):
    tokens = []

    for linha in xrange(len(dadosArq)):
        dadosArq[linha] = dadosArq[linha].strip()
        aux = ''

        for caracter in xrange(len(dadosArq[linha])):
            if(dadosArq[linha][caracter] == ' '):
                if(aux != ''):
                    tokens.append(aux)

                aux = ''
            elif(dadosArq[linha][caracter] in separador):
                if(aux != ''):
                    tokens.append(aux)

                tokens.append(dadosArq[linha][caracter])
                aux = ''
            else:
                aux += dadosArq[linha][caracter]

        if(aux != ''):
            tokens.append(aux)

    return tokens

    #----------

#----------

def analisadorSintaticoFuncao(nomeArquivo):
    dadosArq = abrirELerFuncao(nomeArquivo)

    if(len(dadosArq) == 0):
        return 'vazio',endArquivo,nomeArquivo

    if(dadosArq[0] == 'abrir'):
        return dadosArq

    tokens = tokenizar(dadosArq,operadoresAritmeticos+list(['(',')',','])+operadoresLogicos)
    print tokens

    tokensTipos = validarTipos(tokens)
    print tokensTipos

    if(type(tokensTipos) == int):
        return tokensTipos

    return expArquivoFuncao(tokensTipos)

    #----------

#----------

def validarTipos(tokens):
    tokensTipos = tokens[:]

    i = 0
    while(i < len(tokensTipos)):
        if(tokensTipos[i][0] in (caracteresAlfabeto + list('_'))):
            verifica = verificador(tokensTipos[i][1:],(caracteresAlfabeto + list('_') + numeros))
            if(type(verifica) == int):
                return i

            tokensTipos[i] = '<identificador>'

        elif(tokensTipos[i][0] in numeros):
            verifica = verificador(tokensTipos[i][1:],numeros)
            if(type(verifica) == int):
                if(tokensTipos[i][verifica+1] == '.'):
                    verifica = verificador(tokensTipos[i][verifica+2:],numeros)
                    if(type(verifica) == int):
                        if(tokensTipos[i][verifica+2] == 'E' or tokensTipos[i][verifica+2] == 'e'):
                            if(len(tokensTipos[i]) > verifica+3):
                                verifica = verificador(tokensTipos[i][verifica+3:],numeros)
                                if(type(verifica) == int):
                                    return i
                                else:
                                    tokensTipos[i] = '<numeroReal>'
                            else:
                                if(len(tokensTipos) > i+1 and (tokensTipos[i+1] == '+' or tokensTipos[i+1] == '-')):
                                    if(len(tokensTipos) > i+2):
                                        verifica = verificador(tokensTipos[i+2],numeros)
                                        if(type(verifica) == int):
                                            return i+2
                                        else:
                                            tokens[i] = tokens[i]+tokens[i+1]+tokens[i+2]
                                            tokensTipos[i] = '<numeroReal>'
                                            del tokens[i+1]
                                            del tokens[i+1]
                                            del tokensTipos[i+1]
                                            del tokensTipos[i+1]
                                    else:
                                        return i+1
                                else:
                                    if(len(tokensTipos) > i+1):
                                        return i+1
                                    else:
                                        return i
                        else:
                            return i
                    else:
                        tokensTipos[i] = '<numeroReal>'
                else:
                    if(tokensTipos[i][verifica+1] == 'E' or tokensTipos[i][verifica+1] == 'e'):
                        if(len(tokensTipos[i]) > verifica+2):
                            verifica = verificador(tokensTipos[i][verifica+2:],numeros)
                            if(type(verifica) == int):
                                return i
                            else:
                                tokensTipos[i] = '<numeroInteiro>'
                        else:
                            if(len(tokensTipos) > i+1 and (tokensTipos[i+1] == '+' or tokensTipos[i+1] == '-')):
                                if(len(tokensTipos) > i+2):
                                    verifica = verificador(tokensTipos[i+2],numeros)
                                    if(type(verifica) == int):
                                        return i+2
                                    else:
                                        tokens[i] = tokens[i]+tokens[i+1]+tokens[i+2]
                                        tokensTipos[i] = '<numeroInteiro>'
                                        del tokens[i+1]
                                        del tokens[i+1]
                                        del tokensTipos[i+1]
                                        del tokensTipos[i+1]
                                else:
                                    return i+1
                            else:
                                if(len(tokensTipos) > i+1):
                                    return i+1
                                else:
                                    return i
                    else:
                        return i
            else:
                tokensTipos[i] = '<numeroInteiro>'
        elif(tokensTipos[i][0] in operadoresAritmeticos):
            if((len(tokensTipos) > i+1) and ((tokensTipos[i][0] == '*' and tokensTipos[i+1][0] == '*')\
                    or (tokensTipos[i][0] == '/' and tokensTipos[i+1][0] == '/'))):
                tokens[i] = tokens[i]+tokens[i+1]
                tokensTipos[i] = '<operadorAritmetico>'
                del tokens[i+1]
                del tokensTipos[i+1]
            else:
                tokensTipos[i] = '<operadorAritmetico>'
        elif(tokensTipos[i][0] in operadoresLogicos):
            if((len(tokensTipos) > i+1) and ((tokensTipos[i][0] == '<' and tokensTipos[i+1][0] == '=')\
                    or (tokensTipos[i][0] == '>' and tokensTipos[i+1][0] == '=')\
                    or (tokensTipos[i][0] == '!' and tokensTipos[i+1][0] == '=')\
                    or (tokensTipos[i][0] == '=' and tokensTipos[i+1][0] == '='))):
                tokens[i] = tokens[i]+tokens[i+1]
                tokensTipos[i] = '<operadorLogico>'
                del tokens[i+1]
                del tokensTipos[i+1]
            elif(tokensTipos[i][0] != '='):
                tokensTipos[i] = '<operadorLogico>'
        else:
            if(not (tokensTipos[i][0] in list(['(',')',',']))):
                return i

        i = i + 1

    return tokensTipos

    #----------

#----------

def verificador(tokens, lista):
    for i in xrange(len(tokens)):
        if(tokens[i] not in lista):
            return i

    return True

    #----------

#----------

def expArquivoFuncao(tokens):
    verifica = expDeclararFuncao(tokens,0)
    if(verifica[0] == False):
        return verifica[1]

    return True

    #----------

#----------

def expDeclararFuncao(tokens,i):
    if(len(tokens) > i and tokens[i] == '<identificador>'):
        if(len(tokens) > i+1 and tokens[i+1] == '('):
            if(len(tokens) > i+2 and tokens[i+2] == ')'):
                return (True,i+2)
            else:
                verifica = expVariaveisFuncao(tokens,i+2)
                if(verifica[0] == True):
                    if(len(tokens) > verifica[1] and tokens[verifica[1]] == ')'):
                        return (True,verifica[1])
                    else:
                        return (False,verifica[1])
                else:
                    return (False,verifica[1])
        else:
            return (False,i+1)
    else:
        return (False,i)

    #----------

#----------

def expVariaveisFuncao(tokens,i):
    if(len(tokens) > i and tokens[i] == '<identificador>'):
        if(len(tokens) > i+1 and tokens[i+1] == ','):
            return expVariaveisFuncao(tokens,i+2)
        else:
            return (True,i+1)
    else:
        return (False,i)

    #----------

#----------

print analisadorSintaticoFuncao('teste')

#----------

fim = time.time()

print 'Tempo:',(fim-inicio)
