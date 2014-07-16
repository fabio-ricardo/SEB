#coding:utf-8
from Tkinter import *
import math
from tkFileDialog import askopenfilename
from tkMessageBox import *

Ta = 0
angle = 0
d = 0
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
		if self.ang.get().isdigit() and self.dia.get().isdigit() and self.alt.get().isdigit() and self.T.get().isdigit() and (nome[-4:] == '.tif' or nome[-5:] == '.tiff'):
			global angle, d, z, Ta,nomeFile
			angle = math.pi*(90 -float(self.ang.get()))/180
			d = 1+0.033*math.cos((2*math.pi* float(self.dia.get()))/365)
			z = float(self.alt.get())
			Ta = float(self.T.get())
			nomeFile = nome
			self.fechar()
		else: 
			if (nome[-4:] <> '.tif' or nome[-5:] <> '.tiff'):
				self.erro()
			else:
				self.erroDigito()

	def fechar(self): 
		self.raiz.destroy()
	
	def escreveNome(self):
		global nome
		nome = askopenfilename()
		Label(self.raiz,text=nome).grid(row=12, column=1,sticky=W, pady=5)

inst1=Tk()
Griding(inst1)
inst1.mainloop()


