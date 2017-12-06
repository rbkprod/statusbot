from collections import namedtuple
import command_handler
import pytest
def test_get_command():
    get_cmd = command_handler.get_command('status @TESTID')
    assert isinstance(get_cmd[0], str)
    assert len(get_cmd[1]) >= 1
    get_cmd = command_handler.get_command('status')
    assert len(get_cmd[1]) == 0
def test_create_command():
    get_tuple = command_handler.create_command('status', 'U5PU8069F', False)
    assert isinstance(get_tuple, tuple)
    assert len(get_tuple) == 4
    assert get_tuple.is_admin
def test_get_status():
    cmdtuple = namedtuple('Cmd', 'cmd caller_id is_admin params')
    cmd = cmdtuple('status', 'U5PU8069F', False, [])
    get_status = command_handler.get_status(cmd)
    assert isinstance(get_status, str)
def test_call_command():
     #with pytest.raises(IndexError):
     cmd = command_handler.call_command('noncommand', '@CallerID', False)
     assert cmd.startswith('There was a problem')
def test_get_list_command():
    #with pytest.raises(ValueError):
    lst = command_handler.call_command('list slkdl', '@CallerID', False) 
    assert isinstance(lst, str)
    lst = command_handler.call_command('list warn', '@CallerId', False)
    assert lst
def test_is_valid_command():
    is_valid = command_handler.is_valid_command('this is not a command')
    assert not is_valid
    is_valid = command_handler.is_valid_command('status')
    assert is_valid