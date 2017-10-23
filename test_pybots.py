import pybots_data

s = 'daniel.burke89'
b = bytearray()
b.extend(map(ord, s))
print(pybots_data.get_status(s))

