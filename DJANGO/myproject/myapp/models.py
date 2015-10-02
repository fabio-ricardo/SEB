# -*- coding: utf-8 -*-
from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='imagem/')

class Document2(models.Model):
    funcfile = models.FileField(upload_to='funcao/')

class Document3(models.Model):
    bandfile = models.FileField(upload_to='banda/')