def getValue(value, vtype):
    if vtype == "double":
        return "%.15e"%value
    elif vtype == "float":
        return "%.6e"%value
    else:
        return value
