from django.db import models
from bitfield import BitField
from to_dict import choices_to_dict
from to_dict import bitfield_to_dict


#
# Functions for streaming static models
#
def choices_static_to_dict(cls, field):
  # Get the default value, or empty string if none set
  default = field.default if hasattr(field, 'default') else ''
  # Return the dict with default as value
  return choices_to_dict(field.choices, default)


def bitfield_static_to_dict(cls, field):
  # Get the default value, or 0 if none set
  default = field.default if hasattr(field, 'default') else 0
  # Get the flags
  flags = field.labels
  # Call bitfield_static_to_dict with a 0 value for static
  return bitfield_to_dict(flags, default)


# The method streams to JSON a class (static model) by considering the default
# value or just 0 when default is not specified.
def model_static_to_dict(cls, **kwargs):
  """This method stream static data of model to a dict.
  This includes fields with choices (options) and fields with default values
  Keyword arguments:
  cls -- the class of the model containing the static data to stream
  """
  # the dictionary containing the static data
  data = {}
  # retrieve all the concrete fields
  opts = cls._meta
  fields = opts.concrete_fields
  # Go through all those fields
  for field in fields:
    # for the field having a member 'choices' and thif field being not empty
    if hasattr(field, 'choices') and field.choices:
      data[field.name] = choices_static_to_dict(cls, field)
    # For bitfields
    elif isinstance(field, BitField):
      data[field.name] = bitfield_static_to_dict(cls, field)
    # for the field having a member 'default'
    elif (hasattr(field, 'default')
          and field.default != models.fields.NOT_PROVIDED
          and field.default is not None):
      data[field.name] = field.default() if callable(field.default) else field.default
  return data
