# -*- coding: utf-8 -*-
from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Selecione a imagem:'
    )

class DocumentForm2(forms.Form):
    funcfile = forms.FileField(
        label='Selecione a função:'
    )

class DocumentForm3(forms.Form):
    bandfile = forms.FileField(
        label='Selecione o parametro:'
    )