# -*- coding: utf-8 -*-
import logging
from django.db import models
from django.db.models.fields import FieldDoesNotExist


# Remove element not present in the dictionary,
# create new element and call update_model_from_dict for
# existing instances
def update_related_from_list(instance, fieldname, l):
  related_field = getattr(instance, fieldname)
  # Remove instance in table not present in l
  for related_instance in [x for x in related_field.all() if x.id not in [y['id'] for y in l if 'id' in y]]:
    logging.debug('delete related_instance %s' % related_instance.id)
    related_instance.delete()
  # Create instance in table for element of the l without id
  for element in [x for x in l if 'id' not in x]:
    # first, pop all tags in the dictionary that are not model fields (eg. added)
    for unknown_key in [key for key, value in element.iteritems() if key not in related_field.model._meta.get_all_field_names()]:
      del element[unknown_key]
    # element must be a dictionary containing all the mandatory fields
    new_related_instance = related_field.create(**element)
    logging.debug('create related_instance %s' % new_related_instance.id)
  # Get all the related instances present in the dict
  # meaning instances that must be updated
  related_instances_to_update = [x for x in related_field.all() if x.id in [y['id'] for y in l if 'id' in y]]
  # Get a list of couples of the related_instance
  # and the associated dictionary
  couple_of_updates = [(x, next(y for y in l if 'id' in y and y['id'] == x.id)) for x in related_instances_to_update]
  # Perform the update on all the couples
  for related_instance, d in couple_of_updates:
    update_model_from_dict(related_instance, d)


# Take one instance and update its attributes depending on
# the content of the dictionary
def update_model_from_dict(instance, d):
  if not isinstance(d, dict):
    logging.debug(d)
    raise TypeError('d is not a dictionary')
  for key, value in d.iteritems():
    if isinstance(value, list): # related field
      update_related_from_list(instance, key, value)
    elif isinstance(value, dict): # ForeignKey field
      attr = getattr(instance, key)
      update_model_from_dict(attr, value)
    else: # All other types
      try:
        if isinstance(instance._meta.get_field_by_name(key)[0], models.ForeignKey):
          # we are dealing with a ForeignKey refered to by its id
          setattr(instance, key + '_id', value)
        else: # Just a plain scalar key
          setattr(instance, key, value)
      except FieldDoesNotExist as e:
        # We have an uknown field to our model (eg added), just ignore it.
        pass
  instance.save()
