"""
ATM PIN Cracker Simulation
Simulates the process of cracking a 4-digit ATM PIN with sound and visual effects.
"""

import sys
import os
import tty
import termios
import random
import time
import simpleaudio as sa # pylint: disable=import-error
import numpy as np
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

COLORS = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.CYAN]

def clear_screen():
    """Clear the terminal screen for a retro effect."""
    os.system("clear" if os.name == "posix" else "cls")

def wait_for_any_key():
    """Wait for any key press."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdin.read(1)  # Wait for a single key press
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old_settings)

def generate_random_numbers(count, length):
    """Generate a list of random numbers with a fixed length."""
    return [str(random.randint(0, 10**length - 1)).zfill(length) for _ in range(count)]

def display_numbers(numbers):
    """Display numbers on the screen in a grid with colors."""
    for number in numbers:
        colored_number = "".join(random.choice(COLORS) + digit for digit in number)
        print(colored_number)
    print("\nProcessing...\n")

def generate_tone(frequency, duration):
    """Generate a sine wave tone."""
    sample_rate = 44100
    t = np.linspace(0, duration / 1000, int(sample_rate * (duration / 1000)), endpoint=False)
    wave = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    return wave

def play_tone(frequency, duration):
    """Play a tone for a specific frequency and duration."""
    wave = generate_tone(frequency, duration)
    play_obj = sa.play_buffer(wave, 1, 2, 44100)
    play_obj.wait_done()

def refine_numbers(numbers):
    """Gradually refine random numbers to a single 4-digit PIN."""
    while len(numbers) > 4:
        # Reduce the list to half its size
        numbers = numbers[: len(numbers) // 2]
        clear_screen()
        display_numbers(numbers)
        play_tone(400, 200)
        time.sleep(0.5)

    # Refine each digit to the correct PIN
    pin = ""
    for i in range(4):
        for number in numbers:
            pin += random.choice(number[i])
            clear_screen()
            display_numbers([pin.ljust(4, "_")])
            play_tone(400 + int(pin[-1]) * 50, 200)
            time.sleep(0.2)
        pin = pin[:4]

    return pin

def main():
    """Main function to execute the ATM PIN cracker simulation."""
    clear_screen()
    print(Fore.YELLOW + "ATM ACCESS PROGRAM")
    print(Fore.YELLOW + "Press any key to begin the simulation...")
    wait_for_any_key()

    # Generate random numbers
    random_numbers = generate_random_numbers(16, 4)
    clear_screen()
    display_numbers(random_numbers)

    # Gradually refine numbers to find the PIN
    pin = refine_numbers(random_numbers)

    # Display the final PIN
    clear_screen()
    print(Fore.GREEN + f"PIN CRACKED: {pin}")
    play_tone(800, 500)
    print(Fore.RED + "\nAccess Granted. Unauthorized use detected. Exiting...")

if __name__ == "__main__":
    main()
