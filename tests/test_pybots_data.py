import random
import pytest
import pybots_data

def test_add_user_to_list():
    #random_id = random.randint(1, 100000)
    pybots_data.add_user_to_list('testid', 12)
    users_in_warn = pybots_data.get_list('warn')
    assert 'testid' in users_in_warn
    pybots_data.add_user_to_list('testid', 18)
    users_in_warn = pybots_data.get_list('wban')
    assert 'testid' in users_in_warn
    pybots_data.add_user_to_list('testid', 27)
    users_in_warn = pybots_data.get_list('ban')
    assert 'testid' in users_in_warn

def test_del_user_from_list():
    pybots_data.del_user_from_list('testid', 12)
    users_in_warn = pybots_data.get_list('warn')
    assert 'testid' not in users_in_warn
    pybots_data.del_user_from_list('testid', 18)
    users_in_warn = pybots_data.get_list('warn')
    assert 'testid' not in users_in_warn
    pybots_data.del_user_from_list('testid', 27)
    users_in_warn = pybots_data.get_list('warn')
    assert 'testid' not in users_in_warn
    
#test_add_user_to_list()