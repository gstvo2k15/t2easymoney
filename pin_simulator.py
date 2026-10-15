"""Local, cinematic PIN identification simulation based on easymoney.mp4."""

import argparse
import math
import os
from pathlib import Path
import random
import time

AUDIO_PATH = Path(__file__).resolve().parent / "assets" / "identification.wav"
ROWS = 10
COLUMNS = 48
SCAN_SECONDS = 2.0
REFINE_SECONDS = 3.0
TITLE = (
    "PPPPP   IIIIIII   N     N",
    "P    P     I      NN    N   IDENTIFICATION",
    "P    P     I      N N   N",
    "PPPPP      I      N  N  N     PROGRAM",
    "P          I      N   N N",
    "P          I      N    NN",
    "P       IIIIIII   N     N",
)


def number_grid(elapsed, seed=7, pin="9003"):
    """Keep ten rows while narrowing the matrix to the reference PIN."""
    progress = min(1.0, max(0.0, (elapsed - SCAN_SECONDS) / REFINE_SECONDS))
    width = max(4, COLUMNS - int(progress * (COLUMNS - 4)))
    rng = random.Random(seed + int(max(0, elapsed) * 15))
    if progress == 1:
        return [pin] * ROWS
    return [pin + "".join(rng.choice("0123456789") for _ in range(width - 4))
            for _ in range(ROWS)]


class Simulator:
    """Fixed-resolution LCD renderer; resizing never changes the layout."""

    def __init__(self, pygame, size=(960, 540), mute=False, fullscreen=False):
        self.pg = pygame
        pygame.display.init()
        pygame.font.init()
        flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
        self.window = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("PIN Identification Program")
        self.canvas = pygame.Surface((640, 360))
        self.font = pygame.font.SysFont("couriernew,dejavusansmono,liberationmono,monospace", 14)
        self.ink = (31, 49, 56)
        self.background = self.make_background()
        self.state = "ready"
        self.started = 0.0
        self.pin = None
        self.sound = None
        self.sound_channel = None
        if not mute:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
                self.sound = pygame.mixer.Sound(str(AUDIO_PATH))
            except pygame.error:
                pass  # The visual simulation also works without an audio device.

    def make_background(self):
        pg = self.pg
        surface = pg.Surface((640, 360))
        surface.fill((0, 0, 0))
        pg.draw.rect(surface, (64, 83, 91), (6, 47, 628, 266))
        pg.draw.rect(surface, (22, 37, 44), (23, 52, 591, 244), border_radius=7)
        pg.draw.rect(surface, (10, 25, 30), (43, 71, 563, 207), border_radius=7)
        rng = random.Random(31)
        # Static grain and uneven backlight approximate the filmed LCD surface.
        for y in range(78, 269):
            for x in range(53, 600):
                glow = 13 * math.sin(math.pi * (x - 53) / 547)
                shade = rng.randrange(-7, 8) + glow - abs(y - 167) * .035
                surface.set_at((x, y), (int(123 + shade), int(132 + shade), int(115 + shade)))
        return surface

    def text(self, value, x, y):
        self.canvas.blit(self.font.render(value, True, self.ink), (x, y))

    def begin(self, now):
        self.stop_sound()
        self.pin = f"{random.SystemRandom().randrange(10000):04d}"
        self.state = "scanning"
        self.started = now
        if self.sound:
            self.sound_channel = self.sound.play()

    def stop_sound(self):
        if self.sound_channel:
            self.sound_channel.stop()
            self.sound_channel = None

    def render(self, elapsed=0.0, blink=True):
        self.canvas.blit(self.background, (0, 0))
        # All text is clipped to the glass rather than spilling into the bezel.
        self.canvas.set_clip((53, 78, 547, 191))
        if self.state == "ready":
            for row, line in enumerate(TITLE):
                self.text(line, 53, 95 + row * 15)
            self.text("Strike a key when ready ...", 53, 226)
            if blink:
                self.pg.draw.rect(self.canvas, self.ink, (53 + self.font.size("Strike a key when ready ...")[0], 229, 9, 14))
        else:
            grid = number_grid(elapsed, pin=self.pin)
            done = elapsed >= SCAN_SECONDS + REFINE_SECONDS
            if done:
                # The last shot retains four copies above the result.
                for row in range(4):
                    self.text(self.pin, 53, 91 + row * 15)
                self.text("PIN IDENTIFICATION NUMBER: " + self.pin, 53, 179)
                self.text(">", 53, 211)
                if blink:
                    self.pg.draw.rect(self.canvas, self.ink, (66, 214, 9, 14))
            else:
                visible = min(ROWS, 1 + int(elapsed / .08))
                for row, line in enumerate(grid[:visible]):
                    self.text(line, 53, 92 + row * 15)
        self.canvas.set_clip(None)
        return self.canvas

    def present(self):
        width, height = self.window.get_size()
        scale = min(width / 640, height / 360)
        size = (max(1, int(640 * scale)), max(1, int(360 * scale)))
        self.window.fill((0, 0, 0))
        self.window.blit(self.pg.transform.smoothscale(self.canvas, size),
                         ((width - size[0]) // 2, (height - size[1]) // 2))
        self.pg.display.flip()

    def run(self, autoplay=False):
        clock = self.pg.time.Clock()
        if autoplay:
            self.begin(time.monotonic())
        running = True
        while running:
            now = time.monotonic()
            for event in self.pg.event.get():
                if event.type == self.pg.QUIT:
                    running = False
                elif event.type == self.pg.KEYDOWN:
                    if event.key in (self.pg.K_ESCAPE, self.pg.K_RETURN, self.pg.K_KP_ENTER):
                        running = False
                    elif self.state == "ready":
                        self.begin(now)
                    elif event.key == self.pg.K_r:
                        self.stop_sound()
                        self.state = "ready"
                elif event.type == self.pg.VIDEORESIZE:
                    self.window = self.pg.display.set_mode(event.size, self.pg.RESIZABLE)
            elapsed = now - self.started if self.state != "ready" else 0
            self.render(elapsed, int(now * 2) % 2 == 0)
            self.present()
            clock.tick(30)
        self.stop_sound()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mute", action="store_true", help="Disable keyboard and electronic sound effects")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--autoplay", action="store_true", help="Start without waiting for a key")
    parser.add_argument("--snapshot", type=Path, help="Save a frame without opening a window")
    parser.add_argument("--at", type=float, default=0, help="Seconds into identification for snapshot")
    parser.add_argument("--ready", action="store_true", help="Snapshot the initial title")
    args = parser.parse_args()
    if args.snapshot:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("Install dependencies: python -m pip install -r requirements.txt") from exc
    try:
        app = Simulator(pygame, mute=args.mute or bool(args.snapshot), fullscreen=args.fullscreen)
        if args.snapshot:
            if not args.ready:
                app.begin(0)
            pygame.image.save(app.render(max(0, args.at)), str(args.snapshot))
        else:
            app.run(args.autoplay)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
