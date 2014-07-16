#coding: utf-8
import gdal, osgeo, time, numpy, sys, math
from gdalconst import *
from constantes import *
from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import *

inicio = time.time()

Ta = 0
cosZ = 0
dr = 0
z = 0 
nomeFile = ''

class Griding:
	def __init__(self,raiz):
		self.raiz = raiz
		self.raiz.title('CALCULO S-SEBI')
		
		Label(self.raiz,text='Solar Elevation Angle (graus):').grid(row=5, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Dia Sequencial do Ano:').grid(row=7, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Altitude do pixel (m):').grid(row=9, column=1,sticky=W, pady=5)
		Label(self.raiz,text='Temperatura do ar (K):').grid(row=11, column=1,sticky=W, pady=5)
		
		self.msg=Label(self.raiz,text=' CALCULO ALGORTIMO S-SEBI ',fg='black',font=('Verdana','14','bold'))
		self.msg.grid(row=2, column=1, columnspan=3)
		
		self.msg=Label(self.raiz,text='Clique em OK para iniciar o calculo')
		self.msg.grid(row=14, column=1, columnspan=2)
		
		self.ang=Entry(self.raiz, width=10)
		self.ang.grid(row=5, column=3, sticky=E+W, pady=3)
		self.ang.focus_force()
		
		self.dia=Entry(self.raiz, width=10)
		self.dia.grid(row=7, column=3, sticky=E+W, pady=3)
		self.dia.focus_force()
		
		self.alt=Entry(self.raiz, width=10)
		self.alt.grid(row=9, column=3, sticky=E+W, pady=3)
		self.alt.focus_force()
		
		self.T=Entry(self.raiz, width=10)
		self.T.grid(row=11, column=3, sticky=E+W, pady=3)
		self.T.focus_force()
		
		self.arq=Button(self.raiz, width=15, command=self.escreveNome,text='Selecionar imagem',bg = 'gray')
		self.arq.grid(row=12, column=3, padx=2, pady=3)
		
		self.ok=Button(self.raiz, width=8, command=self.inicia,text='OK',bg = 'gray')
		self.ok.grid(row=13, column=1, padx=2, pady=3)
		
		self.close=Button(self.raiz, width=8, command=self.fechar,text='Fechar', bg = 'gray')
		self.close.grid(row=13, column=2, padx=2, pady=3)
	
	def erroDigito(self):
		    showerror("Erro", "Números devem ser inteiros e não nulos!")
	
	def erro(self):
		    showerror("Erro", "Arquivo não é uma imagem TIFF.")
		
		
	def inicia(self):
		#if self.ang.get().isdigit() and self.dia.get().isdigit() and self.alt.get().isdigit() and self.T.get().isdigit():
		global angle, dr, cosZ, Ta,nomeFile
		cosZ = math.pi*(90 -float(self.ang.get()))/180
		dr = 1+0.033*math.cos((2*math.pi* float(self.dia.get()))/365)
		z = float(self.alt.get())
		Ta = float(self.T.get())
		nomeFile = nome
		self.fechar()
		#else: 
			#if (nome[-4:] <> '.tif' or nome[-5:] <> '.tiff'):
			#	self.erro()
			
		#	self.erroDigito()

	def fechar(self): 
		self.raiz.destroy()
	
	def escreveNome(self):
		global nome
		nome = askopenfilename()
		Label(self.raiz,text=nome).grid(row=12, column=1,sticky=W, pady=5)

inst1=Tk()
Griding(inst1)
inst1.mainloop()


driver = gdal.GetDriverByName('GTiff')
driver.Register()


entrada = gdal.Open(nomeFile,GA_ReadOnly)
if entrada is None:
    print 'Erro ao abrir o arquivo: ' + nomeFile
    sys.exit(1)

linhas = entrada.RasterYSize
colunas = entrada.RasterXSize
NBandas = entrada.RasterCount
driverEntrada = entrada.GetDriver()

print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driverEntrada.ShortName

#----------

pi = math.pi
#cosZ = math.cos((90 - 56.98100422)*pi/180) # pego do metadata da imagem - SUN_ELEVATION
#dr = 1+0.033*math.cos((272*2*pi)/365) # 29 de setembro de 2011
ap = 0.03
#z = 200
tsw = 0.75 + 2*0.00001 * z
p2 = 1 / (tsw * tsw)
L = 0.5
K1 = 607.76
K2 = 1260.56
constSB = 0.0000000567
S = 1367
radOndaCurtaInci = S * cosZ * dr * tsw
Ea = 0.85 * math.pow(-1 * math.log(tsw),0.09)
#Ta = 295
radOndaLongaInci = Ea * constSB * math.pow(Ta,4)
qtdPontos = 20
x1 = 0.1
x2 = 0.9
x2x1 = x2 - x1

#----------

saidaAlbedoSuper = driver.Create('albedoSuperficie.tif',colunas,linhas,1,GDT_Float64)
if saidaAlbedoSuper is None:
    print 'Erro ao criar o arquivo: ' + 'albedoSuperficie.tif'
    sys.exit(1)

saidaNDVI = driver.Create('ndvi.tif',colunas,linhas,1,GDT_Float64)
if saidaNDVI is None:
    print 'Erro ao criar o arquivo: ' + 'ndvi.tif'
    sys.exit(1)

saidaSAVI = driver.Create('savi.tif',colunas,linhas,1,GDT_Float64)
if saidaSAVI is None:
    print 'Erro ao criar o arquivo: ' + 'savi.tif'
    sys.exit(1)

saidaIAF = driver.Create('iaf.tif',colunas,linhas,1,GDT_Float64)
if saidaIAF is None:
    print 'Erro ao criar o arquivo: ' + 'iaf.tif'
    sys.exit(1)

saidaTempSuper = driver.Create('temperatura_superficie.tif',colunas,linhas,1,GDT_Float64)
if saidaTempSuper is None:
    print 'Erro ao criar o arquivo: ' + 'temperatura_superficie.tif'
    sys.exit(1)

saidaSaldoRad = driver.Create('saldoRadiacao.tif',colunas,linhas,1,GDT_Float64)
if saidaSaldoRad is None:
    print 'Erro ao criar o arquivo: ' + 'saldoRadiacao.tif'
    sys.exit(1)

saidaFluxoCalSolo = driver.Create('fluxoCalorSolo.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxoCalSolo is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSolo.tif'
    sys.exit(1)

#----------

bandaEntrada = numpy.empty([NBandas+1],dtype=osgeo.gdal.Band)
bandaEntrada[0] = 0
p1 = numpy.empty([NBandas+1],dtype=numpy.float64)
p1[0] = 0
p1[6] = 0

limSupEsq = numpy.zeros([qtdPontos],dtype=numpy.float64)
limInfEsq = numpy.zeros([qtdPontos],dtype=numpy.float64)
limEsqPVez = True

limSupDir = numpy.zeros([qtdPontos],dtype=numpy.float64)
limInfDir = numpy.zeros([qtdPontos],dtype=numpy.float64)
limDirPVez = True

# ----------

for k in range(1,NBandas+1):
    bandaEntrada[k] = entrada.GetRasterBand(k)

    if (k != 6):
        p1[k] = pi / (descBandas[k][5] * cosZ * dr)

bandaAlbedoSuper = saidaAlbedoSuper.GetRasterBand(1)
bandaNDVI = saidaNDVI.GetRasterBand(1)
bandaSAVI = saidaSAVI.GetRasterBand(1)
bandaIAF = saidaIAF.GetRasterBand(1)
bandaTempSuper = saidaTempSuper.GetRasterBand(1)
bandaSaldoRad = saidaSaldoRad.GetRasterBand(1)
bandaFluxoCalSolo = saidaFluxoCalSolo.GetRasterBand(1)

#----------

xBlockSize = 256
yBlockSize = 256

for i in range(0,linhas,yBlockSize):
    if i + yBlockSize < linhas:
        lerLinhas = yBlockSize
    else:
        lerLinhas = linhas - i

    for j in range(0,colunas,xBlockSize):
        if j + xBlockSize < colunas:
            lerColunas = xBlockSize
        else:
            lerColunas = colunas - j

        #----------

        dados = numpy.empty([NBandas+1,lerLinhas,lerColunas],dtype=numpy.float64)
        dados[0] = 0

        for k in range(1,NBandas+1):
            dados[k] = bandaEntrada[k].ReadAsArray(j,i,lerColunas,lerLinhas).astype(numpy.float64)

        #----------

        albedoPlanetrio = 0

        for k in range(1,NBandas+1):
            if (k == 6):
                radianciaB6 = descBandas[k][3] + (descBandas[k][6] * dados[k])
            else:
                radiancia = descBandas[k][3] + (descBandas[k][6] * dados[k])
                reflectancia = p1[k] * radiancia

                if (k == 3):
                    reflectanciaB3 = reflectancia
                if (k == 4):
                    reflectanciaB4 = reflectancia

                albedoPlanetrio = albedoPlanetrio + (descBandas[k][7] * reflectancia)

        dados = None
        radiancia = None
        reflectancia = None

        ndvi = (reflectanciaB4 - reflectanciaB3) / (reflectanciaB4 + reflectanciaB3)
        bandaNDVI.WriteArray(ndvi,j,i)

        albedoSuperficie = (albedoPlanetrio - ap) * p2
        bandaAlbedoSuper.WriteArray(albedoSuperficie,j,i)

        albedoPlanetrio = None

        savi = ((1 + L) * (reflectanciaB4 - reflectanciaB3)) / (L + (reflectanciaB4 + reflectanciaB3))
        bandaSAVI.WriteArray(savi,j,i)

        reflectanciaB4 = None
        reflectanciaB3 = None

        numpy.seterr(all='ignore')

        maskLog = ((0.69 - savi) / 0.59) > 0

        iaf = numpy.choose(maskLog, (0.0, -1 * (numpy.log((0.69 - savi) / 0.59) / 0.91)))
        bandaIAF.WriteArray(iaf,j,i)

        numpy.seterr(all='warn')

        savi = None

        ENB = 0.97 + 0.00331 * iaf
        E0 = 0.95 + 0.01 * iaf

        iaf = None

        temperaturaSuperficie = K2 / numpy.log(((ENB * K1) / radianciaB6) + 1)
        bandaTempSuper.WriteArray(temperaturaSuperficie,j,i)

        radianciaB6 = None
        ENB = None

        radOndaLongaEmi = (E0 * constSB) * (temperaturaSuperficie*temperaturaSuperficie*\
                                            temperaturaSuperficie*temperaturaSuperficie)

        saldoRadiacao = radOndaCurtaInci * (1 - albedoSuperficie) - radOndaLongaEmi +\
                        radOndaLongaInci - (1 - E0) * radOndaLongaInci
        bandaSaldoRad.WriteArray(saldoRadiacao,j,i)

        E0 = None
        radOndaLongaEmi = None

        fluxoCalSolo = ((temperaturaSuperficie - 273.15) * (0.0038 + (0.0074 * albedoSuperficie))\
                       * (1 - (0.98 * (ndvi*ndvi*ndvi*ndvi)))) * saldoRadiacao
        bandaFluxoCalSolo.WriteArray(fluxoCalSolo,j,i)

        ndvi = None
        saldoRadiacao = None
        fluxoCalSolo = None

        #----------

        maskAlbedoSuper = albedoSuperficie <= 0.2
        limiteLadoEsq = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = albedoSuperficie >= 0.75
        limiteLadoDir = temperaturaSuperficie[maskAlbedoSuper]

        maskAlbedoSuper = None
        albedoSuperficie = None
        temperaturaSuperficie = None

        limiteLadoEsq = numpy.sort(limiteLadoEsq)
        limiteLadoDir = numpy.sort(limiteLadoDir)

        limSupEsqAux = limiteLadoEsq[::-1][0:qtdPontos]
        limInfEsqAux = limiteLadoEsq[0:qtdPontos]

        limSupDirAux = limiteLadoDir[::-1][0:qtdPontos]
        limInfDirAux = limiteLadoDir[0:qtdPontos]

        limiteLadoEsq = None
        limiteLadoDir = None

        if (limSupEsqAux.size > 0):
            if (limEsqPVez):
                limSupEsq = numpy.sort(limSupEsqAux)[::-1][0:qtdPontos]
                limInfEsq = numpy.sort(limInfEsqAux)[0:qtdPontos]
                limEsqPVez = False
            else:
                limSupEsq = numpy.sort(numpy.concatenate((limSupEsq,limSupEsqAux)))[::-1][0:qtdPontos]
                limInfEsq = numpy.sort(numpy.concatenate((limInfEsq,limInfEsqAux)))[0:qtdPontos]

        if (limSupDirAux.size > 0):
            if (limDirPVez):
                limSupDir = numpy.sort(limSupDirAux)[::-1][0:qtdPontos]
                limInfDir = numpy.sort(limInfDirAux)[0:qtdPontos]
                limDirPVez = False
            else:
                limSupDir = numpy.sort(numpy.concatenate((limSupDir,limSupDirAux)))[::-1][0:qtdPontos]
                limInfDir = numpy.sort(numpy.concatenate((limInfDir,limInfDirAux)))[0:qtdPontos]

        limSupEsqAux = None
        limInfEsqAux = None
        limSupDirAux = None
        limInfDirAux = None

        #----------

#----------

bandaEntrada = None
entrada = None
bandaNDVI = None
saidaNDVI = None
bandaSAVI = None
saidaSAVI = None
bandaIAF = None
saidaIAF = None

#----------

limSupEsq = numpy.sum(limSupEsq) / qtdPontos
limInfEsq = numpy.sum(limInfEsq) / qtdPontos

limSupDir = numpy.sum(limSupDir) / qtdPontos
limInfDir = numpy.sum(limInfDir) / qtdPontos

m1 = (limSupDir - limSupEsq) / x2x1
m2 = (limInfDir - limInfEsq) / x2x1

c1 = ((x2 * limSupEsq) - (x1 * limSupDir)) / x2x1
c2 = ((x2 * limInfEsq) - (x1 * limInfDir)) / x2x1

#----------

saidaFracEvapo = driver.Create('fracaoEvaporativa.tif',colunas,linhas,1,GDT_Float64)
if saidaFracEvapo is None:
    print 'Erro ao criar o arquivo: ' + 'fracaoEvaporativa.tif'
    sys.exit(1)

saidaFluxCalSensi = driver.Create('fluxoCalorSensivel.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxCalSensi is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorSensivel.tif'
    sys.exit(1)

saidaFluxCalLaten = driver.Create('fluxoCalorLatente.tif',colunas,linhas,1,GDT_Float64)
if saidaFluxCalLaten is None:
    print 'Erro ao criar o arquivo: ' + 'fluxoCalorLatente.tif'
    sys.exit(1)

#----------

bandaFracEvapo = saidaFracEvapo.GetRasterBand(1)
bandaFluxCalSensi = saidaFluxCalSensi.GetRasterBand(1)
bandaFluxCalLaten = saidaFluxCalLaten.GetRasterBand(1)

#----------

albedoSuperficie = bandaAlbedoSuper.ReadAsArray()
temperaturaSuperficie = bandaTempSuper.ReadAsArray()

#----------

fracaoEvaporativa = (c1 + (m1 * albedoSuperficie) - temperaturaSuperficie) / ((c1 - c2) + ((m1 - m2) * albedoSuperficie))
bandaFracEvapo.WriteArray(fracaoEvaporativa,0,0)

albedoSuperficie = None
temperaturaSuperficie = None

saldoRadiacao = bandaSaldoRad.ReadAsArray()
fluxoCalSolo = bandaFluxoCalSolo.ReadAsArray()

fluxoCalorSensivel = (1 - fracaoEvaporativa) * (saldoRadiacao - fluxoCalSolo)
bandaFluxCalSensi.WriteArray(fluxoCalorSensivel,0,0)

fluxoCalorSensivel = None

fluxoCalorLatente = fracaoEvaporativa * (saldoRadiacao - fluxoCalSolo)
bandaFluxCalLaten.WriteArray(fluxoCalorLatente,0,0)

fluxoCalorLatente = None

#----------

saldoRadiacao = None
fluxoCalSolo = None
fracaoEvaporativa = None

#----------

bandaAlbedoSuper = None
saidaAlbedoSuper = None
bandaTempSuper = None
saidaTempSuper = None
bandaSaldoRad = None
saidaSaldoRad = None
bandaFluxoCalSolo = None
saidaFluxoCalSolo = None
bandaFracEvapo = None
saidaFracEvapo = None
bandaFluxCalSensi = None
saidaFluxCalSensi = None
bandaFluxCalLaten = None
saidaFluxCalLaten = None

#----------

fim = time.time()

print 'Tempo total: '+str(fim - inicio)+' segundos.'
