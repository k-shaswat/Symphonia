# Symphonia: Your Musical Companion

Symphonia is a Python-based application that allows you to extract musical notes from an audio file and play them using different soundfonts. It uses advanced signal processing techniques to analyze pitch data from the audio file and generate musical notes with customizable instruments. 

## Features

- **Audio to Music Conversion**: Extracts musical notes from an audio file (instrumental or vocals).
- **Soundfont Support**: Plays extracted notes with different instruments using FluidSynth.
- **Interactive Instrument Selection**: Allows users to choose from a list of soundfonts (instruments) to play the notes.
  
## Requirements

The project requires the following Python libraries:

- `librosa`: For audio processing and pitch extraction.
- `numpy`: For numerical operations.
- `math`: For frequency calculations.
- `fluidsynth`: For sound synthesis and MIDI playback.
- `os`: For file handling.

## Usage

1. Install required libraries
    ```bash
    pip install -r requirements.txt
2. Place your audio file (instrumental or vocals) in the desired folder.
3. Run the script:
   ```bash
   python symphonia.py

4. Once the audio is processed, the program will display the available instruments for you to choose from (e.g., Acoustic Guitar, Grand Piano, Mellotron Flute).

5. The program will then generate the notes and play them using the selected instrument's soundfont.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


