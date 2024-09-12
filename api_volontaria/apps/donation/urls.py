# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:24:41 2020

@author: Nathalie
"""
from django.contrib import admin 
from django.urls import include, path

urlpatterns = [
    path('donation/', include('donation.urls')), 
    path('admin/', admin.site.urls), 
    ]

