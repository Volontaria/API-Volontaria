from django.db import models
from orderable.models import Orderable
from ckeditor.fields import RichTextField


class InfoSection(Orderable):

    is_active = models.BooleanField('Actif', default=True)
    title = models.CharField('Titre', max_length=255)
    content = RichTextField('Contenu')
    is_accordion = models.BooleanField('Accordeon', default=True)

    class Meta(Orderable.Meta):
        verbose_name = 'Section page informations'
        verbose_name_plural = 'Sections page informations'

    def __str__(self):
        return self.title
