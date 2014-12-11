#coding:utf-8

import time
import analisadorSintatico as analisador
import transformadorPython as transPy
import executadorPython as execPy

#----------

inicio = time.time()

#----------

nomeFuncao = 'a'
linguagem = 'Python'
endArquivo = '/home/vini/projeto/AlgoritmoSebal/funcoes/'

#----------

def analisarETransformar(nomeFunc,linguagem):
    analisado = analisador.analisar(endArquivo+nomeFunc+'.jfrv')

    if(analisado[0] == False):
        aux = analisado[1] + ' da funcao \''+nomeFunc+'\''
        return False,aux
    else:
        if(linguagem == 'Python'):
            transformado = transPy.transformar(analisado[1],analisado[2])
            codigo = transformado[0]

            for i in xrange(len(transformado[1])):
                verifica = analisarETransformar(transformado[1][i],'Python')
                if(verifica[0] == False):
                    return verifica
                else:
                    codigo = codigo + '\n' + verifica[1]

            return True,codigo

#----------

codigo = analisarETransformar(nomeFuncao,linguagem)

if(codigo[0] == False):
    print codigo[0]
else:
    if(linguagem == 'Python'):
        execPy.executar(codigo[1])

#----------

fim = time.time()

print 'Tempo:',(fim-inicio)