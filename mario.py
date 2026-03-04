"""
Super Mario Bros - World 1-1 Clone
OOP Demo: Inheritance, Encapsulation, Polymorphism, Abstraction
Controls: Arrow Left/Right = di chuyen | Space/Up = nhay | R = restart
"""

import pygame
import sys

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SW, SH      = 800, 480
FPS         = 60
TILE        = 32
GRAVITY     = 0.55
MAX_FALL    = 14
MARIO_SPEED = 3.8
JUMP_FORCE  = -13.5

# Palette (NES-inspired)
SKY         = (107, 140, 255)
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
RED         = (220, 50,  50)
BROWN       = (139, 90,  43)
DARK_BROWN  = (100, 60,  20)
ORANGE      = (230, 100, 30)
YELLOW      = (255, 213, 0)
GOLD        = (255, 185, 15)
GREEN       = (60,  180, 60)
DARK_GREEN  = (30,  120, 30)
PIPE_GREEN  = (70,  190, 70)
PIPE_DARK   = (40,  140, 40)
BRICK_RED   = (195, 90,  30)
BRICK_DARK  = (150, 65,  20)
QBLOCK_YEL  = (230, 180, 20)
QBLOCK_DARK = (180, 130, 10)
GROUND_TOP  = (222, 168, 78)
GROUND_BODY = (180, 120, 40)
COIN_GOLD   = (255, 200, 0)
COIN_DARK   = (200, 150, 0)
GOOMBA_BR   = (160, 100, 40)
GOOMBA_DK   = (100, 60,  20)
FLAG_GREEN  = (50,  200, 80)
CLOUD_WHITE = (240, 240, 255)
UI_DARK     = (20,  20,  40)


# ─────────────────────────────────────────────
# WORLD 1-1 MAP (tile columns)
# G = ground, B = brick, Q = question, P = pipe,
# E = goomba spawn, C = coin, F = flag, . = empty
# Row 0 = top (sky), Row 13 = ground level (y=13*TILE)
# ─────────────────────────────────────────────
# Each entry: (col, row, type)
LEVEL_W = 212   # tiles wide

def build_level():
    tiles   = []
    enemies = []
    coins   = []
    pipes   = []
    flag_x  = 0

    # ── Ground ── (row 14 & 15, full width with gap)
    GAP_START, GAP_END = 71, 74   # gap before flag
    for col in range(LEVEL_W):
        if GAP_START <= col < GAP_END:
            continue
        tiles.append((col, 14, "G"))
        tiles.append((col, 15, "G"))

    # ── Bricks & Q-blocks row 10 ──
    for col in [17, 18, 20]:
        tiles.append((col, 10, "B"))
    tiles.append((19, 10, "Q"))  # coin inside

    for col in [22, 23, 24]:
        tiles.append((col, 10, "B"))

    for col in [78, 80, 82]:
        tiles.append((col, 10, "B"))
    tiles.append((79, 10, "Q"))
    tiles.append((81, 10, "Q"))

    for col in [91, 93, 94]:
        tiles.append((col, 10, "B"))
    tiles.append((92, 10, "Q"))

    for col in [107, 109, 110]:
        tiles.append((col, 10, "B"))
    tiles.append((108, 10, "Q"))

    # ── Q blocks lower row 12 ──
    tiles.append((19, 12, "Q"))  # mushroom (just coin here)

    # ── Staircase 1 (col 136-139) ──
    for step, cols in enumerate([
        [139], [138, 139], [137, 138, 139], [136, 137, 138, 139]
    ]):
        for c in cols:
            tiles.append((c, 14 - step, "G"))

    # ── Staircase 2 (col 141-144) ──
    for step, cols in enumerate([
        [141, 142, 143, 144], [142, 143, 144], [143, 144], [144]
    ]):
        for c in cols:
            tiles.append((c, 14 - step, "G"))

    # ── Staircase before flag (col 155-160) ──
    for step in range(1, 9):
        for r in range(step):
            tiles.append((154 + step, 14 - r, "G"))

    # ── Pipes ──
    pipe_defs = [
        (29, 2), (39, 3), (47, 4), (58, 4),
        (85, 2), (119, 2), (130, 2),
    ]
    for (pc, ph) in pipe_defs:
        pipes.append((pc, ph))

    # ── Coins ──
    coin_cols = [
        *range(30, 38), *range(42, 46),
        *range(61, 65), *range(70, 73),
        *range(90, 95), *range(100, 106),
        *range(115, 118),
    ]
    for cc in coin_cols:
        coins.append((cc, 12))

    # ── Enemies ──
    goomba_cols = [22, 38, 43, 52, 56, 63, 81, 90, 99, 114, 130, 136]
    for gc in goomba_cols:
        enemies.append((gc, 13))

    # ── Flag ──
    flag_x = 165

    return tiles, enemies, coins, pipes, flag_x


# ─────────────────────────────────────────────
# BASE CLASS
# ─────────────────────────────────────────────
class GameObject:
    def __init__(self, x, y, w, h):
        self._x = float(x)
        self._y = float(y)
        self._w = w
        self._h = h

    @property
    def rect(self):
        return pygame.Rect(int(self._x), int(self._y), self._w, self._h)

    @property
    def x(self): return self._x
    @property
    def y(self): return self._y

    def draw(self, surface, cam_x):
        raise NotImplementedError

    def update(self, *args):
        pass


# ─────────────────────────────────────────────
# TILE  (Ground / Brick / Question block)
# ─────────────────────────────────────────────
class Tile(GameObject):
    def __init__(self, col, row, kind="G"):
        super().__init__(col * TILE, row * TILE, TILE, TILE)
        self._kind   = kind
        self._active = True   # Q-block: False after hit

    @property
    def kind(self): return self._kind
    @property
    def active(self): return self._active

    def hit(self):
        if self._kind == "Q":
            self._active = False

    def draw(self, surface, cam_x):
        sx = int(self._x) - cam_x
        if sx > SW + TILE or sx < -TILE:
            return
        r = pygame.Rect(sx, int(self._y), self._w, self._h)

        if self._kind == "G":
            pygame.draw.rect(surface, GROUND_TOP,  r)
            pygame.draw.rect(surface, GROUND_BODY,
                             pygame.Rect(sx, int(self._y)+6, TILE, TILE-6))
            pygame.draw.rect(surface, DARK_BROWN, r, 1)

        elif self._kind == "B":
            pygame.draw.rect(surface, BRICK_RED, r)
            # mortar lines
            pygame.draw.line(surface, BRICK_DARK, (sx, int(self._y)+TILE//2),
                             (sx+TILE, int(self._y)+TILE//2), 1)
            pygame.draw.line(surface, BRICK_DARK, (sx+TILE//2, int(self._y)),
                             (sx+TILE//2, int(self._y)+TILE//2), 1)
            pygame.draw.line(surface, BRICK_DARK, (sx+TILE//4, int(self._y)+TILE//2),
                             (sx+TILE//4, int(self._y)+TILE), 1)
            pygame.draw.line(surface, BRICK_DARK, (sx+3*TILE//4, int(self._y)+TILE//2),
                             (sx+3*TILE//4, int(self._y)+TILE), 1)
            pygame.draw.rect(surface, BRICK_DARK, r, 1)

        elif self._kind == "Q":
            c = QBLOCK_YEL if self._active else (120, 100, 60)
            pygame.draw.rect(surface, c, r)
            pygame.draw.rect(surface, QBLOCK_DARK if self._active else (80, 70, 40), r, 2)
            if self._active:
                qx, qy = sx + TILE//2, int(self._y) + TILE//2
                font = pygame.font.SysFont("Arial", 18, bold=True)
                t = font.render("?", True, WHITE)
                surface.blit(t, t.get_rect(center=(qx, qy)))


# ─────────────────────────────────────────────
# PIPE
# ─────────────────────────────────────────────
class Pipe(GameObject):
    def __init__(self, col, height_tiles):
        h = height_tiles * TILE
        y = 14 * TILE - h
        super().__init__(col * TILE, y, TILE * 2, h)
        self._height_tiles = height_tiles

    def draw(self, surface, cam_x):
        sx = int(self._x) - cam_x
        if sx > SW + TILE*2 or sx < -TILE*2:
            return
        # body
        body = pygame.Rect(sx + 3, int(self._y) + TILE, TILE*2 - 6, self._h - TILE)
        pygame.draw.rect(surface, PIPE_GREEN, body)
        pygame.draw.rect(surface, PIPE_DARK, body, 2)
        # highlight
        hi = pygame.Rect(sx + 6, int(self._y) + TILE + 4, 6, self._h - TILE - 8)
        pygame.draw.rect(surface, (120, 230, 120), hi)
        # cap
        cap = pygame.Rect(sx, int(self._y), TILE*2, TILE)
        pygame.draw.rect(surface, PIPE_GREEN, cap)
        pygame.draw.rect(surface, PIPE_DARK, cap, 2)
        hi2 = pygame.Rect(sx + 4, int(self._y) + 4, 8, TILE - 8)
        pygame.draw.rect(surface, (120, 230, 120), hi2)


# ─────────────────────────────────────────────
# COIN
# ─────────────────────────────────────────────
class Coin(GameObject):
    def __init__(self, col, row):
        super().__init__(col*TILE + 10, row*TILE, 12, 16)
        self._collected = False
        self._anim      = 0

    @property
    def collected(self): return self._collected

    def collect(self):
        self._collected = True

    def update(self, *args):
        self._anim = (self._anim + 3) % 360

    def draw(self, surface, cam_x):
        if self._collected:
            return
        sx = int(self._x) - cam_x
        w  = max(2, int(abs(pygame.math.Vector2(1, 0).rotate(self._anim).x) * 12))
        cx = sx + 6
        cy = int(self._y) + 8
        pygame.draw.ellipse(surface, COIN_GOLD, (cx - w//2, cy - 8, w, 16))
        pygame.draw.ellipse(surface, COIN_DARK, (cx - w//2, cy - 8, w, 16), 1)


# ─────────────────────────────────────────────
# GOOMBA
# ─────────────────────────────────────────────
class Goomba(GameObject):
    def __init__(self, col, row):
        super().__init__(col*TILE, row*TILE - TILE, TILE, TILE)
        self._vx      = -1.2
        self._vy      = 0.0
        self._alive   = True
        self._dead    = False   # squished
        self._dead_timer = 0
        self._anim    = 0

    @property
    def alive(self): return self._alive
    @property
    def dead(self): return self._dead

    def squish(self):
        self._dead      = True
        self._alive     = False
        self._dead_timer = 40

    def update(self, tiles, pipes):
        if self._dead:
            self._dead_timer -= 1
            return
        if not self._alive:
            return

        self._anim = (self._anim + 1) % 30
        self._vy  += GRAVITY
        self._vy   = min(self._vy, MAX_FALL)
        self._x   += self._vx
        self._y   += self._vy

        # Collision with tiles & pipes
        grect = self.rect
        on_ground = False
        for t in tiles:
            tr = t.rect
            if grect.colliderect(tr):
                if self._vy > 0 and grect.bottom - self._vy <= tr.top + 4:
                    self._y = tr.top - self._h
                    self._vy = 0
                    on_ground = True
                elif self._vx < 0 and grect.left <= tr.right:
                    self._x = tr.right
                    self._vx = abs(self._vx)
                elif self._vx > 0 and grect.right >= tr.left:
                    self._x = tr.left - self._w
                    self._vx = -abs(self._vx)

        for p in pipes:
            pr = p.rect
            if grect.colliderect(pr):
                if self._vx < 0:
                    self._x = pr.right
                    self._vx = abs(self._vx)
                else:
                    self._x = pr.left - self._w
                    self._vx = -abs(self._vx)

        # Turn at ledge
        if on_ground:
            next_x = self._x + self._vx * 4
            ledge = True
            for t in tiles:
                if (t.rect.left <= next_x + self._w//2 <= t.rect.right
                        and t.rect.top >= int(self._y) + self._h - 4):
                    ledge = False
                    break
            if ledge:
                self._vx = -self._vx

        # Out of world
        if self._y > SH + 100:
            self._alive = False

    def draw(self, surface, cam_x):
        if not self._alive and not self._dead:
            return
        sx = int(self._x) - cam_x
        if sx > SW + TILE or sx < -TILE:
            return

        if self._dead:
            # Squished flat
            pygame.draw.ellipse(surface, GOOMBA_BR,
                                (sx+2, int(self._y)+20, TILE-4, 12))
            return

        cy = int(self._y)
        # Body
        pygame.draw.ellipse(surface, GOOMBA_BR, (sx+2, cy+10, TILE-4, TILE-10))
        # Head
        pygame.draw.ellipse(surface, GOOMBA_BR, (sx+3, cy+2, TILE-6, TILE//2+4))
        # Eyes
        pygame.draw.circle(surface, WHITE, (sx+10, cy+10), 4)
        pygame.draw.circle(surface, WHITE, (sx+TILE-10, cy+10), 4)
        pygame.draw.circle(surface, BLACK, (sx+10, cy+11), 2)
        pygame.draw.circle(surface, BLACK, (sx+TILE-10, cy+11), 2)
        # Eyebrows (angry)
        pygame.draw.line(surface, GOOMBA_DK, (sx+7, cy+6), (sx+13, cy+8), 2)
        pygame.draw.line(surface, GOOMBA_DK, (sx+TILE-7, cy+6), (sx+TILE-13, cy+8), 2)
        # Feet
        foot_off = 4 if self._anim < 15 else -4
        pygame.draw.ellipse(surface, GOOMBA_DK,
                            (sx+1, cy+TILE-8+foot_off//2, 12, 8))
        pygame.draw.ellipse(surface, GOOMBA_DK,
                            (sx+TILE-13, cy+TILE-8-foot_off//2, 12, 8))


# ─────────────────────────────────────────────
# MARIO
# ─────────────────────────────────────────────
class Mario(GameObject):
    def __init__(self, col, row):
        super().__init__(col*TILE, row*TILE - TILE*2, TILE, TILE*2)
        self._vx       = 0.0
        self._vy       = 0.0
        self._on_ground= False
        self._alive    = True
        self._face_right = True
        self._anim     = 0
        self._run_frame= 0
        self._dead_timer = 0
        self._invincible = 0   # frames after being hit (flicker)

    @property
    def alive(self): return self._alive
    @property
    def dead_done(self): return self._dead_timer < 0

    def die(self):
        if self._invincible > 0:
            return
        self._alive = False
        self._vy    = JUMP_FORCE * 0.8
        self._dead_timer = 120

    def update(self, keys, tiles, pipes, enemies, coins):
        if not self._alive:
            self._vy += GRAVITY
            self._y  += self._vy
            self._dead_timer -= 1
            return

        if self._invincible > 0:
            self._invincible -= 1

        # Horizontal
        moving = False
        if keys[pygame.K_LEFT]:
            self._vx = -MARIO_SPEED
            self._face_right = False
            moving = True
        elif keys[pygame.K_RIGHT]:
            self._vx = MARIO_SPEED
            self._face_right = True
            moving = True
        else:
            self._vx *= 0.75

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self._on_ground:
            self._vy = JUMP_FORCE
            self._on_ground = False

        # Gravity
        self._vy += GRAVITY
        self._vy  = min(self._vy, MAX_FALL)

        # Move X
        self._x += self._vx
        self._x  = max(0, self._x)
        self._resolve_x(tiles, pipes)

        # Move Y
        self._y += self._vy
        self._on_ground = False
        self._resolve_y(tiles, pipes)

        # Animation
        if moving:
            self._anim += 1
            if self._anim >= 8:
                self._anim = 0
                self._run_frame = (self._run_frame + 1) % 3
        else:
            self._run_frame = 0

        # Coin collection
        mrect = self.rect
        for coin in coins:
            if not coin.collected and mrect.colliderect(coin.rect):
                coin.collect()

        # Enemy collision
        for enemy in enemies:
            if not enemy.alive and not enemy.dead:
                continue
            if mrect.colliderect(enemy.rect):
                # Stomping from above
                if (self._vy > 0
                        and mrect.bottom - self._vy * 0.5 <= enemy.rect.top + 8):
                    enemy.squish()
                    self._vy = JUMP_FORCE * 0.5
                else:
                    self.die()

        # Fall off world
        if self._y > SH + 64:
            self._alive = False
            self._dead_timer = 0

    def _resolve_x(self, tiles, pipes):
        mr = self.rect
        for obj_list in (tiles, pipes):
            for t in obj_list:
                tr = t.rect
                if mr.colliderect(tr):
                    if self._vx > 0:
                        self._x = tr.left - self._w
                    elif self._vx < 0:
                        self._x = tr.right
                    self._vx = 0
                    mr = self.rect

    def _resolve_y(self, tiles, pipes):
        mr = self.rect
        for obj_list in (tiles, pipes):
            for t in obj_list:
                tr = t.rect
                if mr.colliderect(tr):
                    if self._vy > 0:
                        self._y = tr.top - self._h
                        self._vy = 0
                        self._on_ground = True
                        # Hit block from below? No — that's landing on top
                    elif self._vy < 0:
                        self._y = tr.bottom
                        self._vy = 0
                        # Hit Q-block from below
                        if hasattr(t, "hit"):
                            t.hit()
                    mr = self.rect

    def draw(self, surface, cam_x):
        sx = int(self._x) - cam_x
        sy = int(self._y)

        # Flicker when invincible
        if self._invincible > 0 and (self._invincible // 4) % 2 == 0:
            return

        if not self._alive:
            self._draw_dead(surface, sx, sy)
            return

        self._draw_mario(surface, sx, sy)

    def _draw_mario(self, surface, sx, sy):
        flip = not self._face_right

        # Hat
        hat_rect = pygame.Rect(sx+4, sy, TILE-8, 8)
        pygame.draw.rect(surface, RED, hat_rect)
        brim = pygame.Rect(sx+1, sy+7, TILE-2, 5)
        pygame.draw.rect(surface, RED, brim)

        # Hair / face
        pygame.draw.rect(surface, (220, 170, 100), (sx+4, sy+10, TILE-8, 10))

        # Eyes
        ex = sx+18 if self._face_right else sx+6
        pygame.draw.circle(surface, BLACK, (ex, sy+14), 2)

        # Mustache
        mx = sx+10 if self._face_right else sx+8
        pygame.draw.ellipse(surface, BROWN, (mx, sy+18, 12, 5))

        # Body (overalls)
        body = pygame.Rect(sx+4, sy+20, TILE-8, 14)
        pygame.draw.rect(surface, (50, 80, 200), body)
        # Buttons
        pygame.draw.circle(surface, YELLOW, (sx+10, sy+25), 2)
        pygame.draw.circle(surface, YELLOW, (sx+TILE-10, sy+25), 2)

        # Shirt sleeves
        pygame.draw.rect(surface, RED, (sx, sy+20, 5, 10))
        pygame.draw.rect(surface, RED, (sx+TILE-5, sy+20, 5, 10))
        # Hands
        pygame.draw.circle(surface, (220, 170, 100), (sx+3, sy+30), 4)
        pygame.draw.circle(surface, (220, 170, 100), (sx+TILE-3, sy+30), 4)

        # Legs (run animation)
        frames = [(0, 0), (4, -2), (0, 0)]
        loff, roff = frames[self._run_frame][0], frames[self._run_frame][1]
        # Left leg
        pygame.draw.rect(surface, (50, 80, 200),
                         (sx+4, sy+34+loff, 10, 10))
        pygame.draw.rect(surface, BROWN, (sx+2, sy+44+loff, 12, 6))
        # Right leg
        pygame.draw.rect(surface, (50, 80, 200),
                         (sx+TILE-14, sy+34-roff, 10, 10))
        pygame.draw.rect(surface, BROWN, (sx+TILE-14, sy+44-roff, 12, 6))

    def _draw_dead(self, surface, sx, sy):
        # Spinning / flat dead sprite
        pygame.draw.ellipse(surface, RED, (sx+2, sy+4, TILE-4, TILE//2))
        pygame.draw.rect(surface, (220, 170, 100), (sx+6, sy+8, TILE-12, 8))
        pygame.draw.ellipse(surface, BROWN, (sx+8, sy+14, 14, 5))


# ─────────────────────────────────────────────
# CLOUD (decoration)
# ─────────────────────────────────────────────
class Cloud:
    def __init__(self, x, y, scale=1.0):
        self._x = x
        self._y = y
        self._s = scale

    def draw(self, surface, cam_x):
        sx = int(self._x - cam_x * 0.3)  # parallax
        sy = self._y
        s  = self._s
        parts = [(0, 10, 40, 20), (10, 0, 30, 24), (30, 5, 35, 20)]
        for px, py, pw, ph in parts:
            pygame.draw.ellipse(surface, CLOUD_WHITE,
                                (sx+int(px*s), sy+int(py*s),
                                 int(pw*s), int(ph*s)))


# ─────────────────────────────────────────────
# FLAG POLE
# ─────────────────────────────────────────────
class FlagPole:
    def __init__(self, col):
        self._x = col * TILE + TILE//2

    def draw(self, surface, cam_x):
        sx = self._x - cam_x
        # Pole
        pygame.draw.rect(surface, (180, 180, 180), (sx-2, 3*TILE, 4, 11*TILE))
        pygame.draw.circle(surface, GOLD, (sx, 3*TILE), 8)
        # Flag
        pts = [(sx, 3*TILE+8), (sx+30, 3*TILE+20), (sx, 3*TILE+36)]
        pygame.draw.polygon(surface, FLAG_GREEN, pts)

    def check_win(self, mario_rect, cam_x) -> bool:
        sx = self._x - cam_x
        return mario_rect.right >= self._x - 16


# ─────────────────────────────────────────────
# HUD
# ─────────────────────────────────────────────
class HUD:
    def __init__(self):
        self._font      = pygame.font.SysFont("Courier New", 16, bold=True)
        self._font_big  = pygame.font.SysFont("Courier New", 36, bold=True)

    def draw(self, surface, score, coins, lives, time_left):
        # Semi-transparent bar
        bar = pygame.Surface((SW, 36), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, 0))

        items = [
            ("MARIO",  f"{score:06d}", 20),
            ("COINS",  f"x{coins:02d}",  SW//2 - 40),
            ("WORLD",  "1-1",          SW//2 + 40),
            ("TIME",   f"{time_left:03d}", SW - 100),
        ]
        for label, val, lx in items:
            lt = self._font.render(label, True, (200, 200, 200))
            vt = self._font.render(val,   True, WHITE)
            surface.blit(lt, (lx, 4))
            surface.blit(vt, (lx, 20))

    def draw_lives(self, surface, lives):
        t = self._font.render(f"LIVES: {lives}", True, WHITE)
        surface.blit(t, (20, 40))

    def draw_center(self, surface, text, sub=""):
        t  = self._font_big.render(text, True, WHITE)
        surface.blit(t, t.get_rect(center=(SW//2, SH//2 - 20)))
        if sub:
            s = self._font.render(sub, True, (200, 200, 200))
            surface.blit(s, s.get_rect(center=(SW//2, SH//2 + 24)))

    def draw_win(self, surface, score):
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        self.draw_center(surface, "COURSE CLEAR!", f"Score: {score:06d}  Press R to restart")


# ─────────────────────────────────────────────
# CAMERA
# ─────────────────────────────────────────────
class Camera:
    def __init__(self):
        self._x = 0
        self._max_x = (LEVEL_W - SW // TILE) * TILE

    def update(self, target_x):
        target = int(target_x) - SW // 3
        self._x = max(0, min(target, self._max_x))

    @property
    def x(self): return self._x


# ─────────────────────────────────────────────
# GAME CONTROLLER
# ─────────────────────────────────────────────
class Game:
    STATE_PLAY  = "play"
    STATE_DEAD  = "dead"
    STATE_WIN   = "win"
    STATE_START = "start"

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Super Mario Bros - World 1-1 (OOP Demo)")
        self._clock = pygame.time.Clock()
        self._hud   = HUD()
        self._score = 0
        self._coin_count = 0
        self._lives = 3
        self._load_level()

    def _load_level(self):
        tile_defs, enemy_defs, coin_defs, pipe_defs, flag_col = build_level()

        self._tiles   = [Tile(c, r, k)   for c, r, k in tile_defs]
        self._pipes   = [Pipe(c, h)      for c, h   in pipe_defs]
        self._coins   = [Coin(c, r)      for c, r   in coin_defs]
        self._enemies = [Goomba(c, r)    for c, r   in enemy_defs]
        self._flag    = FlagPole(flag_col)
        self._mario   = Mario(3, 14)
        self._camera  = Camera()
        self._state   = self.STATE_PLAY
        self._time    = 400
        self._time_timer = 0
        self._clouds  = [
            Cloud(100, 40, 1.2), Cloud(300, 60, 0.9), Cloud(550, 45, 1.5),
            Cloud(800, 55, 1.0), Cloud(1100, 40, 1.3), Cloud(1400, 60, 1.1),
            Cloud(1700, 45, 0.8), Cloud(2000, 50, 1.4), Cloud(2400, 40, 1.0),
            Cloud(2800, 55, 1.2), Cloud(3200, 45, 0.9), Cloud(3600, 60, 1.3),
        ]
        # Solid tiles for collision (ground + brick + Q)
        self._solid = self._tiles + self._pipes  # pipes are solid too

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    self.__init__()

    def _update(self):
        keys = pygame.key.get_pressed()

        if self._state == self.STATE_PLAY:
            # Timer countdown
            self._time_timer += 1
            if self._time_timer >= FPS:
                self._time_timer = 0
                self._time = max(0, self._time - 1)
                if self._time == 0:
                    self._mario.die()

            # Update objects
            self._mario.update(keys, self._tiles, self._pipes,
                               self._enemies, self._coins)
            for e in self._enemies:
                e.update(self._tiles, self._pipes)
            for c in self._coins:
                c.update()
            for cl in self._clouds:
                pass  # static clouds

            # Coin score
            collected = sum(1 for c in self._coins if c.collected)
            self._coin_count = collected
            self._score = collected * 200

            # Enemy stomp score
            squished = sum(1 for e in self._enemies if e.dead)
            self._score += squished * 100

            # Camera
            self._camera.update(self._mario.x)

            # Win condition
            if self._flag.check_win(self._mario.rect, self._camera.x):
                self._state = self.STATE_WIN
                self._score += self._time * 50

            # Death condition
            if not self._mario.alive:
                self._state = self.STATE_DEAD

        elif self._state == self.STATE_DEAD:
            self._mario.update(keys, [], [], [], [])
            if self._mario.dead_done:
                self._lives -= 1
                if self._lives <= 0:
                    self._load_level()
                    self._lives = 3
                else:
                    self._load_level()

    def _draw(self):
        # Sky
        self._screen.fill(SKY)

        cam = self._camera.x

        # Clouds (parallax)
        for cl in self._clouds:
            cl.draw(self._screen, cam)

        # Game objects
        for pipe in self._pipes:
            pipe.draw(self._screen, cam)
        for tile in self._tiles:
            tile.draw(self._screen, cam)
        for coin in self._coins:
            coin.draw(self._screen, cam)
        for enemy in self._enemies:
            enemy.draw(self._screen, cam)

        self._flag.draw(self._screen, cam)
        self._mario.draw(self._screen, cam)

        # HUD
        self._hud.draw(self._screen, self._score, self._coin_count,
                       self._lives, self._time)

        if self._state == self.STATE_WIN:
            self._hud.draw_win(self._screen, self._score)
        elif self._state == self.STATE_DEAD and not self._mario.alive:
            pass  # mario fall animation plays

        pygame.display.flip()

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self._clock.tick(FPS)


# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
