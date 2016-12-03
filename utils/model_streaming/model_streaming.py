import itertools
import json
from django.db import models
from utils.model_streaming.to_dict import choices_to_dict


def filter_fields(included_fields, excluded_fields, model_name, fields):
  """ Filter the fields according to the directives.
  Keyword arguments:
  included_fields -- field name that should be included. If None, all fields
  should be included.
  excluded_fields -- field name that should be filtered out. If None, no
  fields should be filtered out.
  model_name -- string containind the name of the model
  fields -- list of string which represents the field names
  """
  # Sanity check to make sure contradictory parameters
  if included_fields is not None and excluded_fields is not None:
    raise ValueError('included AND excluded fields specified')
  # Here we filter out all the field not related to this particular model
  included_fields = [name.split('.')[-1] for name in included_fields if name.startswith(model_name + '.')] if included_fields else None
  excluded_fields = [name.split('.')[-1] for name in excluded_fields if name.startswith(model_name + '.')] if excluded_fields else None
  # Then we filter according to the directives.
  if included_fields is not None:
    fields = filter(lambda field: field.name in included_fields, fields)
  elif excluded_fields is not None:
    fields = filter(lambda field: field.name not in excluded_fields, fields)
  return fields


#
# List of serializer to be used when going through the fields
# The visitor design pattern might be more appropriate
#
def default_serializer(instance, **kwargs):
  return instance


def Choice_serializer(instance, **kwargs):
  return choices_to_dict(kwargs['field'].choices, str(instance))


def BooleanField_serializer(instance, **kwargs):
  return instance


def CharField_serializer(instance, **kwargs):
  if hasattr(kwargs['field'], 'choices') and kwargs['field'].choices != []:
    # If it is a choice, convert to a dict
    return Choice_serializer(instance, **kwargs)
  else:
    # Else, just return the string value
    return instance


def BitField_serializer(instance, **kwargs):
  # Call bitfield_static_to_dict with a the value of the field
  return bitfield_to_dict(instance._labels, int(instance))


def OneToOneField_serializer(instance, **kwargs):
  return model_to_dict(instance, **kwargs)


def ManyToManyField_serializer(instance, **kwargs):
  return [model_to_dict(field, **kwargs) for field in instance.all()]


def DateTimeField_serializer(instance, **kwargs):
  return json.dumps(instance.strftime('%Y-%m-%dT%H:%M:%S')).replace('"', '')


def RelatedField_serializer(instance, **kwargs):
  # The hasattr is ugly but I don't how else to handle a RelatedManager, the class
  # is not even visible. Anyway, all is a public API so it's probably safer to
  # do that than to rely on a undocumented class which really is a implementation detail
  if hasattr(instance, 'all'):
    return [model_to_dict(field, **kwargs) for field in instance.all()]
  else:
    return model_to_dict(instance, **kwargs)


# Forward usage of model_to_dict. We have to use this trick so we can use
# model_to_dict in the map below.
def to_dict(instance, **kwargs):
  return model_to_dict(instance, **kwargs)

# Actual declaration of serializer_map
serializer_map = {
  models.CharField.__name__:          CharField_serializer,
#  models.BooleanField.__name__:       BooleanField_serializer,
  models.ForeignKey.__name__:         to_dict,
  models.OneToOneField.__name__:      OneToOneField_serializer,
  models.ManyToManyField.__name__:    ManyToManyField_serializer,
  models.DateField.__name__:           DateTimeField_serializer,
  models.DateTimeField.__name__:      DateTimeField_serializer,
  models.fields.related.ReverseManyToOneDescriptor.__name__: RelatedField_serializer,
  models.fields.related.ForeignObjectRel.__name__: RelatedField_serializer,
  models.fields.reverse_related.ManyToOneRel.__name__: RelatedField_serializer,
  'default':                          default_serializer
}


# All fields have a name in field.name.
# Related fields however are not exposing their actual name (the parent model
# attribute's name) but a namespaces name such as: 'devis:devisstatushistory'
# There is a special API to get the actual "accesor" name
def get_field_name(field):
  if hasattr(field, 'get_accessor_name'):
    # related field
    return field.get_accessor_name()
  # regular field
  return field.name


# model_to_dict shall manage related object without going back to the original model
# model_to_dict shall manage reference to the same model but with a different instance:
#  A(id=12) -> B(id=7) -> A(id=8)
def model_to_dict(instance, **kwargs):
  """ Convert a instance model to a dictionary.
  Keyword arguments:
  included_fields -- field name that should be included. If None, all fields
  should be included. Default == None.
  excluded_fields -- field name that should be filtered out. If None, no
  fields should be filtered out. Default == None.
  max_depth -- maximum depth in the nested field. Default == 100.
  """
  # The dict that will contain the streamed object
  d = { 'id': instance.pk, '_ms_type': instance.__class__.__name__ }
  # cycle check
  if 'ids' not in kwargs:
    # If ids is not initialized, do it
    kwargs['ids'] = []
  if (instance.pk, instance.__class__.__name__) in kwargs['ids']:
    # If the instance has already been visited, yield
    return d
  # if this is the first time we stream this instance, store its id
  kwargs['ids'].append((instance.pk, instance.__class__.__name__))
  # retrieve the parameters (use default values)
  included_fields = kwargs.get('included_fields', None)
  excluded_fields = kwargs.get('excluded_fields', None)
  # max_depth = kwargs.get('max_depth', 100)
  # enumerate all the fields (normal fields, foreign key, manyto..., related fields)
  opts = instance._meta
  fields = list(itertools.chain(opts.get_fields(include_hidden=True)))
  # Filter the fields
  fields = filter_fields(included_fields, excluded_fields, instance.__class__.__name__, fields)
  # for earch fields, call the appropriate serializer
  for field in fields:
    field_name = get_field_name(field)
    kwargs['field'] = field
    # retrieve the result and set it in the resulting dictionary
    try:
      d[field_name] = serializer_map[field.__class__.__name__](getattr(instance, field_name), **kwargs)
    except KeyError:
      # if no specialized serializer, fall back to default
      d[field_name] = serializer_map['default'](getattr(instance, field_name), **kwargs)
  # return the dictionary
  return d
