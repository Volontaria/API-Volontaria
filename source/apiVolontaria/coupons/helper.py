# -*- coding: utf-8 -*-
import unicodedata


def remove_accents(input):
    nfkd_form = unicodedata.normalize('NFKD', input)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
