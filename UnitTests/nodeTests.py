import pytest


from board import Node, Piece, Board, Player
from gui import Gui
class first_move_tests:
    def first_node(self):
        board = Board()
        player1 = Player("Player 1", board)

        assert player1.place_piece(player1.pieces[2], "a7")

    def second_node(self):
        board = Board()
        player1 = Player("Player 1", board)

        assert player1.place_piece(player1.pieces[0], "f4")

    def third_node(self):
        board = Board()
        player1 = Player("Player 1", board)

        assert player1.place_piece(player1.pieces[1], "c5")

class second_move_tests:
    def first_move(self):
        board = Board()
        player1 = Player("Player 1", board)
        player2 = Player("player 2", board)

        player1.place_piece(player1.pieces[2], "a7")
        assert player2.place_piece(player2.pieces[2], "g7")

    def second_move(self):
        board = Board()
        player1 = Player("Player 1", board)
        player2 = Player("player 2", board)

        player1.place_piece(player1.pieces[2], "b6")
        assert player2.place_piece(player2.pieces[2], "f6")

    def third_move(self):
        board = Board()
        player1 = Player("Player 1", board)
        player2 = Player("player 2", board)

        player1.place_piece(player1.pieces[2], "c5")
        assert player2.place_piece(player2.pieces[2], "e5")