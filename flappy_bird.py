"""
Flappy Bird Clone - OOP Demo
Minh hoa cac khai niem OOP: Class, Inheritance, Encapsulation, Polymorphism
"""

import pygame
import random
import sys

# ============================================================
# CONSTANTS
# ============================================================
SCREEN_W, SCREEN_H = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -9
PIPE_SPEED = 3
PIPE_GAP = 160
PIPE_INTERVAL = 1500  # ms

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
SKY    = (78,  192, 202)
GREEN  = (83,  154, 57)
GREEN2 = (57,  125, 32)
YELLOW = (255, 213, 0)
ORANGE = (255, 150, 0)
RED    = (220, 50,  50)
GRAY   = (180, 180, 180)
DARK   = (40,  40,  40)
GROUND = (222, 184, 135)


# ============================================================
# CLASS: GameObject (Base class - Encapsulation)
# ============================================================
class GameObject:
    """Lop co so cho tat ca doi tuong trong game."""

    def __init__(self, x: float, y: float, w: int, h: int):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self._x), int(self._y), self._w, self._h)

    def draw(self, surface: pygame.Surface):
        """Phuong thuc ao - cac lop con se override."""
        raise NotImplementedError

    def update(self):
        """Cap nhat trang thai moi frame."""
        pass


# ============================================================
# CLASS: Bird (Inheritance, Encapsulation)
# ============================================================
class Bird(GameObject):
    """Con chim - nhan vat chinh cua game."""

    WING_UP   = 0
    WING_MID  = 1
    WING_DOWN = 2

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 34, 26)
        self._vel_y: float = 0
        self._alive: bool = True
        self._wing_state: int = self.WING_MID
        self._wing_timer: int = 0
        self._rotation: float = 0

    # --- Public interface ---
    def jump(self):
        if self._alive:
            self._vel_y = JUMP_FORCE

    def kill(self):
        self._alive = False

    @property
    def alive(self) -> bool:
        return self._alive

    @property
    def center(self):
        return (int(self._x + self._w / 2), int(self._y + self._h / 2))

    # --- Update ---
    def update(self):
        if not self._alive:
            # Roi xuong dat sau khi chet
            self._vel_y = min(self._vel_y + GRAVITY * 2, 15)
            self._y += self._vel_y
            self._rotation = -90
            return

        self._vel_y += GRAVITY
        self._vel_y = min(self._vel_y, 12)
        self._y += self._vel_y

        # Tinh goc xoay theo van toc
        self._rotation = max(-30, min(90, self._vel_y * 4))

        # Hoan phap canh
        self._wing_timer += 1
        if self._wing_timer >= 6:
            self._wing_timer = 0
            self._wing_state = (self._wing_state + 1) % 3

    # --- Draw ---
    def draw(self, surface: pygame.Surface):
        cx, cy = self.center
        # Ve than chim
        body_surf = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        self._draw_body(body_surf)

        # Xoay than
        angle = -self._rotation
        rotated = pygame.transform.rotate(body_surf, angle)
        rect = rotated.get_rect(center=(cx, cy))
        surface.blit(rotated, rect)

    def _draw_body(self, surf: pygame.Surface):
        w, h = self._w, self._h
        cx, cy = w // 2, h // 2

        # Than (ellipse vang)
        pygame.draw.ellipse(surf, YELLOW, (2, 4, w - 4, h - 6))
        pygame.draw.ellipse(surf, ORANGE, (2, 4, w - 4, h - 6), 2)

        # Canh
        if self._wing_state == self.WING_UP:
            pygame.draw.ellipse(surf, WHITE, (4, 2, 12, 7))
        elif self._wing_state == self.WING_MID:
            pygame.draw.ellipse(surf, WHITE, (4, cy - 3, 12, 7))
        else:
            pygame.draw.ellipse(surf, WHITE, (4, h - 9, 12, 7))

        # Mat
        pygame.draw.circle(surf, WHITE, (cx + 6, cy - 3), 5)
        pygame.draw.circle(surf, BLACK, (cx + 7, cy - 3), 3)
        pygame.draw.circle(surf, WHITE, (cx + 8, cy - 4), 1)

        # Mo
        beak_pts = [(cx + 10, cy - 1), (w, cy + 2), (cx + 10, cy + 4)]
        pygame.draw.polygon(surf, ORANGE, beak_pts)

    def get_mask(self) -> pygame.mask.Mask:
        surf = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 255, 255, 255), (4, 5, self._w - 8, self._h - 8))
        return pygame.mask.from_surface(surf)


# ============================================================
# CLASS: Pipe (Inheritance)
# ============================================================
class Pipe(GameObject):
    """Cap ong dan - vat can."""

    PIPE_W = 60

    def __init__(self, x: int, gap_y: int):
        super().__init__(x, 0, self.PIPE_W, SCREEN_H)
        self._gap_y = gap_y          # Trung tam khoang trong
        self._passed = False

    @property
    def passed(self) -> bool:
        return self._passed

    @passed.setter
    def passed(self, val: bool):
        self._passed = val

    @property
    def off_screen(self) -> bool:
        return self._x + self._w < 0

    def get_rects(self):
        """Tra ve rect cua ong tren va ong duoi."""
        top_h = self._gap_y - PIPE_GAP // 2
        bot_y = self._gap_y + PIPE_GAP // 2
        bot_h = SCREEN_H - bot_y
        top_rect = pygame.Rect(int(self._x), 0, self._w, top_h)
        bot_rect = pygame.Rect(int(self._x), bot_y, self._w, bot_h)
        return top_rect, bot_rect

    def update(self):
        self._x -= PIPE_SPEED

    def draw(self, surface: pygame.Surface):
        top_rect, bot_rect = self.get_rects()
        self._draw_pipe(surface, top_rect, flipped=True)
        self._draw_pipe(surface, bot_rect, flipped=False)

    def _draw_pipe(self, surface: pygame.Surface, rect: pygame.Rect, flipped: bool):
        # Than ong
        pygame.draw.rect(surface, GREEN, rect)
        pygame.draw.rect(surface, GREEN2, rect, 3)

        # Mui ong (hinh chu nhat rong hon)
        cap_h = 20
        cap_w = rect.w + 8
        if flipped:
            cap_rect = pygame.Rect(rect.x - 4, rect.bottom - cap_h, cap_w, cap_h)
        else:
            cap_rect = pygame.Rect(rect.x - 4, rect.top, cap_w, cap_h)

        pygame.draw.rect(surface, GREEN, cap_rect)
        pygame.draw.rect(surface, GREEN2, cap_rect, 3)

        # Highlight
        hi_rect = pygame.Rect(rect.x + 5, rect.y, 8, rect.h)
        pygame.draw.rect(surface, (120, 200, 80), hi_rect)


# ============================================================
# CLASS: Ground (Inheritance)
# ============================================================
class Ground(GameObject):
    """Mat dat cuon."""

    H = 80

    def __init__(self):
        super().__init__(0, SCREEN_H - self.H, SCREEN_W * 2, self.H)
        self._scroll = 0

    def update(self):
        self._scroll = (self._scroll + PIPE_SPEED) % SCREEN_W

    def draw(self, surface: pygame.Surface):
        x = -self._scroll
        # Ve 2 lan de tao hieu ung cuon vo tan
        for i in range(3):
            pygame.draw.rect(surface, GROUND, (x + i * SCREEN_W, SCREEN_H - self.H, SCREEN_W, self.H))
            pygame.draw.rect(surface, (180, 140, 90), (x + i * SCREEN_W, SCREEN_H - self.H, SCREEN_W, 6))
            # Ve co
            for gx in range(0, SCREEN_W, 20):
                pygame.draw.rect(surface, GREEN, (x + i * SCREEN_W + gx, SCREEN_H - self.H, 3, 8))

    @property
    def top(self) -> int:
        return SCREEN_H - self.H


# ============================================================
# CLASS: Particle (Hieu ung hat - Encapsulation)
# ============================================================
class Particle:
    def __init__(self, x, y):
        self.x = x + random.randint(-10, 10)
        self.y = y + random.randint(-10, 10)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, 0)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = random.choice([YELLOW, ORANGE, WHITE, RED])
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        r, g, b = self.color
        size = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), size)


# ============================================================
# CLASS: ScoreDisplay (Encapsulation)
# ============================================================
class ScoreDisplay:
    def __init__(self):
        self._font_big   = pygame.font.SysFont("Arial", 52, bold=True)
        self._font_med   = pygame.font.SysFont("Arial", 28, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 20)

    def draw_score(self, surface: pygame.Surface, score: int):
        text = self._font_big.render(str(score), True, WHITE)
        shadow = self._font_big.render(str(score), True, DARK)
        cx = SCREEN_W // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, 62)))
        surface.blit(text,   text.get_rect(center=(cx, 60)))

    def draw_best(self, surface: pygame.Surface, best: int):
        text = self._font_small.render(f"Best: {best}", True, WHITE)
        surface.blit(text, text.get_rect(center=(SCREEN_W // 2, 95)))

    def draw_panel(self, surface: pygame.Surface, score: int, best: int, state: str):
        """Ve bang diem o man hinh ket thuc."""
        panel = pygame.Surface((320, 200), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 160), panel.get_rect(), border_radius=16)
        surface.blit(panel, panel.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))

        cx = SCREEN_W // 2
        cy = SCREEN_H // 2 - 30

        title = self._font_med.render("GAME OVER" if state == "dead" else "FLAPPY BIRD", True, RED if state == "dead" else YELLOW)
        surface.blit(title, title.get_rect(center=(cx, cy - 70)))

        sc_label = self._font_small.render("Score", True, GRAY)
        sc_val   = self._font_med.render(str(score), True, WHITE)
        surface.blit(sc_label, sc_label.get_rect(center=(cx - 60, cy - 20)))
        surface.blit(sc_val,   sc_val.get_rect(center=(cx - 60, cy + 10)))

        bst_label = self._font_small.render("Best", True, GRAY)
        bst_val   = self._font_med.render(str(best), True, YELLOW)
        surface.blit(bst_label, bst_label.get_rect(center=(cx + 60, cy - 20)))
        surface.blit(bst_val,   bst_val.get_rect(center=(cx + 60, cy + 10)))

        hint = self._font_small.render("SPACE / Click de choi lai", True, WHITE)
        surface.blit(hint, hint.get_rect(center=(cx, cy + 60)))

    def draw_start(self, surface: pygame.Surface):
        cx = SCREEN_W // 2
        title = self._font_big.render("FLAPPY", True, YELLOW)
        sub   = self._font_big.render("BIRD",   True, ORANGE)
        hint  = self._font_small.render("Nhan SPACE hoac Click de bat dau", True, WHITE)
        surface.blit(title, title.get_rect(center=(cx, SCREEN_H // 2 - 80)))
        surface.blit(sub,   sub.get_rect(center=(cx, SCREEN_H // 2 - 20)))
        surface.blit(hint,  hint.get_rect(center=(cx, SCREEN_H // 2 + 60)))


# ============================================================
# CLASS: Background (Inheritance + Polymorphism)
# ============================================================
class Background(GameObject):
    """Nen bau troi voi may."""

    def __init__(self):
        super().__init__(0, 0, SCREEN_W, SCREEN_H)
        self._clouds = [
            {"x": random.randint(0, SCREEN_W), "y": random.randint(30, 200), "w": random.randint(60, 120), "spd": random.uniform(0.3, 0.8)}
            for _ in range(5)
        ]

    def update(self):
        for c in self._clouds:
            c["x"] -= c["spd"]
            if c["x"] + c["w"] < 0:
                c["x"] = SCREEN_W + 20
                c["y"] = random.randint(30, 200)

    def draw(self, surface: pygame.Surface):
        surface.fill(SKY)
        for c in self._clouds:
            self._draw_cloud(surface, int(c["x"]), c["y"], c["w"])

    def _draw_cloud(self, surface, x, y, w):
        h = w // 2
        pygame.draw.ellipse(surface, WHITE, (x, y, w, h))
        pygame.draw.ellipse(surface, WHITE, (x + w // 4, y - h // 2, w // 2, h // 2))


# ============================================================
# CLASS: Game (Controller - tong hop tat ca)
# ============================================================
class Game:
    """Lop dieu khien toan bo tro choi - Polymorphism qua cac doi tuong."""

    STATE_START = "start"
    STATE_PLAY  = "play"
    STATE_DEAD  = "dead"

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Flappy Bird - OOP Demo")
        self._clock = pygame.time.Clock()

        self._bg      = Background()
        self._ground  = Ground()
        self._score_display = ScoreDisplay()

        self._best_score = 0
        self._state = self.STATE_START

        self._reset()

    def _reset(self):
        self._bird      = Bird(80, SCREEN_H // 2)
        self._pipes: list[Pipe] = []
        self._particles: list[Particle] = []
        self._score     = 0
        self._last_pipe = pygame.time.get_ticks()
        self._state     = self.STATE_START if self._state == self.STATE_START else self.STATE_START

    def _spawn_pipe(self):
        gap_y = random.randint(180, SCREEN_H - Ground.H - 100)
        self._pipes.append(Pipe(SCREEN_W + 10, gap_y))

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                key = getattr(event, "key", None)
                if key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self._state == self.STATE_START:
                    self._state = self.STATE_PLAY
                    self._last_pipe = pygame.time.get_ticks()
                elif self._state == self.STATE_PLAY:
                    self._bird.jump()
                    # Hieu ung hat khi nhay
                    bx, by = self._bird.center
                    for _ in range(5):
                        self._particles.append(Particle(bx, by))
                elif self._state == self.STATE_DEAD:
                    self._reset()
                    self._state = self.STATE_PLAY
                    self._last_pipe = pygame.time.get_ticks()

    def _update(self):
        now = pygame.time.get_ticks()

        self._bg.update()
        self._ground.update()

        if self._state == self.STATE_PLAY:
            self._bird.update()

            # Spawn ong dan
            if now - self._last_pipe > PIPE_INTERVAL:
                self._spawn_pipe()
                self._last_pipe = now

            # Cap nhat ong
            for pipe in self._pipes:
                pipe.update()

                # Kiem tra qua ong -> tang diem
                bird_cx = self._bird.center[0]
                if not pipe.passed and pipe.rect.right < bird_cx:
                    pipe.passed = True
                    self._score += 1
                    if self._score > self._best_score:
                        self._best_score = self._score

                # Kiem tra va cham
                if self._bird.alive:
                    top_rect, bot_rect = pipe.get_rects()
                    bird_rect = self._bird.rect
                    # Thu hep mot chut de de choi hon
                    inner = bird_rect.inflate(-8, -8)
                    if inner.colliderect(top_rect) or inner.colliderect(bot_rect):
                        self._bird.kill()
                        self._state = self.STATE_DEAD
                        for _ in range(20):
                            self._particles.append(Particle(*self._bird.center))

            # Xoa ong da di qua man hinh
            self._pipes = [p for p in self._pipes if not p.off_screen]

            # Kiem tra roi dat / len tran
            if self._bird.alive:
                if self._bird.rect.bottom >= self._ground.top or self._bird.rect.top <= 0:
                    self._bird.kill()
                    self._state = self.STATE_DEAD
                    for _ in range(20):
                        self._particles.append(Particle(*self._bird.center))

        elif self._state == self.STATE_DEAD:
            self._bird.update()

        # Cap nhat hat
        for p in self._particles:
            p.update()
        self._particles = [p for p in self._particles if p.life > 0]

    def _draw(self):
        # Ve nen
        self._bg.draw(self._screen)

        # Ve ong
        for pipe in self._pipes:
            pipe.draw(self._screen)

        # Ve dat
        self._ground.draw(self._screen)

        # Ve chim
        self._bird.draw(self._screen)

        # Ve hat
        for p in self._particles:
            p.draw(self._screen)

        # Ve UI
        if self._state == self.STATE_START:
            self._score_display.draw_panel(self._screen, 0, self._best_score, "start")
        elif self._state == self.STATE_PLAY:
            self._score_display.draw_score(self._screen, self._score)
            self._score_display.draw_best(self._screen, self._best_score)
        elif self._state == self.STATE_DEAD:
            self._score_display.draw_panel(self._screen, self._score, self._best_score, "dead")

        pygame.display.flip()

    def run(self):
        """Vong lap chinh cua game."""
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self._clock.tick(FPS)


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    game = Game()
    game.run()
