import librosa
import numpy as np
import math
import fluidsynth
import time
import os

# Constants
NOTE_FREQUENCIES = {
    'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'D#0': 19.45, 'E0': 20.60, 'F0': 21.83, 'F#0': 23.12, 'G0': 24.50,
    'G#0': 25.96, 'A0': 27.50, 'A#0': 29.14, 'B0': 30.87, 'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89,
    'E1': 41.20, 'F1': 43.65, 'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
    'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00,
    'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47, 'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56,
    'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
    'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88, 'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
    'E5': 659.26, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98,
    'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53, 'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02,
    'E7': 2637.02, 'F7': 2793.83, 'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'A#7': 3729.31, 'B7': 3951.07,
    'C8': 4186.01
}


# Function to validate sustained notes. By default, note sustained for less than 0.1 seconds are ignored. 
def validate_sustained_notes(notes, threshold=5):
    """
    Args:
    notes (list): A list of musical notes sampled every 0.1 seconds.
    threshold (int): The minimum number of consecutive occurrences a note must appear to be valid.

    Returns:
    list: A list of notes with invalid (short-lived) notes replaced with None.
    """
    valid_notes = []
    n = len(notes)
    i = 0

    while i < n:
        current_note = notes[i]
        count = 1

        # Count how many times the current note appears consecutively
        while i + 1 < n and notes[i + 1] == current_note:
            count += 1
            i += 1

        # If the note is sustained enough, it's valid, otherwise replace it with None
        if count >= threshold:
            valid_notes.extend([current_note] * count)
        else:
            valid_notes.extend([None] * count)

        i += 1  # Move to the next unique note

    return valid_notes


# Function to convert frequency to musical note
def frequency_to_note(frequency):
    if isinstance(frequency, np.float64) and np.isnan(frequency):
        return None

    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    A4_freq = 440.0  # Reference frequency for A4

    semitones = round(12 * math.log2(frequency / A4_freq))
    note_index = (semitones + 9) % 12
    octave = 4 + (semitones + 9) // 12
    note_name = notes[note_index]

    return f"{note_name}{octave}"


# Function to play notes using FluidSynth
def play_notes_with_soundfont(note_and_duration, soundfont_path):
    """
    Plays notes using the specified SoundFont.
    """
    
    fs = fluidsynth.Synth()
    fs.start(driver='dsound')  # Windows DirectSound driver. #Change Driver based on platform.

    # Load the SoundFont
    sfid = fs.sfload(soundfont_path)
    fs.program_select(0, sfid, 0, 0)

    for note_duration in note_and_duration:
        note_name, duration = note_duration
        if note_name in NOTE_FREQUENCIES:
            frequency = NOTE_FREQUENCIES[note_name]
            midi_note = round(69 + 12 * np.log2(frequency / 440.0))
            print(f"Playing note: {note_name} (MIDI: {midi_note})")

            # Play the note
            fs.noteon(0, midi_note, 50)
            time.sleep(duration)
            fs.noteoff(0, midi_note)

    fs.delete()  # Clean up resources


# Function to load audio file and extract pitch using YIN algorithm
def extract_pitches_from_audio(audio_path):

    print("Processing audio file: ", audio_path)

    try:
        y, sr = librosa.load(audio_path)
    except Exception as e:
        print("Error loading audio file: ", e)
        return [], []

    pitches, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))
    pitch_values = pitches
    time_values = librosa.times_like(pitches).tolist()

    return pitch_values, time_values


# Function to gather notes and durations from pitch data
def get_notes_and_durations(pitch_values, time_values):
    """
    Converts pitch values to musical notes and calculates their durations.
    """
    notes = [frequency_to_note(f) for f in pitch_values]
    sustained_notes = validate_sustained_notes(notes)

    note_and_duration = []
    i = 0
    while i < len(sustained_notes):
        start_note = sustained_notes[i]
        start_time = time_values[i]
        while i < len(sustained_notes) and sustained_notes[i] == start_note:
            i += 1

        end_time = time_values[i-1]
        duration = end_time - start_time
        note_and_duration.append([start_note, duration])

    return note_and_duration


# Main function to drive the program
def main():
    audio_path = input("Enter the path of the instrumental/vocal file: ").strip()

    if not os.path.exists(audio_path):
        print("File not found: ", audio_path)
        exit(1)

    pitch_values, time_values = extract_pitches_from_audio(audio_path)


    note_and_duration = get_notes_and_durations(pitch_values, time_values)

    while True:
        try:
            instrument_choice = int(input("Enter the output instrument:\n1: Acoustic Guitar\n2: Grand Piano\n3: Mellotron Flute\n"))
            if instrument_choice not in [1, 2, 3]:
                raise ValueError("Invalid instrument choice.")
            
            instruments = ["guitar", "piano", "flute"]
            instrument = instruments[instrument_choice - 1]
            soundfont_path = f"./soundfront/{instrument}.sf2"

            play_notes_with_soundfont(note_and_duration, soundfont_path)

            continue_choice = input("Do you want to play another instrument? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("Exiting the program.")
                break

        except ValueError as e:
            print("Error: ", e)
            continue


if __name__ == "__main__":
    print("Welcome to Symphonia: Your Musical Companion \n")
    main()
