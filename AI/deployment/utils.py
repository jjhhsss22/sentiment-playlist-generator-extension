
# convert numpy array to python list
def to_list(array) -> list:
    return array.tolist()

# round all values in a list
def round_list(values: list, decimals=1) -> list:
    return [round(v, decimals) for v in values]