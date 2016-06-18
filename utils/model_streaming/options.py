# -*- coding: utf-8 -*-


# input: provice a list of options in the form:
# options = (
#   (A, "option 1"),
#   (B, "option 2"),
#   (C, "option 3"),
#   (D, "option 4")
# )
# and a character to identify the selection option (e.g. 'C')
# output: A couple containing the index and the list of labels in the form:
# (2, ["option 1", "option 2", "option 3", "option 4"])
def get_single_choice_data(type, value):
  return ({
    'selected': next(index for index, label in enumerate(type) if label[0] == value),
    'labels': [label[1] for label in type]
  })


# input: provice a list of options in the form:
# options = (
#  "option 1",
#   option 2",
#   option 3",
#   option 4"
# )
# and a bitfield representing which option is selected (e.g. 9)
# output: An option dictionary specifying which option is selected
# [{"checked": True,  label: "option 1"},
#  {"checked": False, label: "option 2"},
#  {"checked": False, label: "option 3"},
#  {"checked": True,  label: "option 4"}]
def get_multiple_choice_data(option, bitfield):
  return [{"checked": 1 << index & bitfield != 0, "label": label} for index, label in enumerate(option)]


# Convert a option dictionary in the form:
# [{"checked": True,  label: "option 1"},
#  {"checked": False, label: "option 2"},
#  {"checked": False, label: "option 3"},
#  {"checked": True,  label: "option 4"}]
# to a bitfield (e.g 9)
def reduce_array_to_bit_field(array):
  res = 0
  for index in [index for index, entry in enumerate(array) if entry['checked']]:
    res |= 1 << index
  return res
