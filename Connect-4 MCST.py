import numpy as np
import random
import math
from colorama import Fore
import time

C_PARAM = 2
ROLLOUTS = 1
ITTERATIONS = 5_000
RUN_TIME = 3
COMPUTER_STARTS = True

print(f"Params:\tC: {C_PARAM}, rollouts: {ROLLOUTS}, itters: {ITTERATIONS}, runtime: {RUN_TIME}, computer starts: {COMPUTER_STARTS}")

class GameState:
    def __init__(self, board, terminal=False, last_slot=None, winner=0, last_player = None):
        self.board = board
        self.terminal = terminal
        self.last_slot = last_slot
        self.last_player = last_player
        self.winner = winner
    
    def copy(self):
        return GameState(
            [row[:] for row in self.board],
            self.terminal,
            self.last_slot,
            self.winner,
            self.last_player
        )
    
    def legal_moves(self):
        return [slot for slot in range(len(self.board[0])) if self.board[0][slot] == 0]
    
    def invert(self):
        new = [row[:] for row in self.board]
        for r in range(len(new)):
            for c in range(len(new[r])):
                if new[r][c] == 1:
                    new[r][c] = -1
                elif new[r][c] == -1:
                    new[r][c] = 1
        return GameState(new, self.terminal, self.last_slot, self.winner, self.last_player)

    def place_piece(self, slot, turn=1):
        self.last_slot = slot
        self.last_player = turn
        if self.board[0][slot]:
            print("error: cant go here")
        for row in range(len(self.board)-1, -1, -1):
            if self.board[row][slot] == 0:
                self.board[row][slot] = turn
                
                return self
        print(slot)
        print(turn)
        raise RuntimeError
    
  
    def rollout_policy(self, player_turn=1): #4 -> 15 sec
        for move in self.legal_moves():
            state_copy = self.copy()
            if state_copy.place_piece(move, player_turn).is_terminal():
                if state_copy.winner == player_turn:
                    return move
        for move in self.legal_moves(): 
            state_copy = self.copy()
            if state_copy.place_piece(move, -player_turn).is_terminal():
                if state_copy.winner == -player_turn:
                    return move

        return random.choice(self.legal_moves())

    def is_terminal(self, verbose=False):
        if self.last_slot is None:
            return False

        # Find the row of the last placed piece
        for r in range(len(self.board)):
            if self.board[r][self.last_slot]:
                row = r
                break

        player = self.last_player if self.last_player else 1

        if verbose:
            print(f"row: {row}, player: {player}")

        # Horizontal check
        for c in range(max(0, self.last_slot - 3), min(len(self.board[0]) - 3, self.last_slot + 1)):
            if all(self.board[row][c + i] == player for i in range(4)):
                self.winner = player
                return True

        # Vertical check
        if row <= len(self.board) - 4:
            if all(self.board[row + i][self.last_slot] == player for i in range(4)):
                self.winner = player
                return True

        # Diagonal (bottom-left to top-right)
        for i in range(-3, 1):
            r_start = row + i
            c_start = self.last_slot + i
            if 0 <= r_start <= len(self.board) - 4 and 0 <= c_start <= len(self.board[0]) - 4:
                if all(self.board[r_start + j][c_start + j] == player for j in range(4)):
                    self.winner = player
                    return True

        # Diagonal (top-left to bottom-right)
        for i in range(-3, 1):
            r_start = row - i
            c_start = self.last_slot + i
            if 3 <= r_start < len(self.board) and 0 <= c_start <= len(self.board[0]) - 4:
                if all(self.board[r_start - j][c_start + j] == player for j in range(4)):
                    self.winner = player
                    return True

        # Check for tie
        if self.legal_moves() == []:
            return True
        
        return False

    def get_winner(self):
        return self.winner
    
    
    def printState(self):
        for row in range(len(self.board)):
            print("|", end="")
            for col in range(len(self.board[row])):
                if self.board[row][col] == 1:
                    if self.last_slot == col and (row == 0 or self.board[row-1][col] == 0):
                        print(Fore.YELLOW + " 0 ", end="")
                    else:
                        print(Fore.YELLOW + " O ", end="")
                elif self.board[row][col] == -1:
                    if self.last_slot == col and (row == 0 or self.board[row-1][col] == 0):
                        print(Fore.RED + " 0 ", end="")
                    else:
                        print(Fore.RED + " O ", end="")
                else:
                    print(Fore.RESET + " · ", end="")
            print(Fore.RESET + "|", end="")
            print()
        print("--1--2--3--4--5--6--7--")
        print()



class MCTSNode:
    def __init__(self, state, turn = 1, parent = None):
        self.state = state
        self.turn = turn
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = state.legal_moves()
    
    def is_terminal(self):
        return self.state.is_terminal()
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def best_move(self):
        return max(self.children, key=lambda c: c.visits)
    
    def best_child(self, c_param=C_PARAM):#which child to choose based on exploitation vs exploration formula
        best_score = -float("inf")
        best_children = [] # if theres a tie

        for child in self.children:
            if child.visits == 0:
                score = float("inf")  # Encourage trying unvisited nodes
            else:
                exploit = child.value / child.visits
                explore = c_param * math.sqrt(math.log(self.visits) / child.visits)
                score = exploit + explore

            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)

        return random.choice(best_children)        
    
    def expand(self):
        slot = random.choice(self.untried_actions) 
        self.untried_actions.remove(slot)

        next_state = self.state.invert().place_piece(slot)
        new_node = MCTSNode(next_state, -1 * self.turn, self)
        self.children.append(new_node)
        return new_node

    def rollout(self):
        curr_state = self.state.copy()
        curr_turn = self.turn
        turns_ahead = 0
        while not curr_state.is_terminal():
            slots = curr_state.rollout_policy(curr_turn)
            curr_state = curr_state.invert().place_piece(slots)
            curr_turn *= -1
            turns_ahead += 1
        
        #return 1 - turns_ahead*0.005 if curr_turn == self.turn else -1 + turns_ahead*0.005
        if curr_state.get_winner():
            return 1 if curr_turn == self.turn else -1 
        return 0 
            
    def backpropagate(self, reward):
        self.value += reward
        self.visits += 1
        if self.parent:
            self.parent.backpropagate(-reward)


def mcts(root_state, rollouts = 1, itterations = 1_000, run_time = 0):
    root_node = MCTSNode(root_state)
    max_depth = 0
    i = 0
    start = time.time()
    next_checkpoint = 0.10  # 10%

    while i < itterations or (time.time() - start) < run_time:

        elapsed = time.time() - start

        iter_progress = min(i / itterations, 1.0)
        time_progress = min(elapsed / run_time, 1.0)

        # Checkpoint logic
        if iter_progress >= next_checkpoint and time_progress >= next_checkpoint:
            print(
            f"\r{round(next_checkpoint * 100)}% complete "
            f"(iters={i}, time={elapsed:.2f}s)",
            end="",
            flush=True
            )
            next_checkpoint += 0.10

        i += 1
        depth = 0
        curr_node = root_node

        # Selection
        while curr_node.is_fully_expanded() and not curr_node.is_terminal():
            depth += 1
            curr_node = curr_node.best_child()
        
        if depth > max_depth:
            max_depth = depth
        # Expansion
        if not curr_node.is_terminal():
            curr_node = curr_node.expand()
        

        sims = [curr_node.rollout() for _ in range(rollouts)]
        winner = np.mean(sims)

        curr_node.backpropagate(winner)
    
    print("\r100% complete".ljust(50))

    print(Fore.RESET + "Max depth: " + str(max_depth))
    print(f"Itters: {i}  |  Time took: {(time.time() - start):.2f}\n")

    sorted_children = sorted(root_node.children, key=lambda obj: obj.visits, reverse=True)
    for child in sorted_children:
        print(f"Move: {child.state.last_slot + 1}, Avg. Value: {round(float(child.value / child.visits), 3)}, Visits: {child.visits}")

    return root_node.best_move()


board = [
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0]
]
# board[5][3] = 1
# board[4][3] = -1
# board[3][3] = 1
# board[2][3] = -1

starting_state = GameState(board)

my_turn = COMPUTER_STARTS #computer turn

next_state = starting_state

while not next_state.is_terminal():
    if my_turn:
        next_state.printState()
        
        best_node = mcts(next_state, rollouts=ROLLOUTS, itterations=ITTERATIONS, run_time=RUN_TIME)
        next_state = best_node.state

    else:
        next_state.invert().printState()

        user_in = ""
        while not type(user_in) == int or not (int(user_in)-1) in next_state.legal_moves():
            user_in = input("what slot (1-7): ").strip()
            try:
                user_in = int(user_in)
            except:
                pass

        slot = int(user_in) - 1
        next_state = next_state.place_piece(slot, -1)

        if next_state.is_terminal():
            break

        if next_state:
            next_state = next_state.invert()
        else:
            raise

    my_turn = not my_turn

    
if my_turn:
    next_state.printState()
else:
    next_state.copy().invert().printState()
    

if next_state.get_winner():
    if next_state.get_winner() == -1:
        print("Player wins!")
    else:
        print("Computer wins.")
else:
    print("Tie!")
