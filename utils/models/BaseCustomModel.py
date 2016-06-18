from uuid import uuid4
from django.db import models


class BaseCustomModel(models.Model):
  uuid = models.CharField(max_length=37, editable=False)
  added = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  # Custom save command to manage the UUID
  def save(self, *args, **kwargs):
    if not self.uuid:
      self.uuid = uuid4().hex
    super(BaseCustomModel, self).save()

  # This model is abstract and shall not generate a table
  class Meta:
      abstract = True
