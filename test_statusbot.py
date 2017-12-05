import pytest
import multiprocessing
from multiprocessing import Process, Queue
import statusbot

def test_handle_leech_text():
    test_string = 'ruan.bekker has leeched 50%'
    should_be_queue = statusbot.handle_leech_text(test_string, True)
    assert isinstance(should_be_queue, multiprocessing.queues.Queue)
    test_string = 'this is not a leech text type'
    should_not_be_queue = statusbot.handle_leech_text(test_string, True)
    assert not should_not_be_queue