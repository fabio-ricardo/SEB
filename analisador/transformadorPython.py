#coding:utf-8

#----------

def transformar(tokens,tokensTipos):
    textoPy = 'def '+tokens[0]
    funcoes = []

    aux = ''
    i = 1
    while(tokens[i] != '\n'):
        aux = aux + tokens[i]
        i = i + 1

    textoPy = textoPy+aux+':'

    retorno = 'return '

    i = i + 1
    while(i < len(tokens)):
        if(tokens[i][0] == 'O' and tokens[i][1] == '_'):
            if(tokens[i][len(tokens[i])-1] == '_' and tokens[i+1][0] == '('):
                aux = '    '+tokens[i][2:len(tokens[i])-1]+' = '+'numpy.choose('+'___mask'\
                    +',('+tokens[i][2:len(tokens[i])-1]+','

                retorno = retorno + tokens[i][2:len(tokens[i])-1] + ','

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

    return textoPy+'\n    '+retorno[0:len(retorno)-1], funcoes

#----------