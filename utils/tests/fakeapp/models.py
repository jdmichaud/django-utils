# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from django.db import models
from bitfield import BitField


###############################################################################
# To be decomissioned
###############################################################################
class FakeItemParent(models.Model):
    char_field = models.CharField(max_length=37)


class FakeItem(models.Model):
    char_field = models.CharField(max_length=37)
    integer_field = models.IntegerField()
    boolean_field = models.BooleanField(default=False)
    non_mandatory_field = models.CharField(max_length=37, blank=True, null=True)
    foreign_key = models.ForeignKey(FakeItemParent)
    time_field = models.TimeField()


class FakeItemChildren(models.Model):
    char_field = models.CharField(max_length=37)
    foreign_key = models.ForeignKey(FakeItem)
    non_mandatory_field = models.CharField(max_length=37, blank=True, null=True)
###############################################################################
###############################################################################
###############################################################################


###############################################################################
# These are the new model test classes
###############################################################################
class SimpleForeignKey(models.Model):
  # IntegerField
  integer = models.IntegerField(default=-578423)
  # CharField
  char = models.CharField(max_length=33, default='Some ForeignKey field')


class CyclicForeignKey(models.Model):
  # CharField
  char = models.CharField(max_length=33, default='Some ForeignKey field')
  # ForeignKey to ModelToDictTestModel
  model_to_dict = models.ForeignKey('ModelToDictTestModel', null=True)


class ManyToManyModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=669)


class OneToOneModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=670)


# A bif model that's suppose to contain all the possible common fields to test
# the streaming function (static and non static)
class ModelToDictTestModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=-578423)
  # PositiveIntegerField
  positive_integer = models.PositiveIntegerField(default=578423)
  # PositiveSmallIntegerField
  postitive_small_integer = models.PositiveSmallIntegerField(default=12)
  # SmallIntegerField
  small_integer = models.SmallIntegerField(default=-12)
  # NullBooleanField
  null_boolean = models.NullBooleanField()
  # CharField
  char = models.CharField(max_length=33)
  # TextField
  text = models.TextField()
  # boolean
  boolean = models.BooleanField(default=False)
  # BinaryField
  # binary = models.BinaryField()
  # date
  date = models.DateField(datetime.datetime(2008, 8, 9))
  # datetime
  datetime = models.DateTimeField(datetime.datetime(2008, 8, 9, 16, 00, 00))
  # GenericIPAddressField
  ip_address_field = models.GenericIPAddressField('192.0.2.30')
  # CommaSeparatedIntegerField
  comma_separated_integer_fields = models.CommaSeparatedIntegerField(max_length=33)
  # AutoField -- no need, as pk is an AutoKey
  # auto = models.AutoField()
  # FileField
  # filef = models.FileField()
  # FilePathField
  # filepath = models.FilePathField()
  # FloatField
  floatf = models.FloatField()
  # ImageField
  # image = models.ImageField()
  # URLField
  url = models.URLField()
  # SlugField
  slug = models.SlugField()
  # EmailField
  email = models.EmailField()
  # Decimal
  decimal = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('1.25'))
  # option
  OPTION_TYPE = (
    ('A', 'Option 1'),
    ('B', 'Option 2'),
    ('C', 'Option 3'),
    ('D', 'Option 4')
  )
  option = models.CharField(max_length=1, choices=OPTION_TYPE, default='C')
  # bitfield
  BITFIELD_TYPE = (
    ('A', 'Type 1'),
    ('B', 'Type 2'),
    ('C', 'Type 3'),
    ('D', 'Type 4'),
    ('E', 'Type 5'),
    ('F', 'Type 6'),
  )
  bitfield = BitField(flags=BITFIELD_TYPE, default=7)
  # foreign key
  simple_foreign_key = models.ForeignKey(SimpleForeignKey)
  # foreign key to an object having a foreign key
  #  to a different ModelToDictTestModel
  cyclic_foreign_key = models.ForeignKey(CyclicForeignKey, null=True)
  # RelatedField
  # simplerelatedfieldmodel_set
  # related_field with related_field
  # complexrelatedfieldmodel_set
  # many to many
  many_to_many = models.ManyToManyField(ManyToManyModel)
  # one to one
  one_to_one = models.OneToOneField(OneToOneModel)


class SimpleRelatedFieldModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=666)
  # link to model_to_dict
  model_to_dict = models.ForeignKey(ModelToDictTestModel)


class ComplexRelatedFieldModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=667)
  # link to model_to_dict
  model_to_dict = models.ForeignKey(ModelToDictTestModel)
  # RelatedField
  # relatedtorelatedfieldmodel_set


# This model points to a model itself pointing to the main test model (ModelToDict)
class RelatedToRelatedFieldModel(models.Model):
  # IntegerField
  integer = models.IntegerField(default=668)
  # link to the related model of ModelToDict
  complex_related_field = models.ForeignKey(ComplexRelatedFieldModel)
