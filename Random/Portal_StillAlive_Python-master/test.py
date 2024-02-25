
import time
import sys
import threading
import os
import shutil
import re
import signal
from pathlib import Path
cursor_x = 1
cursor_y = 1
print_lock = threading.Lock()

term = os.getenv("TERM", "vt100")
is_vt = re.search(r"vt(\d+)", term)

# xterm, rxvt, konsole ...
# but fbcon in linux kernel does not support screen buffer
enable_screen_buffer = not (is_vt or term == "linux")

# color support is after VT241
enable_color = not is_vt or int(re.search(r"\d+", is_vt.group()).group()) >= 241

term_columns, term_lines = 0, 0
if is_vt:
    term_columns, term_lines = 80, 24
else:
    term_columns, term_lines = shutil.get_terminal_size()

term_columns = int(os.getenv("COLUMNS", term_columns))
term_lines = int(os.getenv("LINES", term_lines))

if term_columns < 80 or term_lines < 24:
    print("the terminal size should be at least 80x24")
    sys.exit(1)

is_draw_end = False


ascii_art_width = 40
ascii_art_height = 20

credits_width = min((term_columns - 4) // 2, 56)
credits_height = term_lines - ascii_art_height - 2

lyric_width = term_columns - 4 - credits_width
lyric_height = term_lines - 2

credits_pos_x = lyric_width + 4

ascii_art_x = lyric_width + 4 + (credits_width - ascii_art_width) // 2
ascii_art_y = credits_height + 3

term = os.getenv("TERM", "vt100")
is_vt = re.search(r"vt(\d+)", term)

# xterm, rxvt, konsole ...
# but fbcon in linux kernel does not support screen buffer
enable_screen_buffer = not (is_vt or term == "linux")

# color support is after VT241
enable_color = not is_vt or int(re.search(r"\d+", is_vt.group()).group()) >= 241

enable_sound = '--no-sound' not in sys.argv

if enable_sound:
    import playsound

term_columns, term_lines = 0, 0
if is_vt:
    term_columns, term_lines = 80, 24
else:
    term_columns, term_lines = shutil.get_terminal_size()

term_columns = int(os.getenv("COLUMNS", term_columns))
term_lines = int(os.getenv("LINES", term_lines))

if term_columns < 80 or term_lines < 24:
    print("the terminal size should be at least 80x24")
    sys.exit(1)

is_draw_end = False

def sigint_handler(sig, frame):
    end_draw()
    print('Interrupt by user')
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def begin_draw():
    if enable_screen_buffer:
        print_lock.acquire()
        print('\033[?1049h', end='')
        print_lock.release()
    if enable_color:
        print_lock.acquire()
        print('\033[33;40;1m', end='')
        print_lock.release()


def end_draw():
    global is_draw_endaaaaaaaaaaaaaaa
    print_lock.acquire()
    is_draw_end = True
    if enable_color:
        print('\033[0m', end='')
    if enable_screen_buffer:
        print('\033[?1049l', end='')
    else:
        clear(False)
        move(1, 1, False, False)
    print_lock.release()

def move(x, y, update_cursor=True, mutex=True):
    global cursor_x, cursor_y
    global print_lock
    if(mutex):
        print_lock.acquire()
    print("\033[%d;%dH" % (y, x), end='')
    sys.stdout.flush()
    if(update_cursor):
        cursor_x = x
        cursor_y = y
    if(mutex):
        print_lock.release()


def clear(mutex=True):
    global cursor_x, cursor_y
    global print_lock
    cursor_x = 1
    cursor_y = 1
    if mutex:
        print_lock.acquire()
    print('\033[2J', end='')
    if mutex:
        print_lock.release()

# print with mutex lock and cursor update. Use this for convenience


def _print(str, newline=True):
    global cursor_x, cursor_y
    global print_lock
    print_lock.acquire()
    if(newline):
        print(str)
        cursor_x = 1
        cursor_y = cursor_y + 1
    else:
        print(str, end='')
        cursor_x = cursor_x + len(str)
    print_lock.release()


def clearLyrics():
    move(1, 2)
    for _ in range(lyric_height):
        _print('|' + ' ' * lyric_width)
    move(2, 2)


def drawLyrics(str, x, y, interval, newline):
    move(x + 2, y + 2)
    for ch in str:
        _print(ch, False)
        sys.stdout.flush()
        time.sleep(interval)
        x = x + 1
    if(newline):
        x = 0
        y = y + 1
        move(x + 2, y + 2)
    return x

import time

def drawFrame():
    # Draw the top border
    print(' ' + '-' * (term_columns - 2))

    # Draw the middle part
    for _ in range(term_lines - 2):
        print('|' + ' ' * (term_columns - 2) + '|')

    # Draw the bottom border
    print(' ' + '-' * (term_columns - 2))

    # Flush the output and wait for a second
    sys.stdout.flush()
    time.sleep(1)


dialog_x = 0
dialog_y = 0
drawFrame()
drawLyrics("Hello, World!", dialog_x, dialog_y, 0.1, True)
dialog_y += 1
drawLyrics("I am a Python program.", dialog_x, dialog_y, 0.1, True)
dialog_y += 1
dialog_x += 1
drawLyrics("I am running in a terminal.", dialog_x, dialog_y, 0.1, True)
drawLyrics("[red]This is stolen code lol.", dialog_x, dialog_y, 0, True)
time.sleep(1)