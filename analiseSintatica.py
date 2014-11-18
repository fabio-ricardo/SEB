#coding:utf-8
import numpy
import time

inicio = time.time()

#----------

endArquivo = '/home/vini/projeto/AlgoritmoSebal/funcoes/'
extensao = '.jfrv'

#----------

numeros = list(['0','1','2','3','4','5','6','7','8','9'])
operadores = list(['*','/','-','+'])
caracteresAlfabeto = list(map(chr,range(ord('a'), ord('z') + 1))) +\
                                   list(map(chr,range(ord('A'), ord('Z') + 1)))

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

        if(len(dadosArq[linha]) > 0):
            tokens.append('\n')

    return tokens

    #----------

#----------

def analisadorSintaticoFuncao(nomeArquivo):
    dadosArq = abrirELerFuncao(nomeArquivo)

    if(len(dadosArq) == 0):
        return 'vazio',endArquivo,nomeArquivo

    if(dadosArq[0] == 'abrir'):
        return dadosArq

    tokens = tokenizar(dadosArq,operadores+list(['(',')',',','=','<','>','!']))
    print tokens

    if(tokens[0] == '\n'):
        return 1,(1 ,' ')

    tokensTipos = definirTipos(tokens)
    print tokensTipos

    if(type(tokensTipos) == int):
        return tokensTipos

    '''i = 0
    linha = 1
    aux = numpy.array([])

    while(i < len(tokens)):
        if(tokens[i] == '\n'):
            if(linha == 1):
                expressaoAux = expressaoFunc(aux) #<expressao_Func>
            #else:
            #    expressaoAux = expressaoRecebe(aux,0) #<expressao>

            if(expressaoAux != True):
                return linha, expressaoAux

            linha = linha + 1
            i = i + 1
            aux = numpy.array([])

            continue

        aux = numpy.append(aux,tokens[i])

        i = i + 1'''

    return True

    #----------

#----------

def definirTipos(tokens):
    tokensTipos = tokens[:]

    i = 0
    while(i < len(tokensTipos)):
        if(tokensTipos[i][0] in (caracteresAlfabeto + list('_'))):
            verifica = verificador(tokensTipos[i][1:],(caracteresAlfabeto + list('_') + numeros))
            if(type(verifica) == int):
                return i

            if(tokensTipos[i][0] == 'O' and (len(tokensTipos[i]) > 1 and tokensTipos[i][1] == '_')):
                if(tokensTipos[i][len(tokensTipos[i])-1] == '_' and\
                  (len(tokensTipos) > (i+1) and tokensTipos[i+1][0] == '(')):
                    tokensTipos[i] = '<O_identificador_IF>'
                else:
                    tokensTipos[i] = '<O_identificador>'
            else:
                if(tokensTipos[i][len(tokensTipos[i])-1] == '_' and\
                  (len(tokensTipos) > (i+1) and tokensTipos[i+1][0] == '(')\
                   and i != 0):
                    tokensTipos[i] = '<identificador_IF>'
                else:
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

        i = i + 1

    return tokensTipos

    #----------

#----------

def expressaoFunc(tokens):
    if(not (tokens[0][0] in (caracteresAlfabeto+ list('_')))): #<C1_nome_func>
        return 1,tokens[0][0]

    verifica = verificador(tokens[0][1:],(caracteresAlfabeto+ list('_'))+numeros) #<Resto_nome_func>
    if(verifica != True):
        return verifica+2,tokens[0][verifica+1]

    if(tokens[1][0] != '('): #<'('>
        return len(tokens[0])+1,tokens[1][0]

    verifica = variavelFunc(tokens[2:],len(tokens[0])+1) #<vars>
    if(type(verifica) != int):
        return verifica

    soma = 0
    i = 0
    while(soma < verifica):
        soma = soma + len(tokens[i])
        i = i + 1

    if(len(tokens) > i):
        if(tokens[i] != ')'):
            return soma+1,tokens[i][0]
    else:
        return soma,tokens[i-1]

    return True

    #----------

#----------

def variavelFunc(tokens,coluna):
    if(len(tokens) > 1):
        return variavelFunc2(tokens,coluna)

    return coluna #E

    #----------

#----------

def variavelFunc2(tokens,coluna):
    verifica = verificador(tokens[0][0],(caracteresAlfabeto+ list('_'))) #<C1_vars1>
    if(verifica != True):
        return coluna+1,tokens[0][0]

    verifica = verificador(tokens[0][1:],(caracteresAlfabeto+ list('_'))+numeros) #<Resto_vars1>
    if(verifica != True):
        return verifica+coluna+2,tokens[0][verifica+1]

    if(len(tokens) > 2):
        if(tokens[1][0] != ','): # ,
            return len(tokens[0])+coluna+1,tokens[1][0]

        return variavelFunc2(tokens[2:],coluna+len(tokens[0])+1)
    else:
        return coluna+1

    #----------

#----------
'''
def expressaoRecebe(tokens,coluna):
    if(tokens[0][0] == 'O' and len(tokens[0]) > 1 and tokens[0][1] == '_'):
        print tokens[0],'1',len(tokens[0])
        if(t):

        return True
    elif(tokens[0][0] in (caracteresAlfabeto+ list('_'))):
        print tokens,'2'
        return True

    return 1,tokens[0][0]

    #----------
'''
#----------

def expressaoAritmetica(tokens, coluna):
    verifica = verificador(tokens[0],numeros) #<operando>
    if(verifica != True):
        return verifica+1+coluna,tokens[0][verifica]

    if(len(tokens) == 1):
        return True

    if(len(tokens) == 2):
        return coluna+2,tokens[1][0]

    verifica = verificador(tokens[1],operadores) #<operador>
    if(verifica != True):
        return verifica+1+coluna,tokens[1][verifica]

    return expressaoAritmetica(tokens[2:],coluna+2) #<expressao>

    #----------

#----------

def verificador(token, lista):
    for i in xrange(len(token)):
        if(token[i] not in lista):
            return i

    return True

    #----------

#----------

print analisadorSintaticoFuncao('teste')

#----------

fim = time.time()

print 'Tempo:',(fim-inicio)
