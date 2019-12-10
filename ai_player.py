from typing import List, Dict
from enum import Enum

import logging, math, random, sys

from board import MAX_NUM_PIECES, MIN_NUM_PIECES, Board, Player, Phase

log = logging.getLogger(__name__)

MAXINT = sys.maxsize
MININT = -sys.maxsize -1

class Move:
    def __init__(self, player_id, phase, src = None, dest = None, remove = None):
        self.player_id = player_id
        self.phase = phase
        self.src = src
        self.dest = dest
        self.remove = remove
        self.score = 0

    def clone(self):
        return Move(self.player_id, self.phase, src = self.src, dest = self.dest, remove = self.remove)

    def set_remove(self, node):
        self.remove = node
        return self

    def set_score(self, score):
        self.score = score

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
    

    def __init__(self, p1_id=None, p2_id=None):
        if not SimulateGame._init_board:
            SimulateGame.init_cls()
        self.board = dict(SimulateGame._init_board)
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.player_data = {
            self.p1_id: {'num_placed': 0,
                         'num_on_board': 0
            },
            self.p2_id: {'num_placed': 0,
                         'num_on_board': 0
            },
        }

    def get_phase(self, p_id):
        if self.player_data[p_id]['num_placed'] < MAX_NUM_PIECES:
            return Phase.PLACING
        elif self.player_data[p_id]['num_on_board'] > MIN_NUM_PIECES:
            return Phase.MOVING
        else:
            return Phase.FLYING

    def set_state(self, board, player1=None, player2=None):
        for player in [player1, player2]:
            self.player_data[player.id]['num_placed'] = MAX_NUM_PIECES - len(player.pieces)
        
        for node in board.get_nodes():
            if node.is_occupied():
                p_id = node.piece.player.id
                self.board[node.name] = p_id
                self.player_data[p_id]['num_on_board'] += 1
            else:
                self.board[node.name] = 0

    def get_opponent(self, p_id):
        return self.p2_id if p_id == self.p1_id else self.p1_id

    def do(self, move):
        if move.phase == Phase.PLACING:
            self.player_data[move.player_id]['num_placed'] += 1
            self.player_data[move.player_id]['num_on_board'] += 1

        if move.phase == Phase.MOVING or move.phase == Phase.FLYING: #move
            self.board[move.src] = 0

        self.board[move.dest] = move.player_id

        if move.remove:
            opp = self.get_opponent(move.player_id)
            self.player_data[opp]['num_on_board'] += -1
            self.board[move.remove] = 0

    def undo(self, move):
        if move.phase == Phase.PLACING:
            self.player_data[move.player_id]['num_placed'] += -1
            self.player_data[move.player_id]['num_on_board'] += -1

        if move.phase == Phase.MOVING or move.phase == Phase.FLYING: #move
            self.board[move.src] = move.player_id
        
        self.board[move.dest] = 0

        if move.remove:
            opp = self.get_opponent(move.player_id)
            self.player_data[opp]['num_on_board'] += 1
            self.board[move.remove] = self.get_opponent(move.player_id)

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

    def game_over(self, p_id):
        if self.get_phase(p_id) != Phase.PLACING:
            return self.player_data[p_id]['num_on_board'] < MIN_NUM_PIECES
        else:
            return False

class AI_Player(Player):
    MAX_SCORE = 999999
    DEPTH = 3
    PRUNING = True

    def __init__(self, name, id, board: "Board", opponent: "Player"):
        super().__init__(name, id, board)
        self.opponent = opponent
        self.calls = {
            'alpha_beta': 0,
            'evaluate': 0,
            'generate_moves': 0,
            'pruned': 0
        }
    
    def get_best_move(self):
        
        phase = self.get_phase()

        sim_board = SimulateGame(p1_id = self.opponent.id, p2_id = self.id)
        sim_board.set_state(self.board, player1 = self.opponent, player2 = self)
        opp = sim_board.get_opponent(self.id)

        moves = self.generate_moves(self.id, sim_board)
        
        max_score = -AI_Player.MAX_SCORE
        scored_moves = {}
        scored_moves[max_score] = []

        for move in moves:
            sim_board.do(move)
            move.score += self.alpha_beta(opp, sim_board, AI_Player.DEPTH, MININT, MAXINT)

            if move.score > max_score:
                max_score = move.score
                
            if move.score not in scored_moves:
                scored_moves[move.score] = []
            
            scored_moves[move.score].append(move)

            sim_board.undo(move)
        if scored_moves[max_score]:
            return random.choice(scored_moves[max_score])
        else:
            return None            

    def alpha_beta(self, curr_player, sim_board, depth, alpha, beta):
        self.calls['alpha_beta'] += 1
        opp = sim_board.get_opponent(self.id)
        
        if depth == 0:
            self.calls['evaluate'] += 1
            return sim_board.evaluate(self.id)
        elif sim_board.game_over(opp):
            return AI_Player.MAX_SCORE
        elif sim_board.game_over(self.id):
            return -AI_Player.MAX_SCORE
        else:
            moves = self.generate_moves(curr_player, sim_board)
            if not moves and curr_player == self.id:
                return -AI_Player.MAX_SCORE
            elif not moves and curr_player != self.id:
                return AI_Player.MAX_SCORE

            for move in moves:
                sim_board.do(move)
                if curr_player == self.id: #  Maximizing
                    alpha = max(alpha, self.alpha_beta(opp, sim_board, depth - 1, alpha, beta))

                    if beta <= alpha and AI_Player.PRUNING:
                        self.calls['pruned'] += 1
                        sim_board.undo(move)
                        break
                else: #  Minimizing
                    beta = min(beta, self.alpha_beta(self.id, sim_board, depth - 1, alpha, beta))

                    if beta <= alpha and AI_Player.PRUNING:
                        self.calls['pruned'] += 1
                        sim_board.undo(move)
                        break
                sim_board.undo(move)

            if curr_player == self.id:
                return alpha
            else:
                return beta

    def generate_remove_moves(self, sim_board, move, opp, opp_mills):
        moves = []
        opp_pieces = sim_board.get_pieces()[opp]
        for rnode, rplayer in sim_board.board.items():
            if rplayer == opp and (rnode not in opp_mills or len(opp_mills) == len(opp_pieces)):
                moves.append(move.clone().set_remove(rnode))
        return moves

    def generate_moves(self, curr_player, sim_board):
        self.calls['generate_moves'] += 1
        moves = []
        opp = sim_board.get_opponent(curr_player)
        phase = sim_board.get_phase(curr_player)
        if phase == Phase.PLACING:
            for node, player in sim_board.board.items():
                if sim_board.is_empty(node):
                    move = Move(curr_player, Phase.PLACING, dest=node)
                    sim_board.do(move)
                    mills = sim_board.get_mills()
                    if node in mills[curr_player]:
                        moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                    else:
                        moves.append(move)
                    sim_board.undo(move)
        elif phase == Phase.MOVING:
            for node, player in sim_board.board.items():
                if player == curr_player:
                    for neighbor in SimulateGame.neighbors[node].values():
                        if neighbor and sim_board.is_empty(neighbor):
                            move = Move(curr_player, Phase.MOVING, node, neighbor)
                            sim_board.do(move)
                            mills = sim_board.get_mills()
                            if neighbor in mills[curr_player]:
                                moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                            else:
                                moves.append(move)
                            sim_board.undo(move)
        elif phase == Phase.FLYING:
            for src_node, src_player in sim_board.board.items():
                if src_player == curr_player:
                    for dest_node, dest_player in sim_board.board.items():
                        if sim_board.is_empty(dest_node):
                            move = Move(curr_player, Phase.MOVING, src_node, dest_node)
                            sim_board.do(move)
                            mills = sim_board.get_mills()
                            if dest_node in mills[curr_player]:
                                moves.extend(self.generate_remove_moves(sim_board, move, opp, mills[opp]))
                            else:
                                moves.append(move)
                            sim_board.undo(move)

        return moves
