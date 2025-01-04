
# ATM PIN Cracker Simulation

This project simulates a process of "cracking" a 4-digit ATM PIN in a visual and auditory manner, mimicking old-school hacking aesthetics.

## Features

- Randomly generated numbers that gradually refine to a 4-digit PIN.
- Colorful, retro-styled terminal output.
- Real-time sound effects to enhance the experience.
- Fully contained within a Docker environment for portability.

## How It Works

1. The program generates a grid of random numbers.
2. Numbers are refined in each step until only 4 digits remain.
3. A PIN is "cracked" and displayed with accompanying sound effects.

## Requirements

- Docker installed on your system.
- Packages for reproduce sounds:
  ```bash
  sudo apt update -yqq && sudo apt install -yqq alsa-utils
  ```

## Usage

1. Build the Docker image:

   ```bash
   docker build -t pin-cracker .
   ```

2. Run the container:

   ```bash
   docker run --rm -it --device /dev/snd pin-cracker
   ```

## Technical Details

- **Programming Language**: Python 3.10
- **Dependencies**:
  - `simpleaudio`: For sound effects.
  - `numpy`: To generate sine waves for tones.
  - `colorama`: For colored terminal output.

## Design Principles

This project adheres to the following principles:
- **DRY**: The code is modular and avoids redundancy.
- **KISS**: The logic is simple and easy to follow.

## Disclaimer

This is a simulation for educational purposes and entertainment only. Unauthorized access to ATMs or any other device is illegal.
