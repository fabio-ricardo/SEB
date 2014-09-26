#coding:utf-8
import time

inicio = time.time()

#----------

endArquivo = '/home/vini/projeto/AlgoritmoSebal/funcoes/'
extensao = '.frv'

#----------

def analSintaFuncao(nomeArquivo):
    try:
        arquivo = open(endArquivo+nomeArquivo+extensao,'r')
    except:
        return 'abrir',endArquivo,nomeArquivo

    #----------

    dadosArq = arquivo.read().split('\n')
    dadosArq = dadosArq[:len(dadosArq)-1]

    arquivo.close()

    #----------

    caracteresSemNum = list(map(chr,range(ord('a'), ord('z') + 1))) +\
                                   list(map(chr,range(ord('A'), ord('Z') + 1))) + list('_')
    caracteresComNum = list(map(chr,range(ord('a'), ord('z') + 1))) +\
                                   list(map(chr,range(ord('A'), ord('Z') + 1))) + list('_') +\
                                   list(map(chr,range(ord('0'), ord('9') + 1)))
    caracteresOperadores = list(['+','-','*','/','%'])
    caracteresLogicos = list(['<','>','<=','>=','!=','==','and','or','not'])

    caracteres = caracteresSemNum

    #----------

    if(len(dadosArq) < 1):
        return 'vazio',endArquivo,nomeArquivo

    #----------

    dadosArq[0] = dadosArq[0].strip()

    if(len(dadosArq[0]) < 1):
        return 'incompleto',0,0

    if(not dadosArq[0][0] in caracteres):
        return 'erro',0,0

    #----------

    caracteres = caracteresComNum

    j = 1
    while(j < len(dadosArq[0]) and dadosArq[0][j] != '('):
        if(not dadosArq[0][j] in caracteres):
            if(dadosArq[0][j] == ' '):
                caracteres = list('(')
            else:
                return 'erro',0,j

        j += 1

    if(j == len(dadosArq[0])):
        return 'incompleto',0,j

    #----------

    caracteres = caracteresSemNum

    j += 1
    while(j < len(dadosArq[0]) and dadosArq[0][j] != ')'):
        if(dadosArq[0][j] in caracteres):
            if(caracteres == caracteresSemNum):
                caracteres = caracteresComNum
            elif(caracteres == list(',')):
                caracteres = caracteresSemNum
        else:
            if(dadosArq[0][j] == ' '):
                if(caracteres == caracteresComNum):
                    caracteres = list(',')
            elif(dadosArq[0][j] == ','):
                caracteres = caracteresSemNum
            else:
                return 'erro',0,j

        j += 1

    if(j == len(dadosArq[0])):
        return 'incompleto',0,j

    #----------

    i = 1
    while(i < 2):#len(dadosArq)
        caracteres = caracteresSemNum

        dadosArq[i] = dadosArq[i].strip()

        j = 0
        while(j < len(dadosArq[i]) and dadosArq[i][j] != '='):
            if(dadosArq[i][j] in caracteres):
                caracteres = caracteresComNum
            else:
                if(dadosArq[i][j] == '('):
                    j += 1

                    if(j < len(dadosArq[i]) and dadosArq[i][j] == ')'):
                        return 'erro',i,j

                    while(j < len(dadosArq[i]) and dadosArq[i][j] != ')'):
                        print dadosArq[i][j]#####

                        j += 1

                    if(j == len(dadosArq[i])):
                        return 'incompleto',i,j

                elif(dadosArq[i][j] == ' '):
                    caracteres = list('=')
                else:
                    return 'erro',i,j

            j += 1

        if(j == len(dadosArq[i])):
            return 'incompleto',i,j

        j += 1

        while(j < len(dadosArq[i])):
            print dadosArq[i][j]

            j += 1

        i += 1

    #----------

    return None

    #----------

#----------

print analSintaFuncao('nova_funcao')

#----------

fim = time.time()

print 'Tempo:',(fim-inicio)
