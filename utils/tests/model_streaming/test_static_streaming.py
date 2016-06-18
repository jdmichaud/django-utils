# -*- coding: utf-8 -*-
from decimal import Decimal
from bitfield import BitField

from django.conf import settings
from django.test import TestCase
from django.db.models import loading
from django.db.models.loading import load_app
from django.core.management import call_command

from utils.model_streaming.static_streaming import model_static_to_dict
from utils.model_streaming.static_streaming import bitfield_static_to_dict
from utils.model_streaming.model_streaming import filter_fields

from fakeapp.models import ModelToDictTestModel


class ModelStreamingTest(TestCase):
  def setUp(self):
    pass

  def test_filter_fields(self):
    class TestField:
      def __init__(self, name): self.name = name
    tests = [
      {
        'included_fields': None,
        'excluded_fields': None,
        'model_name': 'testNameField',
        'fields': [TestField('field1'), TestField('field2'), TestField('field3')],
        'expected_outcome': [TestField('field1'), TestField('field2'), TestField('field3')],
      },
      {
        'included_fields': ['testNameField.field2'],
        'excluded_fields': None,
        'model_name': 'testNameField',
        'fields': [TestField('field1'), TestField('field2'), TestField('field3')],
        'expected_outcome': [TestField('field2')],
      },
      {
        'included_fields': None,
        'excluded_fields': ['testNameField.field2'],
        'model_name': 'testNameField',
        'fields': [TestField('field1'), TestField('field2'), TestField('field3')],
        'expected_outcome': [TestField('field1'), TestField('field3')],
      },
      {
        'included_fields': ['testNameField.field2'],
        'excluded_fields': ['testNameField.field1'],
        'model_name': 'testNameField',
        'fields': [TestField('field1'), TestField('field2'), TestField('field3')],
        'expected_outcome': [TestField('field1'), TestField('field2'), TestField('field3')],
      },
    ]
    for test in tests[:-1]:
      observed_outcome = filter_fields(test['included_fields'], test['excluded_fields'], test['model_name'], test['fields'])
      self.assertEquals([f.name for f in test['expected_outcome']], [f.name for f in observed_outcome])
    self.assertRaises(ValueError, filter_fields, tests[-1]['included_fields'], tests[-1]['excluded_fields'], tests[-1]['model_name'], tests[-1]['fields'])

  def test_bitfield_static_to_dict(self):
    class StaticTestClass:
      OPTION_TUPLE_TYPE = ('label1', 'label2')
      option_tuple = BitField(flags=OPTION_TUPLE_TYPE, default=2)
      OPTION_LIST_TYPE = ['label3', 'label4']
      option_list = BitField(flags=OPTION_LIST_TYPE, default=0)
      OPTION_TUPLE_OF_TUPLE_TYPE = [('X', 'label5'), ('Y', 'label6')]
      option_tuple_of_tuple = BitField(flags=OPTION_TUPLE_OF_TUPLE_TYPE, default=0)
    # define the expected outcome
    expected_outcome_option_tuple = [{ 'checked': False,  'label': 'label1' }, { 'checked': True, 'label': 'label2' }]
    expected_outcome_option_list = [{ 'checked': False, 'label': 'label3' }, { 'checked': False, 'label': 'label4' }]
    expected_outcome_option_tuple_of_tuple = [{ 'checked': False, 'label': 'label5' }, { 'checked': False, 'label': 'label6' }]
    # Call the API and compare with the expected outcome
    observed_outcome = bitfield_static_to_dict(StaticTestClass, StaticTestClass.option_tuple)
    self.assertEquals(expected_outcome_option_tuple, observed_outcome)
    observed_outcome = bitfield_static_to_dict(StaticTestClass, StaticTestClass.option_list)
    self.assertEquals(expected_outcome_option_list, observed_outcome)
    observed_outcome = bitfield_static_to_dict(StaticTestClass, StaticTestClass.option_tuple_of_tuple)
    self.assertEquals(expected_outcome_option_tuple_of_tuple, observed_outcome)

  # Test the dump of the static model
  def test_model_static_to_dict(self):
    expected_outcome = {
      'integer': -578423,
      'positive_integer': 578423,
      'postitive_small_integer': 12,
      'small_integer': -12,
      'boolean': False,
      'decimal': Decimal('1.25'),
      'option': { 'selected': 2, 'labels': ['Option 1', 'Option 2', 'Option 3', 'Option 4'] },
      'bitfield': [{'checked': True, 'label': 'Type 1'},
                   {'checked': True, 'label': 'Type 2'},
                   {'checked': True, 'label': 'Type 3'},
                   {'checked': False, 'label': 'Type 4'},
                   {'checked': False, 'label': 'Type 5'},
                   {'checked': False, 'label': 'Type 6'}]
    }
    observed_outcome = model_static_to_dict(ModelToDictTestModel)
    self.assertEquals(expected_outcome, observed_outcome)
