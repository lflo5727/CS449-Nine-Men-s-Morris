import pytest


from board import Node, Piece, Board, Player
from gui import Gui

def firstMove():
    board = Board()
    player1 = Player("Player 1", board)

    assert player1.place_piece()

def secondMove():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    player1.place_piece()
    assert player2.place_piece()