import random
from collections import defaultdict

import pygame
from pygame.sprite import Sprite

from box import Box, Obstacle


class Player(Sprite):
    """A player that can only push boxes"""
    def __init__(self, *groups, x, y, game):
        super().__init__(*groups)
        self.game = game
        self.up = pygame.image.load('img/playerU.png')
        self.up = pygame.transform.scale(self.up, [64, 64])
        self.down = pygame.image.load('img/playerD.png')
        self.down = pygame.transform.scale(self.down, [64, 64])
        self.left = pygame.image.load('img/playerL.png')
        self.left = pygame.transform.scale(self.left, [64, 64])
        self.right = pygame.image.load('img/playerR.png')
        self.right = pygame.transform.scale(self.right, [64, 64])
        self.image = self.down
        self.rect = pygame.Rect(x * 64, y * 64, 64, 64)
        self.x = x
        self.y = y

    def update(self):
        keys = pygame.key.get_pressed()
        move = None
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.image = self.right
            move = (64, 0)
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.image = self.left
            move = (-64, 0)
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            self.image = self.up
            move = (0, -64)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.image = self.down
            move = (0, 64)
        if move:
            curr = self.y, self.x
            target = self.y + move[1] // 64, self.x + move[0] // 64
            target_elem = self.game.puzzle[target]
            if not (target_elem and target_elem.obj and isinstance(target_elem.obj, Obstacle)):
                is_box = isinstance(target_elem.obj, Box)
                if not is_box or (is_box and target_elem.obj.can_move(move)):
                    curr_elem = self.game.puzzle[curr]
                    self.rect.y, self.rect.x = target[0] * 64, target[1] * 64
                    self.y, self.x = target
                    curr_elem.char = '-' if not curr_elem.ground else 'X'
                    curr_elem.obj = None
                    target_elem.char = '*' if not target_elem.ground else '%'
                    target_elem.obj = self
                    # self.game.print_puzzle()
                    return 1
        return 0
    
    def __del__(self):
        self.kill()

    

class ReversePlayer(Player):
    """A player that can only pull boxes"""
    def __init__(self, *groups, x, y, game=None, puzzle=None):
        super().__init__(*groups, x=x, y=y, game=game)
        self.puzzle = puzzle
        self.curr_state = ''
        self.states = defaultdict(int)
        self.prev_move = (0, 0)


    def print_puzzle(self, matrix=None):
        matrix = matrix if matrix is not None else self.game.puzzle
        height, width = len(matrix), len(matrix[0])
        for h in range(height):
            for w in range(width):
                if matrix[h, w]:
                    print(matrix[h, w], end=' ')
                else:
                    print('F', end=' ')
            print(' ')
        print('\n')

    def get_state(self):
        state = ''
        height, width = len(self.game.puzzle), len(self.game.puzzle[0])
        for row in range(height):
            for col in range(width):
                if self.game.puzzle[row, col]:
                    state += str(self.game.puzzle[row, col])
        return state 

    def quick_update(self, boxes_seen):
        quick_chars = {
            '*': '-',
            '%': 'X',
            '+': '*',
            '-': '*',
            'X': '%',
            '@': '-',
            '$': 'X',
        }
        moves_tuples = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        moves = random.choices(
            moves_tuples, 
            weights=[0.1 if m == self.prev_move else 1 for m in moves_tuples],
            k=1
        )
        state = self.get_state()
        for move in moves:
            self.states.add(state)
            new_y, new_x = self.y + move[0], self.x + move[1]
            target = new_y, new_x
            curr_pos = self.y, self.x
            if (0 in (new_x, new_y) or 
                new_x >= len(self.puzzle[0]) - 1 or 
                new_y >= len(self.puzzle) - 1 or
                self.puzzle[target] in '@$'):
                continue
            self.prev_move = -move[0], -move[1]
            reverse_target = self.y - move[0], self.x - move[1]
            self.puzzle[curr_pos] = quick_chars[self.puzzle[curr_pos]]
            self.puzzle[target] = quick_chars[self.puzzle[target]]
            if self.puzzle[reverse_target] in '@$':
                self.puzzle[reverse_target] = quick_chars[self.puzzle[reverse_target]]
                self.puzzle[curr_pos] = '@' if self.puzzle[curr_pos] == '-' else '$'
            self.x, self.y = target[1], target[0]
            if move == (1, 0):
                self.image = self.down
            elif move == (-1, 0):
                self.image = self.up

    def update(self, puzzle_size):
        height, width = puzzle_size
        quick_chars = {
            '*': '-',
            '%': 'X',
            '+': '*',
            '-': '*',
            'X': '%',
            '@': '-',
            '$': 'X',
        }
        moves_tuples = [(64, 0), (-64, 0), (0, -64), (0, 64)]
        moves = random.choices(
            moves_tuples, 
            weights=[0.1 if m == self.prev_move else 1 for m in moves_tuples],
            k=1
        )
        self.curr_state = self.get_state()
        for move in moves:
            self.states[self.curr_state] += 1
            curr_pos = self.y, self.x
            target = self.y + move[0] // 64, self.x + move[1] // 64
            reverse_target = self.y - move[0] // 64, self.x - move[1] // 64
            if (target[1] == self.game.pad_x or 
                target[0] == self.game.pad_y or
                target[1] >= self.game.pad_x + width - 1 or 
                target[0] >= self.game.pad_y + height - 1 or
                (self.game.puzzle[target] and self.game.puzzle[target].char in '@$')):
                self.prev_move = move
                return
            self.prev_move = -move[0], -move[1]
            self.game.puzzle[curr_pos].char = quick_chars[self.game.puzzle[curr_pos].char]
            self.game.puzzle[curr_pos].obj = None
            self.game.puzzle[target].char = quick_chars[self.game.puzzle[target].char]
            if self.game.puzzle[target].obj:
                self.game.puzzle[target].obj.kill()
            self.game.puzzle[target].obj = self
            if (c := self.game.puzzle[reverse_target].char) in '@$':
                self.game.puzzle[reverse_target].char = quick_chars[c]
                self.game.puzzle[reverse_target].obj.reverse_move(move)
            self.rect.y, self.rect.x = target[0] * 64, target[1] * 64
            self.y, self.x = target
            if move == (64, 0):
                self.image = self.down
            elif move == (-64, 0):
                self.image = self.up
            elif move == (0, 64):
                self.image = self.right
            else:
                self.image = self.left
