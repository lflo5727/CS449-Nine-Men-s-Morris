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
    _fake_board = Board()
    _init_board = {}
    neighbors = {}
    ns_check = ['a4', 'b4', 'c4', 'e4', 'f4', 'g4', 'd2', 'd6']
    ew_check = ['d1', 'd2', 'd3', 'd5', 'd6', 'd7', 'b4', 'f4']

    for node in _fake_board.get_nodes():
        _init_board[node.name] = 0
        neighbors[node.name] = {x[0]: getattr(getattr(node, x), 'name', None) for x in ['north', 'east', 'south', 'west']}

    def __init__(self, p1_id, p2_id):
        self.board = dict(SimulatedBoard._init_board)
        self.p1_id = p1_id
        self.p2_id = p2_id

    def set_board_state(self, board):
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

    def get_mills(self):
        mills = {
            self.p1_id: [],
            self.p2_id: []
        }

        for i in [SimulatedBoard.ns_check, SimulatedBoard.ew_check]:
            if i == SimulatedBoard.ns_check:
                x, y = 'n', 's'
            else:
                x, y = 'e', 'w'

            for j in i:
                a = j
                b = SimulatedBoard.neighbors[j][x]
                c = SimulatedBoard.neighbors[j][y]
                a_player, b_player, c_player = self.board[a], self.board[b], self.board[c]
                if a_player != 0 and a_player == b_player == c_player:
                    mills[a_player].extend([a,b,c])

        return mills

    def evaluate_board(self, curr_player):
        score = 0

        player_mill_cnt, player_part_mill_cnt = 0, 0
        opponent_mill_cnt, opponent_part_mill_cnt = 0, 0

        for check in [SimulatedBoard.ns_check, SimulatedBoard.ew_check]:
            player_pieces, opponent_pieces, empty = 0, 0, 0
            if check == SimulatedBoard.ns_check:
                dir1, dir2 = 'n', 's'
            else:
                dir1, dir2 = 'e', 'w'

            for node in check:
                node1 = node
                node2 = SimulatedBoard.neighbors[node][dir1]
                node3 = SimulatedBoard.neighbors[node][dir2]
                player1, player2, player3 = self.board[node1], self.board[node2], self.board[node3]
                for k in [player1, player2, player3]:
                    if k == curr_player:
                        player_pieces += 1
                    elif k == self.get_opponent(curr_player):
                        opponent_pieces += 1
                    else:
                        empty += 1
                
            if player_pieces == 3:
				player_mill_cnt += 1
			elif player_pieces == 2 and empty == 1 
				player_part_mill_cnt += 1
            elif player_pieces == 1 and empty == 2 
                score += 1
            elif opponent_pieces == 3 
                opponent_mill_cnt += 1
            elif opponent_pieces == 2 and empty == 1 
                opponent_part_mill_cnt += 1
            elif opponent_pieces == 1 and empty == 2 
                score += -1
			
		for node, player in self.board.items():
            sub_score = 0
            if node in ['d2', 'd6', 'b4', 'f4']:
                sub_score = 2
            elif node in ['a4', 'c4', 'd1', 'd3', 'd5', 'd7', 'e4', 'g4']:
                sub_score = 1
            
            if player = curr_player:
                score += sub_score
            else:
                score = -sub_score


        

    

                    

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

