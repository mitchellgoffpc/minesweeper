#!/usr/bin/env python

import argparse
import curses
import random


# Helper classes
class Game:
    WON = 'Won'
    LOST = 'Lost'
    PLAY = 'Play'

class Cell:
    FLAGGED = 'Flagged'
    CLEARED = 'Cleared'
    FILLED = 'Filled'

class State:
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.game = Game.PLAY
        self.cursor = [0, 0]
        self.mines = generateMines()
        self.cells = [[Cell.FILLED for i in range(WIDTH)]
                                   for j in range(HEIGHT)]



# Run loop
def main(stdscr):
    state = State()
    key = None

    while key != ord('q'):
        display(stdscr, state)
        key = stdscr.getch()
        respond(state, key)



# Display the minesweeper board
def display(stdscr, state):
    if state.game == Game.WON:
        header = "Congratulations, you won! Press 'r' to play again"
        commands = ['r - restart']
    elif state.game == Game.LOST:
        header = "Whoops, you hit a mine! Press 'r' to play again"
        commands = ['r - restart']
    elif state.game == Game.PLAY:
        header = "Choose a cell using the arrow keys"
        commands = ['ENTER - dig', 'f - flag']

    stdscr.clear()
    stdscr.addstr(0, 0, header)

    # Draw the board
    stdscr.addstr(2, 0, ' '.join('+{}+'.format('-' * WIDTH)))

    for row in range(HEIGHT):
        string = ''.join(charForCell(state, row, col) for col in range(WIDTH))
        stdscr.addstr(row + 3, 0, ' '.join('|{}|'.format(string)))

    stdscr.addstr(HEIGHT + 3, 0, ' '.join('+{}+'.format('-' * WIDTH)))
    stdscr.addstr(HEIGHT + 5, 0, 'Instructions:')
    for i, line in enumerate(commands + ['q - quit']):
        stdscr.addstr(HEIGHT + 7 + i, 0, line)

    # Position the cursor
    row, col = state.cursor
    stdscr.move(row + 3, col * 2 + 2)
    stdscr.refresh()

def charForCell(state, row, col):
    if state.cells[row][col] == Cell.FILLED:
        return '#'
    elif state.cells[row][col] == Cell.FLAGGED:
        return '!'
    elif state.cells[row][col] == Cell.CLEARED:
        mines = adjacentMines(state, row, col)

        if mines == 0:
            return ' '
        else:
            return str(mines)



# Respond to the user's action
def respond(state, key):
    row, col = state.cursor

    if state.game != Game.PLAY:
        if key == ord('r'):
            state.refresh()
    elif key == curses.KEY_UP:
        state.cursor[0] = max(0, state.cursor[0] - 1)
    elif key == curses.KEY_DOWN:
        state.cursor[0] = min(HEIGHT - 1, state.cursor[0] + 1)
    elif key == curses.KEY_LEFT:
        state.cursor[1] = max(0, state.cursor[1] - 1)
    elif key == curses.KEY_RIGHT:
        state.cursor[1] = min(WIDTH - 1, state.cursor[1] + 1)
    elif key == 10: # curses.KEY_ENTER is unreliable
        click(state, row, col)
    elif key == ord('f'):
        flag(state, row, col)

def flag(state, row, col):
    if state.cells[row][col] == Cell.FILLED:
        state.cells[row][col] = Cell.FLAGGED
    elif state.cells[row][col] == Cell.FLAGGED:
        state.cells[row][col] = Cell.FILLED

def click(state, row, col):
    if state.cells[row][col] != Cell.FILLED:
        return
    elif (row, col) in state.mines:
        state.game = Game.LOST
    else:
        uncover(state, row, col)

        if all(state.cells[row][col] != Cell.FILLED
               for row in range(HEIGHT)
               for col in range(WIDTH)):
            state.game = Game.WON

def uncover(state, row, col):
    if (0 <= row < HEIGHT and
        0 <= col < WIDTH and
        state.cells[row][col] == Cell.FILLED):

        state.cells[row][col] = Cell.CLEARED

        if adjacentMines(state, row, col) == 0:
            [uncover(state, row + i, col + j)
                for i in (-1, 0, 1)
                for j in (-1, 0, 1)
                if (i, j) != (0, 0)]



# Helper functions
def generateMines():
    mines = set()

    while len(mines) < NUM_MINES:
        cell = (random.randint(0, HEIGHT - 1),
                random.randint(0, WIDTH - 1))

        mines.add(cell)

    return mines

def adjacentMines(state, row, col):
    return sum(
        (row + i, col + j) in state.mines
        for i in (-1, 0, 1)
        for j in (-1, 0, 1))



# Initialize the game and start the run loop
description = "A simple text-based implementation of the classic game Minesweeper"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--width',
                    type = int,
                    default = 10,
                    help = 'the width of the minesweeper board (default: 10)')
parser.add_argument('--height',
                    type = int,
                    default = 10,
                    help = 'the height of the minesweeper board (default: 10)')
parser.add_argument('--mines',
                    type = int,
                    default = 15,
                    help = 'the number of mines to place on the board (default: 15)')

args = parser.parse_args()
WIDTH = args.width
HEIGHT = args.height
NUM_MINES = args.mines
curses.wrapper(main)
