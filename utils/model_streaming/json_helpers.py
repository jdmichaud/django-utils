# -*- coding: utf-8 -*-
import json
import decimal


class DecimalEncoder(json.JSONEncoder):
  def _iterencode(self, o, markers=None):
    if isinstance(o, decimal.Decimal):
      # wanted a simple yield str(o) in the next line,
      # but that would mean a yield on the line with super(...),
      # which wouldn't work (see my comment below), so...
      # !! WARNING !!
      # !! WARNING !! The use of float here makes the Decimal useless !!
      # !! WARNING !!
      return (str(o) for o in [float(o)])
    return super(DecimalEncoder, self)._iterencode(o, markers)
