import pybots_data


if pybots_data.populate_db_id(True):
    print('Done')
else:
    print('Failed')

