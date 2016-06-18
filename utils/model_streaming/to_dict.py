# Convert a choice to the canonical JSON representation
def choices_to_dict(choices, value):
  # Get the human readable label of each choice
  labels = [label for code, label in choices]
  # Get the index of the value character or 0 by default
  value_index = next((index for index, couple in enumerate(choices) if value == couple[0]), 0)
  # build the dictionary
  return {'selected': value_index, 'labels': labels}


# Convert a bitfield to the canonical JSON representation
def bitfield_to_dict(labels, value):
  return [{ 'checked': 1 << index & value != 0, 'label': label} for index, label in enumerate(labels)]
