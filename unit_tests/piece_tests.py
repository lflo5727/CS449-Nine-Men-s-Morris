import pytest
import pygame

from board import Node, Piece, Board, Player
import nine_mens_morris
from gui import Gui

def pieces_display():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    assert player1.pieces

def phase1_remove_test():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    player1.place_piece(player1.pieces[1], "a7")
    player2.place_piece(player2.pieces[1], "g7")
    player1.place_piece(player1.pieces[2], "a4")
    player2.place_piece(player2.pieces[2], "g4")
    player1.place_piece(player1.pieces[3], "a1")
    player2.place_piece(player2.pieces[3], "d1")

    player2.remove_piece(player2, player1.pieces[3])

    assert player2.get_phase() == 1


def phase2_remove_test():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    player1.place_piece(player1.pieces[1], "a7")
    player2.place_piece(player2.pieces[1], "g7")
    player1.place_piece(player1.pieces[2], "a4")
    player2.place_piece(player2.pieces[2], "g4")
    player1.place_piece(player1.pieces[3], "d1")
    player2.place_piece(player2.pieces[3], "d5")

    player1.place_piece(player1.pieces[4], "b6")
    player2.place_piece(player2.pieces[4], "f6 ")
    player1.place_piece(player1.pieces[5], "c5")
    player2.place_piece(player2.pieces[5], "b4")
    player1.place_piece(player1.pieces[6], "f4")
    player2.place_piece(player2.pieces[6], "e3")

    player1.place_piece(player1.pieces[7], "d6")
    player2.place_piece(player2.pieces[7], "c4")
    player1.place_piece(player1.pieces[8], "e4")
    player2.place_piece(player2.pieces[8], "d2")
    player1.place_piece(player1.pieces[0], "d3")
    player2.place_piece(player2.pieces[0], "d6")

    player1.move_piece(player1.pieces[3], "a1")

    player2.remove_piece(player2, player1.pieces[3])

    assert player2.get_phase() == 2

def place_all_pieces():
        board = Board()
        player1 = Player("Player 1", board)
        player2 = Player("player 2", board)

        player1.place_piece(player1.pieces[1], "a7")
        player2.place_piece(player2.pieces[1], "g7")
        player1.place_piece(player1.pieces[2], "a4")
        player2.place_piece(player2.pieces[2], "g4")
        player1.place_piece(player1.pieces[3], "d1")
        player2.place_piece(player2.pieces[3], "d5")

        player1.place_piece(player1.pieces[4], "b6")
        player2.place_piece(player2.pieces[4], "f6 ")
        player1.place_piece(player1.pieces[5], "c5")
        player2.place_piece(player2.pieces[5], "b4")
        player1.place_piece(player1.pieces[6], "f4")
        player2.place_piece(player2.pieces[6], "e3")

        player1.place_piece(player1.pieces[7], "d6")
        player2.place_piece(player2.pieces[7], "c4")
        player1.place_piece(player1.pieces[8], "e4")
        player2.place_piece(player2.pieces[8], "d2")
        player1.place_piece(player1.pieces[0], "d3")
        player2.place_piece(player2.pieces[0], "d6")

        assert True

def piece_gone():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    player1.place_piece(player1.pieces[1], "a7")
    player2.place_piece(player2.pieces[1], "g7")
    player1.place_piece(player1.pieces[2], "a4")
    player2.place_piece(player2.pieces[2], "g4")
    player1.place_piece(player1.pieces[3], "a1")
    player2.place_piece(player2.pieces[3], "d1")

    player2.remove_piece(player2, player1.pieces[3])

    piece_removed = True
    for item in player2.get_placed_pieces():
        if item == player2.pieces[3]:
            piece_removed = False

    assert piece_removed

def move_neighbor():
    board = Board()
    player1 = Player("Player 1", board)
    player2 = Player("player 2", board)

    player1.place_piece(player1.pieces[1], "a7")
    player2.place_piece(player2.pieces[1], "g7")
    player1.place_piece(player1.pieces[2], "a4")
    player2.place_piece(player2.pieces[2], "g4")
    player1.place_piece(player1.pieces[3], "d1")
    player2.place_piece(player2.pieces[3], "d5")

    player1.place_piece(player1.pieces[4], "b6")
    player2.place_piece(player2.pieces[4], "f6 ")
    player1.place_piece(player1.pieces[5], "c5")
    player2.place_piece(player2.pieces[5], "b4")
    player1.place_piece(player1.pieces[6], "f4")
    player2.place_piece(player2.pieces[6], "e3")

    player1.place_piece(player1.pieces[7], "d6")
    player2.place_piece(player2.pieces[7], "c4")
    player1.place_piece(player1.pieces[8], "e4")
    player2.place_piece(player2.pieces[8], "d2")
    player1.place_piece(player1.pieces[0], "d3")
    player2.place_piece(player2.pieces[0], "d6")

    assert player1.move_piece(player1.pieces[3], "a1")






