#coding: utf-8
import gdal, osgeo, sys, numpy, time, os #importa as bibliotecas
from gdalconst import *

comecoTempo = time.time() #pega o tempo de inicio

gdal.AllRegister() #indica todos os drivers, serve somente para leitura

#driver = gdal.GetDriverByName('GTiff') #pega o driver pelo nome
#driver.Register() #indica o driver, serve para leitura e escrita

nome = 'empilhada.tif' #nome da imagem com extensao

dataSet = gdal.Open(nome,GA_ReadOnly) #abre a imagem com o gdal, somente leitura
if dataSet is None: #se deu um erro vai sair do programa
    print 'Não foi possivel abrir o arquivo: '
    sys.exit(1)

colunas = dataSet.RasterXSize #pega o numero de colunas
linhas = dataSet.RasterYSize #pega o numero de linhas
NBandas = dataSet.RasterCount #pega o numero de bandas
projecao = dataSet.GetProjection() #pega a projecao da imagem
driver = dataSet.GetDriver() #pega o driver da imagem

print colunas, '---', linhas, '---', NBandas, ' --- ', projecao
print driver.ShortName, ' --- ', driver.LongName

geoTransform = dataSet.GetGeoTransform() #pega as informações de georreferenciamento
if not geoTransform is None: #se existe georreferenciamento entao pega as informações
    originX = geoTransform[0] #top left x
    originY = geoTransform[3] #top left y
    pixelWidth = geoTransform[1] #w-e pixel resolution
    pixelHeight = geoTransform[5] #n-s pixel resolution

    print originX, '---', originY, '---', pixelWidth, '---', pixelHeight

x = 10000 #coordenada x
y = 10000 #coordenada y

#É necessario obter o desvio dos pixels para as coordenadas x e y
xOffSet = int((x - originX) / pixelWidth) #pixel x da coordenada, calcula o desvio
yOffSet = int((y - originY) / pixelHeight) #pixel y da coordenada, calcula o desvio

print xOffSet, ' --- ', yOffSet

#banda = dataSet.GetRasterBand(1) #seleciona a banda 1

#tipoBanda = gdal.GetDataTypeName(banda.DataType) #tipo do pixel
#(min,max) = banda.ComputeRasterMinMax(1) #valor minimo e maximo do pixel
                                         #na banda
#print tipoBanda, ' --- ', min, ' --- ', max

#dados = banda.ReadAsArray(0,0,colunas,linhas) #ler toda a banda

#----------
#dados = numpy.array(dataSet.GetRasterBand(1).ReadAsArray().astype(numpy.float32))

#---------- Outro Método de leitura ----------#

#dados = banda.ReadRaster(0,0,colunas,linhas) #le a banda toda
#dados2 = numpy.fromstring(dados, dtype=numpy.uint8) #transforma a string em vetor do tipo uint8 - 1 byte
#dados2 = numpy.reshape(dados2,(linhas,colunas)) #transforma o vetor em matriz do tipo matriz[linhas,colunas]
#----------

#print dados[4000,4000]

#arquivo = open('banda1.txt','w')
#numpy.save(arquivo, dados) #salva o array no arquivo
#arquivo.close()

#arquivo2 = open('banda1.txt','r')
#dados2 = numpy.load(arquivo2) #le o array do arquivo
#arquivo2.close()

#print dados2[4000,4000]
#----------

#raw_input()

#banda = None
#dados = None
#dataSet = None

outDataSet = driver.Create("ndvi.tif",colunas,linhas,1,GDT_Float32) #cria o arquivo
             #parametros: nome, colunas, linhas, bandas, tipo do pixel, propriedades - passa um vetor de string [' ']
outBand = outDataSet.GetRasterBand(1) #seleciona a banda

xTamanhoBloco = 256 #(Penso que é melhor definir um tamanho para o bloco 'x' e 'y')
yTamanhoBloco = 256 #Testes me fizeram escolher 256 x 256, geotiff default 256x256
soma = 0 #usada para calcular a quantidade de pixels

banda = numpy.empty([8],dtype=osgeo.gdal.Band) #cria o array para as bandas
banda[0] = 0 #coloca um vetor nulo na posição '0'

for k in range(1,NBandas+1): #inicializa o array 'banda' com as bandas
    banda[k] = dataSet.GetRasterBand(k) #O índice começa em 1

    xYTamanhoBloco = banda[k].GetBlockSize() #tamanho bloco imagem

    tipoBanda = gdal.GetDataTypeName(banda[k].DataType) #tipo do pixel
    (min,max) = banda[k].ComputeRasterMinMax(1) #valor minimo e maximo do pixel na banda

    print k, ' --- ', tipoBanda, ' --- ', min, ' --- ', max, ' --- ', xYTamanhoBloco

#Algoritmo para ler a imagem em blocos de pixels, um for para as linhas e um para as colunas
#é a forma mais eficiente de se trabalhar com as imagens
for i in range(0,linhas,yTamanhoBloco):
    if i + yTamanhoBloco < linhas:
        lerLinhas = yTamanhoBloco
    else:
        lerLinhas = linhas - i

    for j in range(0,colunas,xTamanhoBloco):
        if j + xTamanhoBloco < colunas:
            lerColunas = xTamanhoBloco
        else:
            lerColunas = colunas - j

        #---------- Ler os dados aqui ----------#

        dados = numpy.empty([NBandas+1,lerLinhas,lerColunas]) #cria o array para os dados
        dados[0] = 0 #coloca um vetor nulo na posição '0'

        #print dados[0]
        for k in range(1,NBandas+1): #le o bloco das banda para dados
            dados[k] = banda[k].ReadAsArray(j,i,lerColunas,lerLinhas) #pode colocar .astype(numpy.float32)
                         #a coluna é o 'x' e a linha é o 'y'

        #---------- Faça as operações aqui ----------#

        #for k in range(1,NBandas+1):
            #print dados[k][lerLinhas-1,lerColunas-1]
            #dados[k] = dados[k]*3
            #print dados[k][lerLinhas-1,lerColunas-1]

            #soma = soma + dados[k].size #'.size' é a quantidade de elementos no array

        #Calculando o NDVI - Transforma só as bandas usadas em float32
        #coloca a soma da banda 3 e da banda 2 no array denominador
        denominador = dados[3].astype(numpy.float32) + dados[2].astype(numpy.float32)

        #este método para calcular o ndvi demora mais que o choose
        #ndvi = numpy.select([denominador > 0, denominador == 0],\
        #[(dados[3].astype(numpy.float32) - dados[2].astype(numpy.float32))/\
        #(denominador+(denominador==0)),-99])

        mask = denominador > 0

        ndvi = numpy.choose(mask, (-99, ((dados[3].astype(numpy.float32) -\
        dados[2].astype(numpy.float32)) / (denominador+(denominador==0)))))

        soma = soma + ndvi.size #soma a quantidade de pixels

        outBand.WriteArray(ndvi,j,i) #salva o bloco na nova imagem, na mesma posição
                                     #que estava na imagem original

        #----------                        ----------#

outBand.FlushCache() #Coloca os dados no disco
outBand.SetNoDataValue(-99) #Seta a propriedade sem valor para -99
#estatisticas = outBand.GetStatistics(0,1) #Coloca as estatisticas da imagem na imagem
#outDataSet.SetProjection(projecao) #coloca a projeção da imagem original na nova

#print estatisticas #imprimi as estatisticas da imagem

outDataSet = None # Limpa a memoria, tem que ser usado para fechar o arquivo
dataSet = None

print soma #imprimi a soma de pixels
print somar

#cria uma imagem colorida com as bandas 1, 2 e 3 da imagem aberta
#os.system('gdal_translate -of jpeg -b 1 -b 2 -b 3 '+nome+' '+nome[:nome.find('.')+1]+'jpg')

finalTempo = time.time() #pega o tempo final

print 'Tempo: ' + str(finalTempo - comecoTempo) + ' segundos.' #imprimi o tempo para executar
