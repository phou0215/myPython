import binascii


hex_val = "61626364"
text_val = "SM-G950N GM188219XV"


def encoder(val, mode='string'):

    return_data = None
    data = bytes(val, encoding="ascii")
    enc = binascii.hexlify(data)
    if mode == 'string':
        return_data = str(enc, 'ascii')
    else:
        return_data = enc
    return return_data


def decoder(val, mode='string'):

    return_data = None
    dnc = binascii.unhexlify(val)
    if mode == 'string':
        return_data = str(dnc, 'ascii')
    else:
        return_data = dnc
    return return_data

print(decoder(hex_val))
print(encoder(text_val))

# value_1 = None
# value_2 = ''
# value_3 = 'asdasdad'
# value_4 = 1231314.123
# value_5 = '1231314.123'
#
# def check_value(value):
#
#     return_data = None
#     if value is None or value == '':
#         return_data = '-'
#     else:
#         try:
#             return_data = float(value)
#         except:
#             return_data = str(value)
#
#     return return_data
#
# print(type(check_value(value_1)))
# print(check_value(value_2))
# print(check_value(value_3))
# print(type(check_value(value_4)))
# print(type(check_value(value_5)))
