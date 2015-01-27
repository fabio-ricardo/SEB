#coding:utf-8

#----------

numeros = list(['0','1','2','3','4','5','6','7','8','9'])
caracteresAlfabeto = list(map(chr,range(ord('a'), ord('z') + 1))) +\
                                   list(map(chr,range(ord('A'), ord('Z') + 1)))
operadoresAritmeticos = list(['*','/','-','+','%'])
operadoresLogicos = list(['=','<','>','!'])

#----------

def abrirELerFuncao(endArquivo):
    try:
        arquivo = open(endArquivo,'r')
    except:
        return False,'Erro ao abrir o arquivo: '+str(endArquivo)

    #----------

    dadosArq = arquivo.read().split('\n')
    dadosArq = dadosArq[:len(dadosArq)-1]

    arquivo.close()

    return True,dadosArq

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

        if(len(tokens) > 0 and tokens[len(tokens)-1] != '\n'):
            tokens.append('\n')

    return tokens

    #----------

#----------

def analisar(endArquivo):
    dadosArq = abrirELerFuncao(endArquivo)

    if(dadosArq[0] == False):
        return dadosArq
    elif(len(dadosArq[1]) == 0):
        return False,'Arquivo vazio: '+str(endArquivo)

    tokens = tokenizar(dadosArq[1],operadoresAritmeticos+list(['(',')',','])+operadoresLogicos)

    tokensTipos = validarTipos(tokens)
    if(tokensTipos[0] == False):
        return False,'Erro no token: '+tokens[tokensTipos[1]]

    return expArquivoFuncao(tokensTipos[1],tokens)

    #----------

#----------

def validarTipos(tokens):
    tokensTipos = tokens[:]

    i = 0
    while(i < len(tokensTipos)):
        if(tokensTipos[i][0] in (caracteresAlfabeto + list('_'))):
            if(tokensTipos[i][0] == 'O' and len(tokensTipos[i]) > 1 and tokensTipos[i][1] == '_'):
                if(len(tokensTipos[i]) > 2):
                    if(tokensTipos[i][2] == '_' and len(tokensTipos[i]) == 3 and len(tokensTipos) > i and tokensTipos[i+1] == '('):
                        return False,i
                    else:
                        verifica = verificador(tokensTipos[i][2:],(caracteresAlfabeto + list('_') + numeros))
                        if(verifica[0] == False):
                            return False,i
                else:
                    return False,i
            elif(tokensTipos[i][0] == '_' and len(tokensTipos[i]) == 1 and len(tokensTipos) > i and tokensTipos[i+1] == '('):
                return False,i
            else:
                verifica = verificador(tokensTipos[i][1:],(caracteresAlfabeto + list('_') + numeros))
                if(verifica[0] == False):
                    return False,i

            tokensTipos[i] = '<identificador>'

        elif(tokensTipos[i][0] in numeros):
            verifica = verificador(tokensTipos[i][1:],numeros)
            if(verifica[0] == False):
                if(tokensTipos[i][verifica[1]+1] == '.'):
                    pos = verifica[1]+2
                    verifica = verificador(tokensTipos[i][pos:],numeros)
                    if(verifica[0] == False):
                        if(tokensTipos[i][pos+verifica[1]] == 'E' or tokensTipos[i][pos+verifica[1]] == 'e'):
                            if(len(tokensTipos[i]) > pos+verifica[1]+1):
                                verifica = verificador(tokensTipos[i][pos+verifica[1]+1:],numeros)
                                if(verifica[0] == False):
                                    return False,i
                                else:
                                    tokensTipos[i] = '<numero>'
                            else:
                                if(len(tokensTipos) > i+1 and (tokensTipos[i+1] == '+' or tokensTipos[i+1] == '-')):
                                    if(len(tokensTipos) > i+2):
                                        verifica = verificador(tokensTipos[i+2],numeros)
                                        if(verifica[0] == False):
                                            return False,i+2
                                        else:
                                            tokens[i] = tokens[i]+tokens[i+1]+tokens[i+2]
                                            tokensTipos[i] = '<numero>'
                                            del tokens[i+1]
                                            del tokens[i+1]
                                            del tokensTipos[i+1]
                                            del tokensTipos[i+1]
                                    else:
                                        return False,i+1
                                else:
                                    return False,i
                        else:
                            return False,i
                    else:
                        tokensTipos[i] = '<numero>'
                else:
                    if(tokensTipos[i][verifica[1]+1] == 'E' or tokensTipos[i][verifica[1]+1] == 'e'):
                        if(len(tokensTipos[i]) > verifica[1]+2):
                            verifica = verificador(tokensTipos[i][verifica[1]+2:],numeros)
                            if(verifica[0] == False):
                                return False,i
                            else:
                                tokensTipos[i] = '<numero>'
                        else:
                            if(len(tokensTipos) > i+1 and (tokensTipos[i+1] == '+' or tokensTipos[i+1] == '-')):
                                if(len(tokensTipos) > i+2):
                                    verifica = verificador(tokensTipos[i+2],numeros)
                                    if(verifica[0] == False):
                                        return False,i+2
                                    else:
                                        tokens[i] = tokens[i]+tokens[i+1]+tokens[i+2]
                                        tokensTipos[i] = '<numero>'
                                        del tokens[i+1]
                                        del tokens[i+1]
                                        del tokensTipos[i+1]
                                        del tokensTipos[i+1]
                                else:
                                    return False,i+1
                            else:
                                return False,i
                    else:
                        return False,i
            else:
                tokensTipos[i] = '<numero>'
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
            if(not (tokensTipos[i][0] in list(['(',')',',','\n']))):
                return False,i

        i = i + 1

    return True,tokensTipos

    #----------

#----------

def verificador(tokens, lista):
    for i in xrange(len(tokens)):
        if(tokens[i] not in lista):
            return False,i

    return True,-1

    #----------

#----------

def expArquivoFuncao(tokensTipos,tokens):
    verifica = expDeclararFuncao(tokensTipos,tokens,0)
    if(verifica[0] == False):
        return False,'Erro de gramatica no token: '+tokens[verifica[1]]

    verifica = expressoesComandos(tokensTipos,tokens,verifica[1])
    if(verifica[0] == False):
        return False,'Erro de gramatica no token: '+tokens[verifica[1]]

    return True,tokens,tokensTipos

    #----------

#----------

def expDeclararFuncao(tokensTipos,tokens,i):
    if(len(tokensTipos) > i and tokensTipos[i] == '<identificador>'):
        if(len(tokensTipos) > i+1 and tokensTipos[i+1] == '('):
            if(len(tokensTipos) > i+2 and tokensTipos[i+2] == ')'):
                if(len(tokensTipos) > i+3 and tokensTipos[i+3] == '\n'):
                    return (True,i+4)
                else:
                    return (False,i+3)
            else:
                verifica = expVariaveisFuncao(tokensTipos,tokens,i+2)
                if(verifica[0] == True):
                    if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == ')'):
                        if(len(tokensTipos) > verifica[1]+1 and tokensTipos[verifica[1]+1] == '\n'):
                            return (True,verifica[1]+2)
                        else:
                            return (False,verifica[1]+1)
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

def expVariaveisFuncao(tokensTipos,tokens,i):
    if(len(tokensTipos) > i and tokensTipos[i] == '<identificador>'):
        if(len(tokensTipos) > i+1 and tokensTipos[i+1] == ','):
            return expVariaveisFuncao(tokensTipos,tokens,i+2)
        else:
            return (True,i+1)
    else:
        return (False,i)

    #----------

#----------

def expressoesComandos(tokensTipos,tokens,i):
    if(len(tokensTipos) > i):
        verifica = expressaoComando(tokensTipos,tokens,i)
        if(verifica[0] == False):
            return (False,verifica[1])
        else:
            if(len(tokensTipos) > verifica[1]):
                return expressoesComandos(tokensTipos,tokens,verifica[1])
            else:
                return (True,verifica[1])
    else:
        return (False,i)

    #----------

#----------

def expressaoComando(tokensTipos,tokens,i):
    verifica = expressaoRecebe(tokensTipos,tokens,i)
    if(verifica[0] == False):
        return (False,verifica[1])
    else:
        if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == '='):
            verifica = expressaoAritmetica(tokensTipos,tokens,verifica[1]+1)
            if(verifica[0] == False):
                return (False,verifica[1])
            else:
                if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == '\n'):
                    return (True,verifica[1]+1)
                else:
                    return (False,verifica[1])
        else:
            return (False,verifica[1])

    #----------

#----------

def expressaoRecebe(tokensTipos,tokens,i):
    if(len(tokensTipos) > i and tokensTipos[i] == '<identificador>'):
        if(len(tokensTipos) > i+1 and tokensTipos[i+1] == '('):
            if(tokens[i][len(tokens[i])-1] == '_'):
                verifica = expressaoLogica(tokensTipos,tokens,i+2)
                if(verifica[0] == False):
                    return (False,verifica[1])
                else:
                    if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == ')'):
                        return (True,verifica[1]+1)
                    else:
                        return (False,verifica[1])
            else:
                return (False,i)
        else:
            return (True,i+1)
    else:
        return (False,i)

    #----------

#----------

def expressaoLogica(tokensTipos,tokens,i):
    verifica = expressaoAritmetica(tokensTipos,tokens,i)
    if(verifica[0] == False):
        return (False,i)
    else:
        if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == '<operadorLogico>'):
            return expressaoAritmetica(tokensTipos,tokens,verifica[1]+1)
        else:
            return (False,verifica[1])

    #----------

#----------

def expressaoAritmetica(tokensTipos,tokens,i):
    if(len(tokensTipos) > i and tokensTipos[i] == '<operadorAritmetico>' and (tokens[i] == '+' or tokens[i] == '-')):
        return expressaoAritmetica(tokensTipos,tokens,i+1)
    else:
        verifica = expressaoOperando(tokensTipos,tokens,i)
        if(verifica[0] == False):
            return (False,verifica[1])
        else:
            if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == '<operadorAritmetico>'):
                return expressaoAritmetica(tokensTipos,tokens,verifica[1]+1)
            else:
                return (True,verifica[1])

    #----------

#----------

def expressaoOperando(tokensTipos,tokens,i):
    if(len(tokensTipos) > i and tokensTipos[i] == '<identificador>'):
        if(len(tokensTipos) > i+1 and tokensTipos[i+1] == '('):
            if(len(tokensTipos) > i+2 and tokensTipos[i+2] == ')'):
                return (True,i+3)
            else:
                verifica = expressaoParametrosFuncao(tokensTipos,tokens,i+2)
                if(verifica[0] == False):
                    return (False,verifica[1])
                else:
                    if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == ')'):
                        return (True,verifica[1]+1)
                    else:
                        return (False,verifica[1])
        else:
            return (True,i+1)
    elif(len(tokensTipos) > i and tokensTipos[i] == '<numero>'):
        return (True,i+1)
    elif(len(tokensTipos) > i and tokensTipos[i] == '('):
        verifica = expressaoAritmetica(tokensTipos,tokens,i+1)
        if(verifica[0] == False):
            return (False,verifica[1])
        else:
            if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == ')'):
                return (True,verifica[1]+1)
            else:
                return (False,verifica[1])
    else:
        return (False,i)

    #----------

#----------

def expressaoParametrosFuncao(tokensTipos,tokens,i):
    verifica = expressaoAritmetica(tokensTipos,tokens,i)
    if(verifica[0] == False):
        return (False,verifica[1])
    else:
        if(len(tokensTipos) > verifica[1] and tokensTipos[verifica[1]] == ','):
            return expressaoParametrosFuncao(tokensTipos,tokens,verifica[1]+1)
        else:
            return (True,verifica[1])

    #----------

#----------