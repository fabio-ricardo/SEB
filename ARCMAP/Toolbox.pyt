import arcpy
import toPython as toPy
import imageIO as imgIO
import numpy

class Toolbox(object):
    def __init__(self):
        self.label =  "Landsat 5 - TM"
        self.alias  = "landsat5tmentrar"

        # List of tool classes associated with this toolbox
        self.tools = [executarFuncao]

class executarFuncao(object):
    def __init__(self):
        self.label       = "Landsat 5 - TM"
        self.description = "Executa a função prédefinida na imagem escolhida."

    def getParameterInfo(self):
        #Define parameter definitions

        # Input Features parameter
        entradaImagem = arcpy.Parameter(
            displayName="Imagem",
            name="entradaImagem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        entradaFuncao = arcpy.Parameter(
            displayName="Funcao",
            name="entradaFuncao",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        entradaFuncaoParams = arcpy.Parameter(
            displayName="Parametros Funcao",
            name="entradaFuncaoParams",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        parameters = [entradaImagem,entradaFuncao,entradaFuncaoParams]

        return parameters

    def execute(self, parameters, messages):
        self.nomeImagem = parameters[0].valueAsText
        i = len(self.nomeImagem)-1
        posPath = 0
        posExt = 0

        while(i > 0):
            if(self.nomeImagem[i] == '\\'):
                posPath = i
                break

            if(self.nomeImagem[i] == '.'):
                posExt = i

            i = i - 1

        self.endArquivoImg = self.nomeImagem[:posPath+1]
        self.extensaoImg = self.nomeImagem[posExt:]
        self.nomeImagem = self.nomeImagem[posPath+1:]

        #----------

        self.nomeFuncao = parameters[1].valueAsText

        i = len(self.nomeFuncao)-1
        posPath = 0

        while(i > 0):
            if(self.nomeFuncao[i] == '\\'):
                posPath = i
                break

            i = i - 1

        self.endArquivoFunc = self.nomeFuncao[:posPath+1]
        self.nomeFuncao = self.nomeFuncao[posPath+1:]

        #----------

        try:
            self.arquivo = open(parameters[2].valueAsText,'r')
        except:
            arcpy.AddError("Erro ao abrir o arquivo de parametros.")

        #----------

        self.dadosArq = self.arquivo.read().split('\n')
        self.dadosArq = self.dadosArq[:len(self.dadosArq)-1]

        self.arquivo.close()

        #----------

        self.codigo = toPy.analisarETransformar(self.endArquivoFunc,self.nomeFuncao)

        if(self.codigo[0] == False):
            self.labelAviso.setText(u""+self.codigo[1])
        else:
            #----------

            auxValPar = ''

            for i in xrange(len(self.codigo[4])):
                if(self.dadosArq[i][0] == 'B'):
                    auxValPar = auxValPar + 'bandas['+str(i)+']' + ','
                else:
                    auxValPar = auxValPar + str(self.dadosArq[i]) + ','

            self.parametros = auxValPar[:len(auxValPar)-1]

            #----------

            self.bandas = imgIO.abrirELer(self.endArquivoImg,self.nomeImagem)

            #----------

            self.retorno = toPy.executar(self.codigo,self.bandas,self.parametros)

            #----------

            self.terminado = imgIO.salvar(self.nomeImagem,self.retorno,self.codigo[3],self.endArquivoImg,self.extensaoImg)