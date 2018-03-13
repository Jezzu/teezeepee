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
    window.bkgd(curses.A_NORMAL)
    window.scrollok(1)

    while True:
        window.addstr(bottom_line, 1, display.recv_string())
        window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def input_section(window, chat_sender):
    window.bkgd(curses.A_NORMAL)
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


def main(stdscr):
    config_file = args.config_file if args.config_file is not None else 'tzp.cfg'
    config = configparser.ConfigParser()
    config.read(config_file)
    config = config['default']

    receiver = zmq.Context().instance().socket(zmq.PAIR)
    receiver.bind("inproc://clientchat")

    sender = zmq.Context().instance().socket(zmq.PAIR)
    sender.connect("inproc://clientchat")

    client = Client(args.username, config['server_host'],
                        config['chat_port'], receiver)
    client.run()

    show_receiver = zmq.Context().instance().socket(zmq.PAIR)
    show_receiver.bind("inproc://clientdisplay")

    show_sender = zmq.Context().instance().socket(zmq.PAIR)
    show_sender.connect("inproc://clientdisplay")

    ui = UI(config['server_host'], config['display_port'], show_sender)
    ui.run()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    curses.echo()
    curses.curs_set(0)

    window_height = curses.LINES
    window_width = curses.COLS
    divider =  int(window_height * 0.5)

    history_screen = stdscr.subpad(divider, window_width, 0, 0)
    input_screen = stdscr.subpad(window_height - divider, window_width, divider, 0)
    
    history_thread = threading.Thread(target=display_section, args=(history_screen, show_receiver))
    history_thread.daemon = True
    history_thread.start()

    input_thread = threading.Thread(target=input_section, args=(input_screen, sender))
    input_thread.daemon = True
    input_thread.start()

    history_thread.join()
    input_thread.join()


if '__main__' == __name__:
    try:
        args = parse_args()
        wrapper(main)

    except KeyboardInterrupt as e:
        pass
    except:
        raise

