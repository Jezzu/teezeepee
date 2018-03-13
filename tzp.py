import zmq
import curses

import argparse
import configparser
import threading
import time

from curses import wrapper

from client import Client
from ui import UI

def parse_args():
    parser = argparse.ArgumentParser(description='Client for teezeepee')

    # Please specify your username
    parser.add_argument('username',
                        type=str,
                        help='Specified username')

    parser.add_argument('--config-file',
                        type=str,
                        help='Default path for configuration file.')

    return parser.parse_args()


def display_section(window, display):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)

    while True:
        window.addstr(bottom_line, 1, display.recv_string())
        window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def input_section(window, chat_sender):
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()
    window.box()
    window.refresh()
    
    while True:
        window.clear()
        window.box()
        window.refresh()
        s = window.getstr(1, 1).decode('utf-8')
        if s is not None and s != "":
            chat_sender.send_string(s)
        
        # Short pause
        time.sleep(0.01)

