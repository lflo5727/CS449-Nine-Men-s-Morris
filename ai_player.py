from typing import List, Dict
from collections import deque
import logging

from board import Board, Player

log = logging.getLogger(__name__)

class Move:
    def __init__(self, player_id, phase, src = None, dest = None, remove = None):
        self.src = src
        self.dest = dest
        self.remove = remove
        self.player_id = player_id

class SimulatedBoard:
    fake_board = Board()
    init_board = {}
    neighbors = {}

    for node in fake_board.get_nodes():
        init_board[node.name] = 0
        neighbors[node.name] = [n.name for n in node.neighbors()]

    def __init__(self, p1_id, p2_id):
        self.board = dict(init_board)
        self.p1_id = p1_id
        self.p2_id = p2_id

    def init_board_state(self, board):
        for node in board.get_nodes():
            if node.is_occupied():
                self.board[node.name] = node.piece.player.id

    def copy(self):
        sim_board = SimulatedBoard(self.p1_id, self.p2_id)
        sim_board.board = dict(self.board)
        return sim_board

    def get_opponent(self, p_id)
        return self.p2_id if p_pi == self.p1_id else self.p1_id

    def do(self, move):
        if move.src and not move.dest: #place
            self.board[move.src] = move.player_id
        elif move.src and move.dest: #move
            self.board[move.src] = 0
            self.board[move.dest] = move.player_id

        if move.remove:
            board[move.remove] = 0

    def undo(self, move):
        if move.src and not move.dest: #place
            self.board[move.src] = 0
        elif move.src and move.dest: #move
            self.board[move.src] = move.player_id
            self.board[move.dest] = 0

        if move.remove:
            board[move.remove] = get_opponent(move.player_id)

    def evaluate_board(self):
        pass

    def get_mills(self):
        pass

    def get_part_mills(self):
        pass

class AI_Player(Player):
    def __init__(self, name, id, board: "Board", opponent: "Player"):
        super().__init__(name, id, board)
        self.opponent = opponent
    
    def get_best_move(self):
        pass

    def alpha_beta(self):
        pass

    def generate_moves(self):
        pass

