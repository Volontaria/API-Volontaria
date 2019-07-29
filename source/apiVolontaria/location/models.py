from django.db import models
from django.core.exceptions import ValidationError


class Country(models.Model):
    """ Model for countries"""

    # iso_code corresponds to the ISO 3166 norm
    iso_code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=45, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["name", "iso_code"]


class StateProvince(models.Model):
    """ Model for states and provinces"""

    # iso_code corresponds to the ISO 3166 norm
    iso_code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=55, blank=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s" % (self.name, self.country.name)

    class Meta:
        verbose_name_plural = "StateProvinces"


class Address(models.Model):
    """Model for complete addresses"""
    address_line1 = models.CharField("Address line 1", max_length=45)
    address_line2 = models.CharField(
        "Address line 2",
        max_length=45,
        blank=True,
        default='',
    )
    postal_code = models.CharField("Postal Code", max_length=10)
    city = models.CharField(max_length=50, blank=False)
    state_province = models.ForeignKey(
        StateProvince,
        blank=False,
        on_delete=models.CASCADE,
    )
    country = models.ForeignKey(
        Country,
        blank=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%s, %s, %s, %s" % (self.address_line1,
                                   self.city,
                                   self.state_province.name,
                                   self.country.name,)

    def clean(self):
        if self.state_province.country != self.country:
            raise ValidationError(
                'The StateProvince should be linked to the Country'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(Address, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Addresses"
        unique_together = ("address_line1", "address_line2", "postal_code",
                           "city", "state_province", "country")
