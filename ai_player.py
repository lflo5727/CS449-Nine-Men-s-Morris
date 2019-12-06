from typing import List, Dict
from collections import deque
from enum import Enum

import logging

from board import Board, Player

log = logging.getLogger(__name__)



class Phase(Enum):
    PLACING = 1
    MOVING = 2
    FLYING = 3

class Move:
    def __init__(self, player_id, phase, src = None, dest = None, remove = None):
        self.player_id = player_id
        self.phase = phase
        self.src = src
        self.dest = dest
        self.remove = remove

    def clone(self):
        return Move(self.player_id, self.phase, src = self.src, dest = self.dest, remove = self.remove)

    def set_remove(self, node):
        self.remove = node
        return self

class SimulateGame:
    @classmethod
    def init_cls(cls):
        _fake_board = Board()
        for node in _fake_board.get_nodes():
            cls._init_board[node.name] = 0
            cls.neighbors[node.name] = {x[0]: getattr(getattr(node, x), 'name', None) for x in ['north', 'east', 'south', 'west']}

    _init_board, neighbors = {}, {}
    ns_check = ['a4', 'b4', 'c4', 'e4', 'f4', 'g4', 'd2', 'd6']
    ew_check = ['d1', 'd2', 'd3', 'd5', 'd6', 'd7', 'b4', 'f4']

    def __init__(self, p1_id, p2_id):
        if not SimulateGame._init_board:
            SimulateGame.init_cls()
        self.board = dict(SimulateGame._init_board)
        self.p1_id = p1_id
        self.p2_id = p2_id 

    def set_board_state(self, board):
        for node in board.get_nodes():
            if node.is_occupied():
                self.board[node.name] = node.piece.player.id
            else:
                self.board[node.name] = 0

    def get_opponent(self, p_id):
        return self.p2_id if p_id == self.p1_id else self.p1_id

    def do(self, move):
        if move.phase == Phase.MOVING or move.phase == Phase.FLYING: #move
            self.board[move.src] = 0

        self.board[move.dest] = move.player_id

        if move.remove:
            board[move.remove] = 0

    def undo(self, move):
        if move.phase == Phase.MOVING or move.phase == Phase.FLYING: #move
            self.board[move.src] = move.player_id
        
        self.board[move.dest] = 0

        if move.remove:
            board[move.remove] = get_opponent(move.player_id)

    def is_empty(self, node):
        return self.board[node] == 0

    def is_occupied(self, node):
        return not self.is_empty(node)

    def get_mills(self):
        mills = {
            self.p1_id: [],
            self.p2_id: []
        }

        for i in [SimulateGame.ns_check, SimulateGame.ew_check]:
            if i == SimulateGame.ns_check:
                x, y = 'n', 's'
            else:
                x, y = 'e', 'w'

            for j in i:
                a = j
                b = SimulateGame.neighbors[j][x]
                c = SimulateGame.neighbors[j][y]
                a_player, b_player, c_player = self.board[a], self.board[b], self.board[c]
                if a_player != 0 and a_player == b_player == c_player:
                    mills[a_player].extend([a,b,c])

        return mills

    def get_pieces(self):
        pieces = {
            self.p1_id: [],
            self.p2_id: []
        }

        for node, player in self.board.items():
            if player != 0:
                pieces[player].append(node)
        
        return pieces

    def evaluate(self, curr_player):
        opp_player = self.get_opponent(curr_player)
        score = 0

        for check in [SimulateGame.ns_check, SimulateGame.ew_check]:
            if check == SimulateGame.ns_check:
                dir1, dir2 = 'n', 's'
            else:
                dir1, dir2 = 'e', 'w'

            for node in check:
                player_pieces, opponent_pieces, empty = 0, 0, 0
                node1 = node
                node2 = SimulateGame.neighbors[node][dir1]
                node3 = SimulateGame.neighbors[node][dir2]
                player1, player2, player3 = self.board[node1], self.board[node2], self.board[node3]
                for k in [player1, player2, player3]:
                    if k == curr_player:
                        player_pieces += 1
                    elif k == opp_player:
                        opponent_pieces += 1
                    else:
                        empty += 1
                
            if player_pieces == 3:
                score += 100
            elif player_pieces == 2 and empty == 1:
                score += 10
            elif player_pieces == 1 and empty == 2:
                score += 1
            elif opponent_pieces == 3:
                score += -100
            elif opponent_pieces == 2 and empty == 1:
                score += -10
            elif opponent_pieces == 1 and empty == 2:
                score += -1
            elif player_pieces == 2 and opponent_pieces == 1: #may need tuning
                score += -5
            elif opponent_pieces == 2 and player_pieces == 1:
                score += 5
            
        for node, player in self.board.items():
            sub_score = 0
            if node in ['d2', 'd6', 'b4', 'f4']:
                sub_score = 2
            elif node in ['a4', 'c4', 'd1', 'd3', 'd5', 'd7', 'e4', 'g4']:
                sub_score = 1
            
            if player == curr_player:
                score += sub_score
            elif player == opp_player:
                score += -sub_score

        return score

class AI_Player(Player):
    def __init__(self, name, id, board: "Board", opponent: "Player"):
        super().__init__(name, id, board)
        self.opponent = opponent
        self.phase = Phase.PLACING
    
    def get_best_move(self):
        pass

    def alpha_beta(self):
        pass


    def generate_remove_moves(self, sim_board, move, opp, opp_mills):
        moves = []
        opp_pieces = sim_board.get_pieces()[opp]
        for rnode, rplayer in sim_board.board.items():
            if rplayer == opp and (rnode not in opp_mills or len(opp_mills) == len(opp_pieces)):
                moves.append(move.clone().set_remove(rnode))
        return moves

    def generate_moves(self, sim_board):
        moves = []
        opp = sim_board.get_opponent(self.id)
        
        if self.phase == Phase.PLACING:
            for node, player in sim_board.board.items():
                if sim_board.is_empty(node):
                    move = Move(self.id, Phase.PLACING, dest=node)
                    sim_board.do(move)
                    mills = sim_board.get_mills()
                    if node in mills[self.id]:
                        moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                    else:
                        moves.append(move)
                    sim_board.undo(move)
        elif self.phase == Phase.MOVING:
            for node, player in sim_board.board.items():
                if player == self.id:
                    for neighbor in SimulateGame.neighbors[node].values():
                        if neighbor and sim_board.is_empty(neighbor):
                            move = Move(self.id, Phase.MOVING, node, neighbor)
                            sim_board.do(move)
                            mills = sim_board.get_mills()
                            if neighbor in mills:
                                moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                            else:
                                moves.append(move)
                            sim_board.undo(move)
        elif self.phase == Phase.FLYING:
            for src_node, src_player in sim_board.board.items():
                if src_player == self.id:
                    for dest_node, dest_player in sim_board.board.items():
                        if sim_board.is_empty(dest_node):
                            move = Move(self.id, Phase.MOVING, src_node, dest_node)
                            sim_board.do(move)
                            mills = sim_board.get_mills()
                            if dest_node in mills[self.id]:
                                moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                            else:
                                moves.append(move)
                            sim_board.undo(move)

        return moves


test_board = Board()
test_human = Player("Human", 1, test_board)
test_computer = AI_Player("Computer", 2, test_board, test_human)

test_sim = SimulateGame(test_human.id, test_computer.id)
test_sim.set_board_state(test_board)
test_sim.evaluate(test_computer)
test_sim.board['a1'] = 2                         
test_sim.board['b4'] = 2
test_sim.board['a7'] = 2
test_sim.board['g7'] = 1
test_sim.board['g1'] = 1
test_sim.board['g4'] = 1
test_sim.board['c5'] = 1
test_sim.board['d5'] = 1
#test_sim.board['e5'] = 1
test_computer.phase = Phase.FLYING
test_moves = test_computer.generate_moves(test_sim)