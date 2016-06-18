# -*- coding: utf-8 -*-

from django.db import models
from workflow.classes import Context, StatusHistory
from workflow.tests.fakeapp.fake_item_states import FAStateConstructor

class FakeItem(models.Model):
    name = models.CharField(max_length=37)

    def __init__(self, *args, **kwargs):
        super(FakeItem, self).__init__(*args, **kwargs)
        self.context = Context(self,
                               FakeItemStatusHistory,
                               FAStateConstructor)

# The status history table will keep track of status changes for 
# FaeItems as they will be updated during their lifetime. 
# The current column gives the current status of the FaeItem.
class FakeItemStatusHistory(StatusHistory):
    model = models.ForeignKey(FakeItem)

    class Meta:
        verbose_name = 'FakeItem status history'
