# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.db.models.loading import load_app

from fakeapp.models import FakeItem
from fakeapp.models import FakeItemParent
from fakeapp.models import FakeItemChildren

from utils.model_streaming.update_model_from_dict import update_model_from_dict


class UpdateModelFromDictTest(TestCase):
    def setUp(self):
        print ">", settings.INSTALLED_APPS
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += ( 'utils.tests.fakeapp', )
        loading.cache.loaded = False
        load_app('utils.tests.fakeapp')
        call_command('syncdb', verbosity=0, interactive=False) # Create tables for fakeapp

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS
        print "<", settings.INSTALLED_APPS

    def test_update_model_from_dict(self):
        # Prepare the database
        parent1 = FakeItemParent(char_field='fake_item_parent1')
        parent2 = FakeItemParent(char_field='fake_item_parent2')
        parent1.save()
        parent2.save()
        fake_item = FakeItem(
                char_field="fake_item",
                integer_field=4,
                boolean_field=True,
                non_mandatory_field='non_mandatory_field',
                foreign_key=parent1,
                time_field=datetime.time(hour=10, minute=1))
        fake_item.save()
        children1 = FakeItemChildren(
                char_field="fake_item_children1",
                foreign_key=fake_item)
        children2 = FakeItemChildren(
                char_field="fake_item_children2",
                foreign_key=fake_item)
        children3 = FakeItemChildren(
                char_field="fake_item_children3",
                foreign_key=fake_item)
        children1.save()
        children2.save()
        children3.save()
        # Prepare the dictionary
        # children1: untouched
        # children2: updated
        # children3: removed
        # new children
        fake_item_dict = {
            'char_field'           : 'fake_item_updated',
            'integer_field'        : 8,
            'boolean_field'        : False,
            'foreign_key'          : parent2.id,
            'time_field'           : '11:02:00',
            'fakeitemchildren_set' : [
                {
                    'id'        : children1.id,
                    'char_field': children1.char_field,
                    'foreign_key': fake_item.id,
                    'non_mandatory_field': children1.non_mandatory_field,
                    'added'     : True
                },
                {
                    'id'        : children2.id,
                    'char_field': 'fake_item_children2_updated',
                    'foreign_key': fake_item.id,
                    'added'     : True
                },
                {
                    'char_field' : 'fake_item_new_children',
                    'foreign_key': fake_item.id,
                    'added'      : True
                }
            ]
        }
        # update the model
        update_model_from_dict(fake_item, fake_item_dict)
        # Test outcome
        fake_item = FakeItem.objects.get(pk=fake_item.id)
        self.assertEquals(fake_item_dict['char_field'], fake_item.char_field)
        self.assertEquals(fake_item_dict['integer_field'], fake_item.integer_field)
        self.assertEquals(fake_item_dict['boolean_field'], fake_item.boolean_field)
        self.assertEquals(fake_item_dict['foreign_key'], fake_item.foreign_key.id)
        self.assertEquals(fake_item_dict['time_field'], str(fake_item.time_field))
        self.assertEquals('non_mandatory_field', fake_item.non_mandatory_field)
        self.assertEquals(len(fake_item_dict['fakeitemchildren_set']), len(fake_item.fakeitemchildren_set.all()))
        self.assertTrue(children1.id in [y.id for y in fake_item.fakeitemchildren_set.all()])
        self.assertTrue(children2.id in [y.id for y in fake_item.fakeitemchildren_set.all()])
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][0]['char_field'], fake_item.fakeitemchildren_set.get(id=1).char_field)
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][0]['foreign_key'], fake_item.fakeitemchildren_set.get(id=1).foreign_key.id)
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][1]['char_field'], fake_item.fakeitemchildren_set.get(id=2).char_field)
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][1]['foreign_key'], fake_item.fakeitemchildren_set.get(id=2).foreign_key.id)
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][2]['char_field'], fake_item.fakeitemchildren_set.get(id=3).char_field)
        self.assertEquals(fake_item_dict['fakeitemchildren_set'][2]['foreign_key'], fake_item.fakeitemchildren_set.get(id=3).foreign_key.id)

