"""Check the visible sequence, independently of the window and audio device."""
import unittest
import os
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from pin_simulator import number_grid, Simulator, ROWS, COLUMNS


class ReferenceSequenceTests(unittest.TestCase):
    def test_matrix_fills_width_before_refining(self):
        grid = number_grid(1)
        self.assertEqual(len(grid), 10)
        self.assertTrue(all(len(row) == 48 and row.isdigit() for row in grid))

    def test_refinement_removes_columns_not_rows(self):
        grids = [number_grid(t / 10) for t in range(20, 51)]
        widths = [len(grid[0]) for grid in grids]
        self.assertEqual(widths, sorted(widths, reverse=True))
        self.assertTrue(all(len(grid) == ROWS for grid in grids))
        self.assertEqual(widths[0], COLUMNS)
        self.assertEqual(widths[-1], 4)

    def test_selected_result_is_stable_including_leading_zero(self):
        for seconds in (5, 6, 100):
            self.assertEqual(number_grid(seconds, pin="0042"), ["0042"] * 10)

    def test_frames_are_reproducible(self):
        self.assertEqual(number_grid(2.7), number_grid(2.7))


class ApplicationTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_each_start_generates_a_new_pin_and_result_uses_it(self):
        app = Simulator(pygame, mute=True)
        with patch("pin_simulator.random.SystemRandom") as rng:
            rng.return_value.randrange.side_effect = [42, 9876]
            app.begin(0)
            self.assertEqual(app.pin, "0042")
            with patch.object(app, "text") as text:
                app.render(5)
                text.assert_any_call("PIN IDENTIFICATION NUMBER: 0042", 53, 179)
            app.begin(10)
            self.assertEqual(app.pin, "9876")

    def test_enter_exits_from_ready_scanning_and_result(self):
        for key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            for elapsed in (None, 0, 6):
                app = Simulator(pygame, mute=True)
                if elapsed is not None:
                    app.begin(-elapsed)
                event = pygame.event.Event(pygame.KEYDOWN, key=key)
                # A second iteration fails instead of hanging if Enter is ignored.
                with patch("pygame.event.get", side_effect=[[event], AssertionError("Enter did not exit")]):
                    app.run()

    def test_clean_audio_plays_once_and_stops_on_exit(self):
        app = Simulator(pygame)
        self.assertIsNotNone(app.sound)
        self.assertAlmostEqual(app.sound.get_length(), 5, places=2)
        app.begin(0)
        self.assertIsNotNone(app.sound_channel)
        self.assertTrue(app.sound_channel.get_busy())
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        app.run()
        self.assertIsNone(app.sound_channel)


if __name__ == "__main__":
    unittest.main()
