# -*- coding: utf-8 -*-

import json
import datetime

from django.conf import settings
from django.test import TestCase
from django.db.models import loading
from django.db.models.loading import load_app
from django.core.management import call_command

from utils.model_streaming.model_streaming import model_to_dict

from fakeapp.models import SimpleForeignKey
from fakeapp.models import ManyToManyModel
from fakeapp.models import OneToOneModel
from fakeapp.models import ModelToDictTestModel
from fakeapp.models import CyclicForeignKey
from fakeapp.models import SimpleRelatedFieldModel
from fakeapp.models import ComplexRelatedFieldModel
from fakeapp.models import RelatedToRelatedFieldModel


class ModelStreamingTest(TestCase):
  def setUp(self):
      self.maxDiff = None
      print ">>", settings.INSTALLED_APPS
      self.old_INSTALLED_APPS = settings.INSTALLED_APPS
      settings.INSTALLED_APPS += ( 'utils.tests.fakeapp', )
      loading.cache.loaded = False
      load_app('utils.tests.fakeapp')
      call_command('syncdb', verbosity=0, interactive=False) # Create tables for fakeapp

  def tearDown(self):
      settings.INSTALLED_APPS = self.old_INSTALLED_APPS
      print "<<", settings.INSTALLED_APPS

  # Common function to build the complex model object used to test the streaming
  def build_model(self):
    self.simple_foreign_object = SimpleForeignKey(
      integer=999,
      char="this is subfield"
    )
    self.simple_foreign_object.save()
    self.cyclic_foreign_object = CyclicForeignKey(
      char="this is a cyclic relation example",
      model_to_dict=None
    )
    self.cyclic_foreign_object.save()
    self.many_to_many_object_1 = ManyToManyModel(integer=1)
    self.many_to_many_object_1.save()
    self.many_to_many_object_2 = ManyToManyModel(integer=2)
    self.many_to_many_object_2.save()
    self.many_to_many_object_3 = ManyToManyModel(integer=3)
    self.many_to_many_object_3.save()
    self.one_to_one_object = OneToOneModel(integer=456)
    self.one_to_one_object.save()
    self.model = ModelToDictTestModel(
      integer=-125313,
      positive_integer=75615,
      postitive_small_integer=5,
      small_integer=-2,
      null_boolean=None,
      char="This is a charfiéld",
      text="This is a\n\nmulti-line\ntext\narea\nsome stranges characters follow Â¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ",
      boolean=True,
      # binary="1001"
      date=datetime.datetime(2008, 8, 9),
      datetime=datetime.datetime(2008, 8, 9, 16, 00, 00),
      ip_address_field="192.168.1.0",
      comma_separated_integer_fields="12,58913,-531",
      # filef=
      # filepath
      floatf=1.253541,
      # image
      url="http://www.nike.com/baskets",
      slug="this-is-a-slug",
      email="robert@user.co.uk",
      decimal=1.23,
      option='B',
      bitfield=9,
      simple_foreign_key=self.simple_foreign_object,
      cyclic_foreign_key=self.cyclic_foreign_object,
      one_to_one=self.one_to_one_object,
    )
    self.model.save()
    self.model.many_to_many.add(self.many_to_many_object_1)
    self.model.many_to_many.add(self.many_to_many_object_2)
    self.model.many_to_many.add(self.many_to_many_object_3)
    # Establish the cycle
    self.cyclic_foreign_object.model_to_dict = self.model
    self.cyclic_foreign_object.save()
    # Building related models
    self.simple_related_object = SimpleRelatedFieldModel(
      integer=421,
      model_to_dict=self.model,
    )
    self.simple_related_object.save()
    self.simple_related_object2 = SimpleRelatedFieldModel(
      integer=422,
      model_to_dict=self.model,
    )
    self.simple_related_object2.save()
    self.complex_related_object = ComplexRelatedFieldModel(
      integer=442,
      model_to_dict=self.model,
    )
    self.complex_related_object.save()
    self.related_to_related_object = RelatedToRelatedFieldModel(
      integer=789,
      complex_related_field=self.complex_related_object,
    )
    self.related_to_related_object.save()

  # Test the dump of a dynamically allocated object of a model
  def test_model_to_dict(self):
    self.build_model()
    expected_outcome = {
      'id': self.model.pk,
      '_ms_type': 'ModelToDictTestModel',
      'integer': -125313,
      'positive_integer': 75615,
      'postitive_small_integer': 5,
      'small_integer': -2,
      'null_boolean': None,
      'char': "This is a charfiéld",
      'text': "This is a\n\nmulti-line\ntext\narea\nsome stranges characters follow Â¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ",
      'boolean': True,
      'date': json.dumps(datetime.datetime(2008, 8, 9).strftime('%Y-%m-%dT%H:%M:%S')).replace('"', ''),
      'datetime': json.dumps(datetime.datetime(2008, 8, 9, 16, 00, 00).strftime('%Y-%m-%dT%H:%M:%S')).replace('"', ''),
      'ip_address_field': "192.168.1.0",
      'comma_separated_integer_fields': "12,58913,-531",
      'floatf': 1.253541,
      'url': "http://www.nike.com/baskets",
      'slug': "this-is-a-slug",
      'email': "robert@user.co.uk",
      'decimal': 1.23,
      'option': { 'selected': 1, 'labels': ['Option 1', 'Option 2', 'Option 3', 'Option 4'] },
      'bitfield': [{'checked': True,  'label': 'Type 1'},
                   {'checked': False, 'label': 'Type 2'},
                   {'checked': False, 'label': 'Type 3'},
                   {'checked': True,  'label': 'Type 4'},
                   {'checked': False, 'label': 'Type 5'},
                   {'checked': False, 'label': 'Type 6'}],
      'simple_foreign_key': {
        'id': self.simple_foreign_object.pk,
        '_ms_type': 'SimpleForeignKey',
        'integer': 999,
        'char': "this is subfield",
        'modeltodicttestmodel_set': [{'id': 1, '_ms_type': 'ModelToDictTestModel'}],
      },
      'cyclic_foreign_key': {
        'id': self.cyclic_foreign_object.pk,
        '_ms_type': 'CyclicForeignKey',
        'char': "this is a cyclic relation example",
        'model_to_dict': { 'id': self.model.pk, '_ms_type': 'ModelToDictTestModel' }, # When cycle is detected, id is set instead of object
        'modeltodicttestmodel_set': [{ 'id': self.model.pk, '_ms_type': 'ModelToDictTestModel' }]
      },
      'cyclicforeignkey_set': [{'id': 1, '_ms_type': 'CyclicForeignKey'}],
      'one_to_one': {
        'id': self.one_to_one_object.pk,
        '_ms_type': 'OneToOneModel',
        'integer': 456,
        'modeltodicttestmodel': {'id': 1, '_ms_type': 'ModelToDictTestModel'},
      },
      'many_to_many': [{'id': 1, 'integer': 1, '_ms_type': 'ManyToManyModel'},
                       {'id': 2, 'integer': 2, '_ms_type': 'ManyToManyModel'},
                       {'id': 3, 'integer': 3, '_ms_type': 'ManyToManyModel'}],
      'simplerelatedfieldmodel_set':
        [{ 'id': self.simple_related_object.pk, '_ms_type': 'SimpleRelatedFieldModel', 'integer': 421, 'model_to_dict': { 'id': self.model.pk, '_ms_type': 'ModelToDictTestModel' } },
         { 'id': self.simple_related_object2.pk, '_ms_type': 'SimpleRelatedFieldModel', 'integer': 422, 'model_to_dict': { 'id': self.model.pk, '_ms_type': 'ModelToDictTestModel' } }],
      'complexrelatedfieldmodel_set': [
        {
          'id': self.complex_related_object.pk,
          '_ms_type': 'ComplexRelatedFieldModel',
          'integer': 442,
          'model_to_dict': { 'id': self.model.pk, '_ms_type': 'ModelToDictTestModel' },
          'relatedtorelatedfieldmodel_set': [{
            'id': self.related_to_related_object.pk,
            '_ms_type': 'RelatedToRelatedFieldModel',
            'integer': 789,
            'complex_related_field': { 'id': self.complex_related_object.pk, '_ms_type': 'ComplexRelatedFieldModel' }
          }],
        }
      ]
    }
    observed_outcome = model_to_dict(self.model)
    self.assertEquals(expected_outcome, observed_outcome)
