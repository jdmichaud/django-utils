import sys

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.db.models.loading import load_app

from fakeapp.models import FakeItem

class TestWorkflow(TestCase):

    def setUp(self):
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += ( 'workflow.tests.fakeapp', )
        load_app('workflow.tests.fakeapp')
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0, interactive=False) #Create tables for fakeapp

    def tearDown(self):
        pass
#        settings.INSTALLED_APPS = self.old_INSTALLED_APPS

    def test_workflow(self):
        item = FakeItem.objects.create(name="blah")
        self.assertTrue('CREATED' == str(item.context.get_last_status()))
        item.context.go_next('TEST_SYSTEM')
        self.assertTrue('EMAILED' == str(item.context.get_last_status()))
        item.context.go_next('TEST_SYSTEM')
        self.assertTrue('CONSULTED' == str(item.context.get_last_status()))
        item.context.go_next('TEST_SYSTEM')
        self.assertTrue('PROVIDED' == str(item.context.get_last_status()))
