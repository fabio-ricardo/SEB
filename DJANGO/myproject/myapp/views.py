# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from myproject.myapp.models import Document, Document2, Document3
from myproject.myapp.forms import DocumentForm, DocumentForm2, DocumentForm3

import toPython as toPy
import imageIO as imgIO
import numpy, os

def list(request):
    # Handle file upload
    if request.method == 'POST':
        erro = ''
        form = DocumentForm(request.POST, request.FILES)
        form2 = DocumentForm2(request.POST, request.FILES)
        form3 = DocumentForm3(request.POST, request.FILES)

        if form.is_valid() and form2.is_valid() and form3.is_valid():
            docfile = Document(docfile = request.FILES['docfile'])
            docfile.save()
            #---

            nomeImagem = 'myproject'+docfile.docfile.url
            i = len(nomeImagem)-1
            posPath = 0
            posExt = 0

            while(i > 0):
                if(nomeImagem[i] == '/'):
                    posPath = i
                    break

                if(nomeImagem[i] == '.'):
                    posExt = i

                i = i - 1

            endArquivoImg = nomeImagem[:posPath+1]
            extensaoImg = nomeImagem[posExt:]
            nomeImagem = nomeImagem[posPath+1:]

            #---

            funcfile = Document2(funcfile = request.FILES['funcfile'])
            funcfile.save()

            #---
            nomeFuncao = 'myproject'+funcfile.funcfile.url
            i = len(nomeFuncao)-1
            posPath = 0

            while(i > 0):
                if(nomeFuncao[i] == '/'):
                    posPath = i
                    break

                i = i - 1

            endArquivoFunc = nomeFuncao[:posPath+1]
            nomeFuncao = nomeFuncao[posPath+1:]

            #---

            bandfile = request.FILES['bandfile'].read().split('\n')
            bandfile = bandfile[:len(bandfile)-1]

            #---

            codigo = toPy.analisarETransformar(endArquivoFunc,nomeFuncao)

            if(codigo[0] == False):
                erro = codigo[1]
            else:
                #----------

                auxValPar = ''

                for i in xrange(len(codigo[4])):
                    if(bandfile[i][0] == 'B'):
                        auxValPar = auxValPar + 'bandas['+str(i)+']' + ','
                    else:
                        auxValPar = auxValPar + str(bandfile[i]) + ','

                parametros = auxValPar[:len(auxValPar)-1]

                #----------

                bandas, entrada = imgIO.abrirELer(endArquivoImg,nomeImagem) #mudar depois

                #----------

                retorno = toPy.executar(codigo,bandas,parametros)

                #----------

                terminado = imgIO.salvar(entrada,retorno,codigo[3],endArquivoImg,extensaoImg)

                if(terminado[0] == False):
                    erro = terminado[1]

                    #----------

                erro = "Processo Concluído com Sucesso."

                #----------

            # Redirect to the document list after POST

            form = DocumentForm() # A empty, unbound form
            form2 = DocumentForm2()
            form3 = DocumentForm3()

            images = os.listdir('myproject/media/imagem/')

            return render_to_response(
            'myapp/list.html',
            {'images': images, 'erro': erro, 'form': form, 'form2' : form2, 'form3' : form3},
            context_instance=RequestContext(request)
            )

            #return HttpResponseRedirect(reverse('myproject.myapp.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form
        form2 = DocumentForm2()
        form3 = DocumentForm3()
        erro = ''
        images = os.listdir('myproject/media/imagem/')


    # Render list page with the documents and the form
    return render_to_response(
        'myapp/list.html',
        {'images': images, 'erro': erro, 'form': form, 'form2' : form2, 'form3' : form3},
        context_instance=RequestContext(request)
    )