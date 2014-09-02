#coding: utf-8
import numpy

#----------
descBandas = numpy.zeros([8,8],dtype=numpy.float) #array com a descrição das bandas

#descBandas[1][0] = 'azul' #Cor da banda, o Indice é o numero da banda
descBandas[1][1] = 0.45 #Comprimento de Onda - 'Menor'
descBandas[1][2] = 0.52 #Comprimento de Onda - 'Maior'
descBandas[1][3] = -1.52 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[1][4] = 193.0 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[1][5] = 1957.0 #Irradiância Espectral no Topo da Atmosfera
descBandas[1][6] = (descBandas[1][4] - descBandas[1][3]) / 255.0 # (b[i] - a[i]) / 255

#descBandas[2][0] = 'verde' #Cor da banda, o Indice é o numero da banda
descBandas[2][1] = 0.52 #Comprimento de Onda - 'Menor'
descBandas[2][2] = 0.60 #Comprimento de Onda - 'Maior'
descBandas[2][3] = -2.84 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[2][4] = 365.0 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[2][5] = 1826.0 #Irradiância Espectral no Topo da Atmosfera
descBandas[2][6] = (descBandas[2][4] - descBandas[2][3]) / 255.0 # (b[i] - a[i]) / 255

#descBandas[3][0] = 'vermelho' #Cor da banda, o Indice é o numero da banda
descBandas[3][1] = 0.63 #Comprimento de Onda - 'Menor'
descBandas[3][2] = 0.69 #Comprimento de Onda - 'Maior'
descBandas[3][3] = -1.17 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[3][4] = 264.0 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[3][5] = 1554.0 #Irradiância Espectral no Topo da Atmosfera
descBandas[3][6] = (descBandas[3][4] - descBandas[3][3]) / 255 # (b[i] - a[i]) / 255

#descBandas[4][0] = 'IV-próximo' #Cor da banda, o Indice é o numero da banda
descBandas[4][1] = 0.76 #Comprimento de Onda - 'Menor'
descBandas[4][2] = 0.79 #Comprimento de Onda - 'Maior'
descBandas[4][3] = -1.51 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[4][4] = 221.0 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[4][5] = 1036.0 #Irradiância Espectral no Topo da Atmosfera
descBandas[4][6] = (descBandas[4][4] - descBandas[4][3]) / 255.0 # (b[i] - a[i]) / 255

#descBandas[5][0] = 'IV-médio' #Cor da banda, o Indice é o numero da banda
descBandas[5][1] = 1.55 #Comprimento de Onda - 'Menor'
descBandas[5][2] = 1.75 #Comprimento de Onda - 'Maior'
descBandas[5][3] = -0.37 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[5][4] = 30.2 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[5][5] = 215.0 #Irradiância Espectral no Topo da Atmosfera
descBandas[5][6] = (descBandas[5][4] - descBandas[5][3]) / 255.0 # (b[i] - a[i]) / 255

#descBandas[6][0] = 'IV-termal' #Cor da banda, o Indice é o numero da banda
descBandas[6][1] = 10.4 #Comprimento de Onda - 'Menor'
descBandas[6][2] = 12.5 #Comprimento de Onda - 'Maior'
descBandas[6][3] = 1.2378 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[6][4] = 15.303 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[6][5] = 0 #Irradiância Espectral no Topo da Atmosfera. Não existe nesta banda
descBandas[6][6] = (descBandas[6][4] - descBandas[6][3]) / 255.0 # (b[i] - a[i]) / 255

#descBandas[7][0] = 'IV-médio' #Cor da banda, o Indice é o numero da banda
descBandas[7][1] = 2.08 #Comprimento de Onda - 'Menor'
descBandas[7][2] = 2.35 #Comprimento de Onda - 'Maior'
descBandas[7][3] = -0.15 #Coeficiente de Calibração - 'a' - radiancia expectral
descBandas[7][4] = 16.5 #Coeficiente de Calibração - 'b' - radiancia expectral
descBandas[7][5] = 80.67 #Irradiância Espectral no Topo da Atmosfera
descBandas[7][6] = (descBandas[7][4] - descBandas[7][3]) / 255.0 # (b[i] - a[i]) / 255
#----------

somatIrradiancia = descBandas[1][5] + descBandas[2][5] + descBandas[3][5]\
                   + descBandas[4][5] + descBandas[5][5] \
                   + descBandas[7][5]

descBandas[1][7] = descBandas[1][5] / somatIrradiancia
descBandas[2][7] = descBandas[2][5] / somatIrradiancia
descBandas[3][7] = descBandas[3][5] / somatIrradiancia
descBandas[4][7] = descBandas[4][5] / somatIrradiancia
descBandas[5][7] = descBandas[5][5] / somatIrradiancia
descBandas[7][7] = descBandas[7][5] / somatIrradiancia
