import pygame
import sys
import numpy as np
import random
import json
import datetime
import os
import time

# --- 定数定義 ---
PANEL_WIDTH = 280
BOARD_WIDTH = 720
SCREEN_WIDTH = BOARD_WIDTH + PANEL_WIDTH * 2
SCREEN_HEIGHT = 800
BOARD_SIZE = 9
CELL_SIZE = 80
BOARD_OFFSET_X = PANEL_WIDTH
BOARD_OFFSET_Y = 40
# 色
GRID_COLOR = (100, 100, 100); BLACK = (0, 0, 0); WHITE = (255, 255, 255)
P1_COLOR = (0, 100, 255); P2_COLOR = (255, 50, 50)
P1_PANEL_BG = (20, 20, 60); P2_PANEL_BG = (60, 20, 20)
STONE_COLOR = (128, 128, 128); RECOVERY_TILE_COLOR = (64, 224, 208)
BOMB_TILE_COLOR = (255, 128, 0); DRILL_COLOR = (220, 20, 60)
ICE_TILE_COLOR = (173, 216, 230)
# ハイライト色
MOVE_HIGHLIGHT_COLOR = (255, 255, 0, 128); FALL_HIGHLIGHT_COLOR = (255, 0, 0, 128)
PLACE_HIGHLIGHT_COLOR = (0, 255, 255, 128); FIGURE_BONUS_HIGHLIGHT_COLOR = (255, 215, 0, 200)
DRILL_TARGET_HIGHLIGHT_COLOR = (255, 0, 255, 180)
# コンボエフェクト色
COMBO_COLORS = [
    (0, 128, 255, 200), (0, 200, 128, 200), (255, 50, 50, 200), (153, 50, 204, 200)
]
RAINBOW_COLORS = [
    (255, 0, 0, 200), (255, 127, 0, 200), (255, 255, 0, 200),
    (0, 255, 0, 200), (0, 0, 255, 200), (75, 0, 130, 200), (148, 0, 211, 200)
]

# --- マーカー定義 ---
STONE_MARKER = "S"; RECOVERY_MARKER = "R"; BOMB_MARKER = "B"; ICE_MARKER = "I"; EMPTY_MARKER = " "

# --- ヘルパー関数 ---
def _manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# --- ログ管理クラス (変更なし) ---
class LogManager:
    def __init__(self, filename="game_log.json"):
        self.filename = filename
        with open(self.filename, 'w') as f:
            log_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'action': 'game_start',
                'details': {'board_size': BOARD_SIZE}
            }
            f.write(json.dumps(log_entry) + '\n')

    def log_action(self, action_type, details):
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': action_type,
            'details': details
        }
        with open(self.filename, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    @staticmethod
    def read_log(filename="game_log.json"):
        if not os.path.exists(filename):
            print(f"ログファイルが見つかりません: {filename}")
            return None
        actions = []
        with open(filename, 'r') as f:
            for line in f:
                actions.append(json.loads(line))
        return actions

# --- リプレイ管理クラス (変更なし) ---
class ReplayManager:
    def __init__(self, log):
        self.log = log
        self.index = 0
        self.is_playing = False
        self.timer = 0
        self.speed = 30 # 0.5秒

    def update(self):
        if self.is_playing:
            self.timer -= 1
            if self.timer <= 0:
                self._advance_step()
                self.timer = self.speed

    def _advance_step(self):
        if self.index < len(self.log) - 1:
            self.index += 1
        else:
            self.is_playing = False

    def step_forward(self):
        self.is_playing = False
        self._advance_step()

    def step_backward(self):
        self.is_playing = False
        if self.index > 0:
            self.index -= 1

    def seek_next_turn(self):
        self.is_playing = False
        for i in range(self.index + 1, len(self.log)):
            if self.log[i]['action'] == 'turn_end':
                self.index = i
                return
        self.index = len(self.log) - 1

    def seek_previous_turn(self):
        self.is_playing = False
        if self.index == 0: return
        for i in range(self.index - 1, -1, -1):
            if self.log[i]['action'] == 'turn_end':
                self.index = i
                return
        self.index = 0

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.timer = 0

# --- AIプレイヤークラス (変更なし) ---
class AIPlayer:
    def __init__(self, player_num):
        self.player_num = player_num

    def choose_move(self, game_state):
        if game_state.movable_tiles:
            return random.choice(game_state.movable_tiles)
        elif game_state.fall_trigger_tiles:
            return random.choice(game_state.fall_trigger_tiles)
        return None

    def choose_placement(self, game_state):
        if game_state.placeable_tiles:
            return 'stone', random.choice(game_state.placeable_tiles)
        return None, None

# --- ゲーム状態を管理するクラス (変更なし) ---
class GameState:
    def __init__(self, size=BOARD_SIZE):
        self.board = np.full((size, size), EMPTY_MARKER, dtype=object)
        self.player_pos = {1: (size // 2, 0), 2: (size // 2, size - 1)}
        self.player_points = {1: 0, 2: 0}
        self.skill_costs = {'recovery': 100, 'bomb': 50, 'drill': 200, 'ice': 50}
        self.special_skill = {1: None, 2: None}
        self.selection_confirmed = {1: False, 2: False}
        self.current_phase = "start_screen"
        self.game_mode = None # 'pvp' or 'pva'
        self.current_turn_player = 1
        self.dice_roll = 0
        self.placement_type = 'stone'
        self.movable_tiles, self.placeable_tiles, self.fall_trigger_tiles, self.drill_target_tiles = [], [], [], []
        self.winner, self.win_reason = None, ""
        self.is_animating = False
        self.animation_queue = []
        self.replay_bonus_shapes = []

    def _setup_initial_board(self):
        p1_pos, p2_pos = self.player_pos[1], self.player_pos[2]
        p1_fountain_zone = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE // 2 - 1)]
        p1_valid_spots = [pos for pos in p1_fountain_zone if _manhattan_distance(p1_pos, pos) > 3]
        p1_fountain_pos = random.choice(p1_valid_spots); self.board[p1_fountain_pos] = RECOVERY_MARKER
        p2_fountain_zone = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE // 2 + 2, BOARD_SIZE)]
        p2_valid_spots = [pos for pos in p2_fountain_zone if _manhattan_distance(p2_pos, pos) > 3]
        p2_fountain_pos = random.choice(p2_valid_spots); self.board[p2_fountain_pos] = RECOVERY_MARKER
        dist1, dist2 = _manhattan_distance(p1_pos, p1_fountain_pos), _manhattan_distance(p2_pos, p2_fountain_pos)
        self.current_turn_player = 1 if dist1 > dist2 else 2 if dist2 > dist1 else random.choice([1, 2])
        banned = {p1_fountain_pos, p2_fountain_pos, p1_pos, p2_pos}
        for r_off in [-1, 0, 1]:
            for c_off in [-1, 0, 1]:
                banned.add((p1_pos[0] + r_off, p1_pos[1] + c_off)); banned.add((p2_pos[0] + r_off, p2_pos[1] + c_off))
        possible_spots = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if (r, c) not in banned]
        stone_positions = random.sample(possible_spots, 3)
        for pos in stone_positions: self.board[pos] = STONE_MARKER
        return {'p1_fountain': list(p1_fountain_pos), 'p2_fountain': list(p2_fountain_pos), 'stones': [list(p) for p in stone_positions], 'first_player': self.current_turn_player}

    def select_starting_skill(self, player_num, skill_type):
        if not self.selection_confirmed[player_num]:
            self.special_skill[player_num] = skill_type
            self.selection_confirmed[player_num] = True
        if all(self.selection_confirmed.values()):
            initial_layout = self._setup_initial_board()
            self.current_phase = "roll"
            return initial_layout
        return None

    def find_movable_tiles(self):
        self.movable_tiles, self.fall_trigger_tiles = [], []
        player_r, player_c = self.player_pos[self.current_turn_player]
        other_player_pos = self.player_pos[2 if self.current_turn_player == 1 else 1]
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            path_steps, step = self.dice_roll, 1
            visited_ice, current_pos, final_dest = set(), (player_r, player_c), None
            while step <= path_steps:
                next_pos = (current_pos[0] + dr, current_pos[1] + dc)
                if not (0 <= next_pos[0] < BOARD_SIZE and 0 <= next_pos[1] < BOARD_SIZE):
                    if final_dest: self.fall_trigger_tiles.append(final_dest)
                    break
                if self.board[next_pos] == STONE_MARKER or next_pos == other_player_pos:
                    if final_dest: self.movable_tiles.append(final_dest)
                    break
                final_dest, current_pos = next_pos, next_pos
                if self.board[next_pos] == ICE_MARKER and next_pos not in visited_ice:
                    path_steps += 1; visited_ice.add(next_pos)
                step += 1
            else:
                if final_dest: self.movable_tiles.append(final_dest)
        self.movable_tiles, self.fall_trigger_tiles = list(set(self.movable_tiles)), list(set(self.fall_trigger_tiles))
        if not self.movable_tiles and not self.fall_trigger_tiles:
            self.game_over(winner=2 if self.current_turn_player == 1 else 1, reason="is blocked and cannot move!")

    def move_player(self, new_r, new_c):
        dest_type = self.board[new_r, new_c]
        if dest_type == BOMB_MARKER:
            self.game_over(winner=2 if self.current_turn_player == 1 else 1, reason="stepped on a bomb!")
            return
        self.player_pos[self.current_turn_player] = (new_r, new_c)
        if dest_type == RECOVERY_MARKER: self.player_points[self.current_turn_player] += 20
        self.current_phase = "place"; self.placement_type = 'stone'
        self.clear_highlights(); self.find_placeable_tiles()

    def set_placement_type(self, p_type):
        cost = self.skill_costs.get(p_type)
        if cost is not None and self.player_points[self.current_turn_player] < cost: return
        self.placement_type = p_type
        if p_type == 'drill':
            self.current_phase = 'drill_target'; self.find_drill_target_tiles()
        else:
            self.current_phase = 'place'; self.find_placeable_tiles()

    def find_placeable_tiles(self):
        self.placeable_tiles, self.drill_target_tiles = [], []
        player_r, player_c = self.player_pos[self.current_turn_player]
        other_player_pos = self.player_pos[2 if self.current_turn_player == 1 else 1]
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            r, c = player_r + dr, player_c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and (r, c) != other_player_pos:
                if self.placement_type == 'stone':
                    if self.board[r, c] != STONE_MARKER: self.placeable_tiles.append((r, c))
                elif self.placement_type in ['recovery', 'bomb', 'ice']:
                    if self.board[r, c] == EMPTY_MARKER: self.placeable_tiles.append((r, c))
        if not self.placeable_tiles and self.winner is None:
            self.game_over(winner=2 if self.current_turn_player == 1 else 1, reason="has no place to put an object!")

    def place_object(self, r, c, log_manager=None):
        if self.placement_type == 'stone':
            self.board[r, c] = STONE_MARKER
            found_shapes = self.check_figure_bonus(r, c)
            if found_shapes:
                total_points = len(found_shapes) * 10
                self.player_points[self.current_turn_player] += total_points
                if log_manager:
                    log_shapes = [[list(coord) for coord in shape] for shape in found_shapes]
                    log_manager.log_action('figure_bonus', {'player': self.current_turn_player, 'shapes': log_shapes})
                for i, shape_coords in enumerate(found_shapes):
                    combo_num = i + 1
                    is_rainbow = combo_num >= 4
                    color = None if is_rainbow else COMBO_COLORS[combo_num - 1]
                    animation = {'coords': list(shape_coords), 'points': 10, 'color': color, 'is_rainbow': is_rainbow, 'timer': 60}
                    self.animation_queue.append(animation)
                self.is_animating = True
            else:
                self.end_turn(log_manager)
        else:
            self.player_points[self.current_turn_player] -= self.skill_costs[self.placement_type]
            marker_map = {'recovery': RECOVERY_MARKER, 'bomb': BOMB_MARKER, 'ice': ICE_MARKER}
            self.board[r, c] = marker_map[self.placement_type]
            self.end_turn(log_manager)

    def _is_shape_complete(self, tl_r, tl_c, shape_coords):
        coords = []
        for dr, dc in shape_coords:
            r, c = tl_r + dr, tl_c + dc
            if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r, c] == STONE_MARKER): return None
            coords.append((r, c))
        return coords

    def check_figure_bonus(self, r, c):
        shapes = [
            {(0,0), (1,0), (2,0), (0,1), (2,1)}, {(0,0), (2,0), (0,1), (1,1), (2,1)},
            {(0,0), (1,0), (0,1), (0,2), (1,2)}, {(0,0), (0,2), (1,0), (1,1), (1,2)}
        ]
        found_shapes = set()
        for shape in shapes:
            for dr, dc in shape:
                tl_r, tl_c = r - dr, c - dc
                completed_coords = self._is_shape_complete(tl_r, tl_c, shape)
                if completed_coords: found_shapes.add(frozenset(completed_coords))
        return list(found_shapes) if found_shapes else None

    def find_drill_target_tiles(self):
        self.drill_target_tiles, self.placeable_tiles = [], []
        player_r, player_c = self.player_pos[self.current_turn_player]
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            r, c = player_r + dr, player_c + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r, c] == STONE_MARKER:
                self.drill_target_tiles.append((r, c))
        if not self.drill_target_tiles: print("破壊できる石がありません")

    def use_drill(self, r, c, log_manager=None):
        self.player_points[self.current_turn_player] -= self.skill_costs['drill']
        self.board[r, c] = EMPTY_MARKER
        self.end_turn(log_manager)

    def end_turn(self, log_manager=None):
        old_player = self.current_turn_player
        self.current_turn_player = 2 if self.current_turn_player == 1 else 1
        self.player_points[self.current_turn_player] += 10
        self.current_phase = "roll"; self.dice_roll = 0
        self.clear_highlights()
        if log_manager:
            log_manager.log_action('turn_end', {'player': old_player})

    def clear_highlights(self):
        self.movable_tiles, self.placeable_tiles, self.fall_trigger_tiles, self.drill_target_tiles = [], [], [], []

    def game_over(self, winner, reason):
        if self.winner is None:
            loser = 1 if winner == 2 else 2
            self.winner = winner; self.win_reason = f"Player {loser} {reason}"; self.current_phase = "game_over"

    def apply_log_action(self, log_entry):
        self.replay_bonus_shapes = []
        action = log_entry['action']
        details = log_entry['details']
        
        if action == 'skill_select':
            self.special_skill[details['player']] = details['skill']
            self.selection_confirmed[details['player']] = True
        elif action == 'initial_setup':
            self.board.fill(EMPTY_MARKER)
            self.board[tuple(details['p1_fountain'])] = RECOVERY_MARKER
            self.board[tuple(details['p2_fountain'])] = RECOVERY_MARKER
            for pos in details['stones']:
                self.board[tuple(pos)] = STONE_MARKER
            self.current_turn_player = details['first_player']
        elif action == 'dice_roll':
            self.dice_roll = details['roll']
        elif action == 'move':
            player = details['player']
            new_r, new_c = details['to']
            dest_type = self.board[new_r, new_c]
            if dest_type == RECOVERY_MARKER:
                self.player_points[player] += 20
            self.player_pos[player] = (new_r, new_c)
        elif action == 'place':
            player = details['player']
            p_type = details['type']
            r, c = details['pos']
            if p_type == 'stone':
                self.board[r, c] = STONE_MARKER
            else:
                self.player_points[player] -= self.skill_costs[p_type]
                marker_map = {'recovery': RECOVERY_MARKER, 'bomb': BOMB_MARKER, 'ice': ICE_MARKER}
                self.board[r, c] = marker_map[p_type]
        elif action == 'use_drill':
            player = details['player']
            r, c = details['target']
            self.player_points[player] -= self.skill_costs['drill']
            self.board[r, c] = EMPTY_MARKER
        elif action == 'turn_end':
            next_player = 2 if details['player'] == 1 else 1
            self.current_turn_player = next_player
            self.player_points[next_player] += 10
            self.dice_roll = 0
        elif action == 'game_over':
            self.winner = details['winner']
            self.win_reason = details['reason']
        elif action == 'figure_bonus':
            player = details['player']
            shapes = details['shapes']
            total_points = len(shapes) * 10
            self.player_points[player] += total_points
            for i, shape_coords_list in enumerate(shapes):
                combo_num = i + 1
                is_rainbow = combo_num >= 4
                color = None if is_rainbow else COMBO_COLORS[combo_num - 1]
                shape_coords_tuples = [tuple(coord) for coord in shape_coords_list]
                animation = {'coords': shape_coords_tuples, 'points': 10, 'color': color, 'is_rainbow': is_rainbow, 'timer': 60}
                self.animation_queue.append(animation)
            self.is_animating = True

# --- 描画関連の関数 ---
def draw_board(screen, game_state, icon_images, fonts):
    move_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); move_highlight_surf.fill(MOVE_HIGHLIGHT_COLOR)
    fall_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); fall_highlight_surf.fill(FALL_HIGHLIGHT_COLOR)
    place_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); place_highlight_surf.fill(PLACE_HIGHLIGHT_COLOR)
    drill_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA); drill_highlight_surf.fill(DRILL_TARGET_HIGHLIGHT_COLOR)

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = pygame.Rect(c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            tile_type = game_state.board[r, c]
            icon_to_draw = None
            if tile_type == RECOVERY_MARKER:
                pygame.draw.rect(screen, RECOVERY_TILE_COLOR, rect); icon_to_draw = icon_images['recovery']
            elif tile_type == BOMB_MARKER:
                pygame.draw.rect(screen, BOMB_TILE_COLOR, rect); icon_to_draw = icon_images['bomb']
            elif tile_type == STONE_MARKER:
                icon_to_draw = icon_images['stone']
            elif tile_type == ICE_MARKER:
                pygame.draw.rect(screen, ICE_TILE_COLOR, rect); icon_to_draw = icon_images['ice']
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)
            if icon_to_draw:
                screen.blit(icon_to_draw, icon_to_draw.get_rect(center=rect.center))

    for r, c in game_state.movable_tiles:
         screen.blit(move_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))
    for r, c in game_state.fall_trigger_tiles:
        screen.blit(fall_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))
    if game_state.current_phase == 'place':
        for r, c in game_state.placeable_tiles:
            screen.blit(place_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))
    if game_state.current_phase == 'drill_target':
        for r, c in game_state.drill_target_tiles:
            screen.blit(drill_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))
    
    if game_state.is_animating and game_state.animation_queue:
        current_anim = game_state.animation_queue[0]
        if (current_anim['timer'] // 10) % 2 == 0:
            bonus_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            color = current_anim['color']
            if current_anim['is_rainbow']:
                rainbow_index = (pygame.time.get_ticks() // 100) % len(RAINBOW_COLORS)
                color = RAINBOW_COLORS[rainbow_index]
            bonus_highlight_surf.fill(color)
            for r, c in current_anim['coords']:
                screen.blit(bonus_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))
            
            points_text = f"+{current_anim['points']} pt"
            points_surf = fonts['large'].render(points_text, True, WHITE)
            avg_r = sum(r for r, c in current_anim['coords']) / len(current_anim['coords'])
            avg_c = sum(c for r, c in current_anim['coords']) / len(current_anim['coords'])
            text_rect = points_surf.get_rect(center=(avg_c * CELL_SIZE + BOARD_OFFSET_X + CELL_SIZE/2, avg_r * CELL_SIZE + BOARD_OFFSET_Y + CELL_SIZE/2))
            screen.blit(points_surf, text_rect)
    
    if game_state.replay_bonus_shapes:
        for shape_info in game_state.replay_bonus_shapes:
            color = shape_info['color']
            coords = shape_info['coords']
            bonus_highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            bonus_highlight_surf.fill(color)
            for r, c in coords:
                screen.blit(bonus_highlight_surf, (c * CELL_SIZE + BOARD_OFFSET_X, r * CELL_SIZE + BOARD_OFFSET_Y))

    for player_num, pos in game_state.player_pos.items():
        r, c = pos
        center = (c * CELL_SIZE + BOARD_OFFSET_X + CELL_SIZE // 2, r * CELL_SIZE + BOARD_OFFSET_Y + CELL_SIZE // 2)
        color = P1_COLOR if player_num == 1 else P2_COLOR
        pygame.draw.circle(screen, color, center, CELL_SIZE // 2 - 10)

def draw_player_panels(screen, game_state, fonts, button_rects):
    p1_panel_rect = pygame.Rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    p2_panel_rect = pygame.Rect(SCREEN_WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, P1_PANEL_BG, p1_panel_rect)
    pygame.draw.rect(screen, P2_PANEL_BG, p2_panel_rect)

    for player_num in [1, 2]:
        panel_rect = p1_panel_rect if player_num == 1 else p2_panel_rect
        text_color = WHITE
        
        if game_state.current_phase == "skill_selection":
            if not game_state.selection_confirmed[player_num]:
                title_surf = fonts['large'].render(f"Player {player_num}", True, text_color)
                screen.blit(title_surf, (panel_rect.x + 20, 50))
                subtitle_surf = fonts['medium'].render("Choose Special Skill", True, text_color)
                screen.blit(subtitle_surf, (panel_rect.x + 20, 120))
                
                btn1 = button_rects['start_skill_1'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, ICE_TILE_COLOR, btn1); pygame.draw.rect(screen, WHITE, btn1, 3)
                title1 = fonts['medium'].render("Ice Skill", True, BLACK); desc1 = fonts['small'].render("Place ice tiles", True, BLACK)
                screen.blit(title1, (btn1.x + 20, btn1.y + 20)); screen.blit(desc1, (btn1.x + 20, btn1.y + 60))
            else:
                title_surf = fonts['large'].render(f"Player {player_num}", True, text_color)
                screen.blit(title_surf, (panel_rect.x + 20, 50))
                ready_surf = fonts['large'].render("Ready!", True, (0, 255, 0))
                screen.blit(ready_surf, (panel_rect.x + 20, 250))
            continue

        is_turn = game_state.current_turn_player == player_num
        name_surf = fonts['large'].render(f"Player {player_num}{' (Turn)' if is_turn and game_state.winner is None else ''}", True, text_color)
        screen.blit(name_surf, (panel_rect.x + 20, 50))
        
        points_surf = fonts['medium'].render(f"Points: {game_state.player_points[player_num]}", True, text_color)
        screen.blit(points_surf, (panel_rect.x + 20, 120))
        
        if is_turn and game_state.dice_roll > 0:
            dice_surf = fonts['medium'].render(f"Dice Roll: {game_state.dice_roll}", True, (255, 255, 0))
            screen.blit(dice_surf, (panel_rect.x + 20, 240))

        if is_turn:
            if game_state.current_phase == 'roll':
                btn = button_rects['roll'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, (0, 200, 0), btn)
                text = fonts['medium'].render("Roll Dice", True, WHITE)
                screen.blit(text, text.get_rect(center=btn.center))
            
            elif game_state.current_phase in ['place', 'drill_target']:
                btn_stone = button_rects['place_stone'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, STONE_COLOR, btn_stone)
                if game_state.placement_type == 'stone' and game_state.current_phase == 'place': pygame.draw.rect(screen, WHITE, btn_stone, 4)
                text_stone = fonts['medium'].render("Place Stone", True, WHITE)
                screen.blit(text_stone, text_stone.get_rect(center=btn_stone.center))
                
                btn_rec = button_rects['place_recovery'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, RECOVERY_TILE_COLOR, btn_rec)
                if game_state.placement_type == 'recovery': pygame.draw.rect(screen, WHITE, btn_rec, 4)
                text_rec = fonts['small'].render(f"Recovery ({game_state.skill_costs['recovery']}pt)", True, BLACK)
                screen.blit(text_rec, text_rec.get_rect(center=btn_rec.center))

                btn_bomb = button_rects['place_bomb'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, BOMB_TILE_COLOR, btn_bomb)
                if game_state.placement_type == 'bomb': pygame.draw.rect(screen, WHITE, btn_bomb, 4)
                text_bomb = fonts['small'].render(f"Bomb ({game_state.skill_costs['bomb']}pt)", True, BLACK)
                screen.blit(text_bomb, text_bomb.get_rect(center=btn_bomb.center))

                btn_drill = button_rects['use_drill'].move(panel_rect.x, 0)
                pygame.draw.rect(screen, DRILL_COLOR, btn_drill)
                if game_state.current_phase == 'drill_target': pygame.draw.rect(screen, WHITE, btn_drill, 4)
                text_drill = fonts['small'].render(f"Drill ({game_state.skill_costs['drill']}pt)", True, WHITE)
                screen.blit(text_drill, text_drill.get_rect(center=btn_drill.center))
                
                if game_state.special_skill[player_num] == 'ice_skill':
                    btn_ice = button_rects['place_ice'].move(panel_rect.x, 0)
                    pygame.draw.rect(screen, ICE_TILE_COLOR, btn_ice)
                    if game_state.placement_type == 'ice': pygame.draw.rect(screen, WHITE, btn_ice, 4)
                    text_ice = fonts['small'].render(f"Ice ({game_state.skill_costs['ice']}pt)", True, BLACK)
                    screen.blit(text_ice, text_ice.get_rect(center=btn_ice.center))

def draw_start_screen(screen, fonts, button_rects):
    screen.fill(BLACK)
    title_surf = fonts['large'].render("Turn-Based Strategy Game", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(centerx=SCREEN_WIDTH/2, y=200))

    pvp_btn = button_rects['start_pvp']
    pygame.draw.rect(screen, (0, 150, 0), pvp_btn)
    pygame.draw.rect(screen, WHITE, pvp_btn, 3)
    pvp_text = fonts['medium'].render("Player vs Player", True, WHITE)
    screen.blit(pvp_text, pvp_text.get_rect(center=pvp_btn.center))

    pva_btn = button_rects['start_pva']
    pygame.draw.rect(screen, (150, 150, 0), pva_btn)
    pygame.draw.rect(screen, WHITE, pva_btn, 3)
    pva_text = fonts['medium'].render("Player vs AI", True, WHITE)
    screen.blit(pva_text, pva_text.get_rect(center=pva_btn.center))

    replay_btn = button_rects['view_replay']
    pygame.draw.rect(screen, (0, 0, 150), replay_btn)
    pygame.draw.rect(screen, WHITE, replay_btn, 3)
    replay_text = fonts['medium'].render("View Replay", True, WHITE)
    screen.blit(replay_text, replay_text.get_rect(center=replay_btn.center))

def draw_game_over_screen(screen, game_state, fonts, button_rects):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    win_surf = fonts['large'].render(f"Player {game_state.winner} Wins!", True, (255, 215, 0))
    screen.blit(win_surf, win_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120)))
    reason_surf = fonts['medium'].render(game_state.win_reason, True, WHITE)
    screen.blit(reason_surf, reason_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60)))
    
    restart_btn = button_rects['restart']
    pygame.draw.rect(screen, (0, 150, 0), restart_btn)
    pygame.draw.rect(screen, WHITE, restart_btn, 3)
    restart_text = fonts['medium'].render("Main Menu", True, WHITE)
    screen.blit(restart_text, restart_text.get_rect(center=restart_btn.center))
    
    replay_btn = button_rects['view_replay_game_over']
    pygame.draw.rect(screen, (0, 0, 150), replay_btn)
    pygame.draw.rect(screen, WHITE, replay_btn, 3)
    replay_text = fonts['medium'].render("View Replay", True, WHITE)
    screen.blit(replay_text, replay_text.get_rect(center=replay_btn.center))

def draw_replay_ui(screen, fonts, replay_manager, button_rects, icon_images):
    ui_area = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
    pygame.draw.rect(screen, (30, 30, 30), ui_area)
    
    play_pause_btn = button_rects['replay_play_pause']
    icon = icon_images['replay_pause'] if replay_manager.is_playing else icon_images['replay_play']
    pygame.draw.rect(screen, (0, 150, 0), play_pause_btn)
    screen.blit(icon, icon.get_rect(center=play_pause_btn.center))

    prev_action_btn = button_rects['replay_prev_action']
    pygame.draw.rect(screen, (80, 80, 80), prev_action_btn)
    screen.blit(icon_images['replay_prev_action'], icon_images['replay_prev_action'].get_rect(center=prev_action_btn.center))
    
    next_action_btn = button_rects['replay_next_action']
    pygame.draw.rect(screen, (80, 80, 80), next_action_btn)
    screen.blit(icon_images['replay_next_action'], icon_images['replay_next_action'].get_rect(center=next_action_btn.center))
    
    prev_turn_btn = button_rects['replay_prev_turn']
    pygame.draw.rect(screen, (80, 80, 80), prev_turn_btn)
    screen.blit(icon_images['replay_prev_turn'], icon_images['replay_prev_turn'].get_rect(center=prev_turn_btn.center))
    
    next_turn_btn = button_rects['replay_next_turn']
    pygame.draw.rect(screen, (80, 80, 80), next_turn_btn)
    screen.blit(icon_images['replay_next_turn'], icon_images['replay_next_turn'].get_rect(center=next_turn_btn.center))

    main_menu_btn = button_rects['replay_main_menu']
    pygame.draw.rect(screen, (150, 0, 0), main_menu_btn)
    text_surf = fonts['medium'].render("Main Menu", True, WHITE)
    screen.blit(text_surf, text_surf.get_rect(center=main_menu_btn.center))
    
    progress = f"Action: {replay_manager.index + 1} / {len(replay_manager.log)}"
    progress_surf = fonts['medium'].render(progress, True, WHITE)
    screen.blit(progress_surf, (20, 20))

# --- メイン処理 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2人対戦ターン制ストラテジーゲーム")
    clock = pygame.time.Clock()
    
    fonts = { 'small': pygame.font.Font(None, 32), 'medium': pygame.font.Font(None, 40), 'large': pygame.font.Font(None, 50) }
    
    try:
        icon_size = int(CELL_SIZE * 0.8)
        replay_icon_size = 40
        icon_images = {
            'stone': pygame.transform.scale(pygame.image.load('stone.png').convert_alpha(), (icon_size, icon_size)),
            'recovery': pygame.transform.scale(pygame.image.load('recovery.png').convert_alpha(), (icon_size, icon_size)),
            'bomb': pygame.transform.scale(pygame.image.load('bomb.png').convert_alpha(), (icon_size, icon_size)),
            'ice': pygame.transform.scale(pygame.image.load('ice.png').convert_alpha(), (icon_size, icon_size)),
            'replay_play': pygame.transform.scale(pygame.image.load('replay_play.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
            'replay_pause': pygame.transform.scale(pygame.image.load('replay_pause.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
            'replay_prev_action': pygame.transform.scale(pygame.image.load('replay_prev_action.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
            'replay_next_action': pygame.transform.scale(pygame.image.load('replay_next_action.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
            'replay_prev_turn': pygame.transform.scale(pygame.image.load('replay_prev_turn.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
            'replay_next_turn': pygame.transform.scale(pygame.image.load('replay_next_turn.png').convert_alpha(), (replay_icon_size, replay_icon_size)),
        }
    except pygame.error as e:
        print(f"画像の読み込みに失敗しました: {e}"); pygame.quit(); sys.exit()

    log_manager = None
    game_state = GameState()
    replay_manager = None
    ai_player = AIPlayer(player_num=2)
    ai_turn_timer = 0
    
    button_rects = {
        'start_pvp': pygame.Rect(0, 0, 300, 80),
        'start_pva': pygame.Rect(0, 0, 300, 80),
        'view_replay': pygame.Rect(0, 0, 300, 80),
        'start_skill_1': pygame.Rect(20, 250, PANEL_WIDTH - 40, 120),
        'roll': pygame.Rect(40, 300, 200, 60),
        'place_stone': pygame.Rect(40, 300, 200, 50),
        'place_recovery': pygame.Rect(40, 360, 200, 50),
        'place_bomb': pygame.Rect(40, 420, 200, 50),
        'use_drill': pygame.Rect(40, 480, 200, 50),
        'place_ice': pygame.Rect(40, 540, 200, 50),
        'restart': pygame.Rect(0, 0, 220, 70),
        'view_replay_game_over': pygame.Rect(0, 0, 220, 70),
        'replay_prev_turn': pygame.Rect(PANEL_WIDTH + 20, SCREEN_HEIGHT - 55, 50, 50),
        'replay_prev_action': pygame.Rect(PANEL_WIDTH + 80, SCREEN_HEIGHT - 55, 50, 50),
        'replay_play_pause': pygame.Rect(PANEL_WIDTH + 140, SCREEN_HEIGHT - 55, 80, 50),
        'replay_next_action': pygame.Rect(PANEL_WIDTH + 230, SCREEN_HEIGHT - 55, 50, 50),
        'replay_next_turn': pygame.Rect(PANEL_WIDTH + 290, SCREEN_HEIGHT - 55, 50, 50),
        'replay_main_menu': pygame.Rect(SCREEN_WIDTH - PANEL_WIDTH - 170, SCREEN_HEIGHT - 55, 150, 50),
    }
    button_rects['start_pvp'].center = (SCREEN_WIDTH / 2, 350)
    button_rects['start_pva'].center = (SCREEN_WIDTH / 2, 470)
    button_rects['view_replay'].center = (SCREEN_WIDTH / 2, 590)
    button_rects['restart'].center = (SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 + 50)
    button_rects['view_replay_game_over'].center = (SCREEN_WIDTH / 2 + 130, SCREEN_HEIGHT / 2 + 50)

    while True:
        is_ai_turn = game_state.game_mode == 'pva' and game_state.current_turn_player == 2 and game_state.winner is None

        active_game_state = game_state
        if game_state.current_phase in ["replay", "replay_end"]:
            if replay_manager:
                if not active_game_state.is_animating:
                    replay_manager.update()
                
                temp_replay_state = GameState()
                for i in range(replay_manager.index + 1):
                    temp_replay_state.apply_log_action(replay_manager.log[i])
                active_game_state = temp_replay_state
                
                if replay_manager.index >= len(replay_manager.log) - 1:
                    active_game_state.current_phase = "replay_end"
                else:
                    active_game_state.current_phase = "replay"
        
        if active_game_state.is_animating:
            if active_game_state.animation_queue:
                current_anim = active_game_state.animation_queue[0]
                current_anim['timer'] -= 1
                if current_anim['timer'] <= 0:
                    active_game_state.animation_queue.pop(0)
            else:
                active_game_state.is_animating = False
                if game_state.current_phase != "replay":
                    game_state.end_turn(log_manager)

        if is_ai_turn and not game_state.is_animating:
            ai_turn_timer -= 1
            if ai_turn_timer <= 0:
                if game_state.current_phase == 'roll':
                    game_state.dice_roll = random.randint(1, 3)
                    if log_manager: log_manager.log_action('dice_roll', {'player': 2, 'roll': game_state.dice_roll})
                    game_state.find_movable_tiles()
                    game_state.current_phase = "move"
                    ai_turn_timer = 60
                
                elif game_state.current_phase == 'move':
                    move_pos = ai_player.choose_move(game_state)
                    if move_pos:
                        if move_pos in game_state.fall_trigger_tiles:
                            if log_manager: log_manager.log_action('fall', {'player': 2})
                            game_state.game_over(winner=1, reason="fell off the cliff!")
                        else:
                            from_pos = game_state.player_pos[2]
                            if log_manager: log_manager.log_action('move', {'player': 2, 'from': list(from_pos), 'to': list(move_pos)})
                            game_state.move_player(*move_pos)
                    ai_turn_timer = 60

                elif game_state.current_phase == 'place':
                    p_type, place_pos = ai_player.choose_placement(game_state)
                    if p_type and place_pos:
                        game_state.placement_type = p_type
                        if log_manager: log_manager.log_action('place', {'player': 2, 'type': p_type, 'pos': list(place_pos)})
                        game_state.place_object(*place_pos, log_manager)
                    else:
                        game_state.end_turn(log_manager)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # ★★★ ここからが修正箇所 ★★★
            if game_state.is_animating or (is_ai_turn and game_state.winner is None):
                continue
            # ★★★ ここまでが修正箇所 ★★★

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if game_state.current_phase == "start_screen":
                    if button_rects['start_pvp'].collidepoint(pos):
                        log_manager = LogManager()
                        game_state = GameState()
                        game_state.game_mode = 'pvp'
                        game_state.current_phase = "skill_selection"
                    elif button_rects['start_pva'].collidepoint(pos):
                        log_manager = LogManager()
                        game_state = GameState()
                        game_state.game_mode = 'pva'
                        game_state.current_phase = "skill_selection"
                    elif button_rects['view_replay'].collidepoint(pos):
                        log = LogManager.read_log()
                        if log:
                            replay_manager = ReplayManager(log)
                            game_state = GameState()
                            game_state.current_phase = "replay"
                
                elif game_state.current_phase == "replay":
                    if button_rects['replay_play_pause'].collidepoint(pos): replay_manager.toggle_play()
                    elif button_rects['replay_next_action'].collidepoint(pos): replay_manager.step_forward()
                    elif button_rects['replay_prev_action'].collidepoint(pos): replay_manager.step_backward()
                    elif button_rects['replay_next_turn'].collidepoint(pos): replay_manager.seek_next_turn()
                    elif button_rects['replay_prev_turn'].collidepoint(pos): replay_manager.seek_previous_turn()
                    elif button_rects['replay_main_menu'].collidepoint(pos):
                        game_state = GameState()
                        replay_manager = None

                elif game_state.current_phase == "skill_selection":
                    initial_layout = None
                    if not game_state.selection_confirmed[1]:
                        if button_rects['start_skill_1'].collidepoint(pos):
                            initial_layout = game_state.select_starting_skill(1, 'ice_skill')
                            if log_manager: log_manager.log_action('skill_select', {'player': 1, 'skill': 'ice_skill'})
                    if not game_state.selection_confirmed[2]:
                        btn1_p2 = button_rects['start_skill_1'].move(SCREEN_WIDTH - PANEL_WIDTH, 0)
                        if btn1_p2.collidepoint(pos):
                            initial_layout = game_state.select_starting_skill(2, 'ice_skill')
                            if log_manager: log_manager.log_action('skill_select', {'player': 2, 'skill': 'ice_skill'})
                    if initial_layout and log_manager:
                        log_manager.log_action('initial_setup', initial_layout)
                
                elif game_state.current_phase in ["game_over", "replay_end"]:
                    if button_rects['restart'].collidepoint(pos):
                        game_state = GameState()
                        replay_manager = None
                    elif button_rects['view_replay_game_over'].collidepoint(pos):
                        log = LogManager.read_log("game_log.json")
                        if log:
                            replay_manager = ReplayManager(log)
                            game_state = GameState()
                            game_state.current_phase = "replay"
                
                elif game_state.current_phase != "replay":
                    active_panel_offset = 0 if game_state.current_turn_player == 1 else (SCREEN_WIDTH - PANEL_WIDTH)
                    
                    if game_state.current_phase == "roll":
                        if button_rects['roll'].move(active_panel_offset, 0).collidepoint(pos):
                            game_state.dice_roll = random.randint(1, 3)
                            if log_manager: log_manager.log_action('dice_roll', {'player': game_state.current_turn_player, 'roll': game_state.dice_roll})
                            game_state.find_movable_tiles()
                            if game_state.winner is None: game_state.current_phase = "move"
                    
                    elif game_state.current_phase == "move":
                        clicked_col = (pos[0] - BOARD_OFFSET_X) // CELL_SIZE; clicked_row = (pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
                        if (clicked_row, clicked_col) in game_state.fall_trigger_tiles:
                            if log_manager: log_manager.log_action('fall', {'player': game_state.current_turn_player})
                            game_state.game_over(winner=2 if game_state.current_turn_player == 1 else 1, reason="fell off the cliff!")
                        elif (clicked_row, clicked_col) in game_state.movable_tiles:
                            from_pos = game_state.player_pos[game_state.current_turn_player]
                            if log_manager: log_manager.log_action('move', {'player': game_state.current_turn_player, 'from': list(from_pos), 'to': [clicked_row, clicked_col]})
                            game_state.move_player(clicked_row, clicked_col)
                    
                    elif game_state.current_phase in ['place', 'drill_target']:
                        btn_stone = button_rects['place_stone'].move(active_panel_offset, 0)
                        btn_rec = button_rects['place_recovery'].move(active_panel_offset, 0)
                        btn_bomb = button_rects['place_bomb'].move(active_panel_offset, 0)
                        btn_drill = button_rects['use_drill'].move(active_panel_offset, 0)
                        btn_ice = button_rects['place_ice'].move(active_panel_offset, 0)
                        
                        clicked_button = None
                        if btn_stone.collidepoint(pos): clicked_button = 'stone'
                        elif btn_rec.collidepoint(pos): clicked_button = 'recovery'
                        elif btn_bomb.collidepoint(pos): clicked_button = 'bomb'
                        elif btn_drill.collidepoint(pos): clicked_button = 'drill'
                        elif game_state.special_skill[game_state.current_turn_player] == 'ice_skill' and btn_ice.collidepoint(pos):
                            clicked_button = 'ice'
                        
                        if clicked_button:
                            game_state.set_placement_type(clicked_button)
                        
                        else:
                            clicked_col = (pos[0] - BOARD_OFFSET_X) // CELL_SIZE
                            clicked_row = (pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
                            if game_state.current_phase == 'drill_target':
                                if (clicked_row, clicked_col) in game_state.drill_target_tiles:
                                    if log_manager: log_manager.log_action('use_drill', {'player': game_state.current_turn_player, 'target': (clicked_row, clicked_col)})
                                    game_state.use_drill(clicked_row, clicked_col, log_manager)
                            elif game_state.current_phase == 'place':
                                if (0 <= clicked_col < BOARD_SIZE and 0 <= clicked_row < BOARD_SIZE) and \
                                     (clicked_row, clicked_col) in game_state.placeable_tiles:
                                    if log_manager: log_manager.log_action('place', {'player': game_state.current_turn_player, 'type': game_state.placement_type, 'pos': (clicked_row, clicked_col)})
                                    game_state.place_object(clicked_row, clicked_col, log_manager)

        screen.fill(BLACK)
        
        if game_state.current_phase == "start_screen":
            draw_start_screen(screen, fonts, button_rects)
        elif game_state.current_phase == "skill_selection":
            draw_player_panels(screen, game_state, fonts, button_rects)
            draw_board(screen, game_state, icon_images, fonts)
        elif game_state.current_phase in ["replay", "replay_end"]:
            draw_player_panels(screen, active_game_state, fonts, {})
            draw_board(screen, active_game_state, icon_images, fonts)
            draw_replay_ui(screen, fonts, replay_manager, button_rects, icon_images)
            if active_game_state.current_phase == "replay_end":
                draw_game_over_screen(screen, active_game_state, fonts, button_rects)
        elif game_state.winner is not None:
            if game_state.win_reason:
                if log_manager: log_manager.log_action('game_over', {'winner': game_state.winner, 'reason': game_state.win_reason})
                game_state.win_reason = ""
            draw_player_panels(screen, game_state, fonts, button_rects)
            draw_board(screen, game_state, icon_images, fonts)
            draw_game_over_screen(screen, game_state, fonts, button_rects)
        else:
            draw_player_panels(screen, game_state, fonts, button_rects)
            draw_board(screen, game_state, icon_images, fonts)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
