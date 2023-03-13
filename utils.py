from collections import defaultdict
from heapq import heappop, heappush

import numpy as np


def print_state(state, shape):
	m, n = shape
	matrix = np.array(list(state)).reshape(m, n)
	print(matrix)


def find_boxes_and_goals(state, shape):
	_, width = shape
	boxes, goals = [], []
	for pos, char in enumerate(state):
		if char == '@':
			boxes.append((pos // width, pos % width))
		elif char in 'X%':
			goals.append((pos // width, pos % width))
	return boxes, goals

def get_state(matrix):
	return matrix.tobytes().decode('utf-8').replace('\x00', '')

def is_solved(state):
	return '@' not in state


def dijkstra(state, shape, pos):
	height, width = shape
	dijk = np.array([[float('inf') for _ in range(width)] for _ in range(height)])
	dijk[pos] = 0
	moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
	heap = [(0, pos)]
	while heap:
		distance, curr_pos = heappop(heap)
		if distance > dijk[curr_pos]:
			continue
		for move in moves:
			new_x, new_y = curr_pos[0] + move[0], curr_pos[1] + move[1]
			new_pos = new_x, new_y
			if (1 <= new_x < width - 1 and 
       			1 <= new_y < height - 1 and 
				state[new_x * width + new_y] not in '+-$'):
				new_distance = distance + 1
				if new_distance < dijk[new_pos]:
					dijk[new_pos] = new_distance
					heappush(heap, (new_distance, new_pos))
	return dijk


def dijkstra_sum(state, player_pos, shape):
	height, width = shape
	boxes, goals = find_boxes_and_goals(state, shape)
	boxes_cost = player_cost = 0
	distances = defaultdict(lambda: [])
	for i in range(height):
		for j in range(width):
			if state[i * width + j] != '+':
				distances[(i, j)] = dijkstra(state, shape, (i, j))
	for box in boxes:
		boxes_cost += min(distances[box][goal] for goal in goals)
	player_cost = min(distances[player_pos][box] for box in boxes) if boxes else 0
	return boxes_cost + player_cost


def manhattan_sum(state, player_pos, shape):
	player_x, player_y = player_pos
	boxes, goals = find_boxes_and_goals(state, shape)
	boxes_cost = player_cost = 0
	for box_x, box_y in boxes:
		boxes_cost += min(abs(box_x - goal_x) + abs(box_y - goal_y) 
						  for goal_x, goal_y in goals)
	player_cost = min(abs(box_x - player_x) + abs(box_y - player_y) 
					  for box_x, box_y in boxes) if boxes else 0
	return boxes_cost + player_cost



def is_deadlock(state, shape):
	if not state:
		return False
	height, width = shape
	boxes, _ = find_boxes_and_goals(state, shape)
	for bx, by in boxes:
		box = bx * width + by
		if ((state[box - 1] == '+' and state[box - width] == '+') or
			(state[box + 1] == '+' and state[box + width] == '+')):
			return True
	box = goal = 0
	for i in range(width + 1, 2 * width - 1):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	box = goal = 0
	for i in range(width * (height - 2) + 1, width * (height - 2) + width - 1):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	box = goal = 0
	for i in range(width + 1, width * (height - 1) + 1, width):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	box = goal = 0
	for i in range(2 * width - 2, width * height - 2, width):
		if state[i] == '@':
			box += 1
		elif state[i] in 'X%':
			goal += 1
	if box > goal:
		return True
	return False

def can_move(state, shape, player_pos, move):
	new_state = list(state)
	x, y = player_pos
	_, width = shape
	move_cost = 0
	target = x + move[0], y + move[1]
	boxtarget = x + move[0] * 2, y + move[1] * 2
	curr1d = x * width + y
	target1d = target[0] * width + target[1]
	boxtarget1d = boxtarget[0] * width + boxtarget[1]
	if state[target1d] == '+':
		return None, move_cost
	elif state[target1d] in '-X':
		new_state[curr1d] = '-' if new_state[curr1d] == '*' else 'X'
		new_state[target1d] = '*' if new_state[target1d] == '-' else '%'
	elif state[target1d] in '@$':
		if state[boxtarget1d] in '+@$':
			return None, move_cost
		elif state[boxtarget1d] in '-X':
			new_state[boxtarget1d] = '@' if new_state[boxtarget1d] == '-' else '$'
			new_state[target1d] = '*' if new_state[target1d] == '@' else '%'
			new_state[curr1d] = '-' if new_state[curr1d] == '*' else 'X'
			move_cost += 1
	return ''.join(new_state), move_cost

