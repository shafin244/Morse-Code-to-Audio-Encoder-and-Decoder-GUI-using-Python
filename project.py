import tkinter as tk
from tkinter import filedialog, messagebox
import wave
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-', '?': '..--..',
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': '/'
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(char.upper(), '') for char in text)

def morse_to_text(morse):
    reversed_dict = {v: k for k, v in MORSE_CODE_DICT.items()}
    return ''.join(reversed_dict.get(code, '') for code in morse.split(' '))

# Define the duration of dots, dashes, and spaces (in seconds)
dot_duration = 0.05
dash_duration = 3 * dot_duration
intra_char_space_duration = dot_duration
inter_char_space_duration = 3 * dot_duration
word_space_duration = 7 * dot_duration

# Define the sample rate
sample_rate = 8000

def generate_sine_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t +  0.03)

# Function to generate the waveform for a Morse code symbol
def morse_to_waveform(morse_code, sample_rate):
    frequency = 1000  # Frequency of the tone (in Hz)
    waveform = np.array([])

    for symbol in morse_code:
        if symbol == '.':
            waveform = np.concatenate((waveform, generate_sine_wave(frequency, dot_duration, sample_rate)))
        elif symbol == '-':
            waveform = np.concatenate((waveform, generate_sine_wave(frequency, dash_duration, sample_rate)))
        elif symbol == ' ':
            waveform = np.concatenate((waveform, np.zeros(int(sample_rate * inter_char_space_duration))))
        elif symbol == '/':
            waveform = np.concatenate((waveform, np.zeros(int(sample_rate * word_space_duration))))
        
        # Add intra-character space after each dot or dash
        if symbol in ['.', '-']:
            waveform = np.concatenate((waveform, np.zeros(int(sample_rate * intra_char_space_duration))))

    return waveform

def encode_morse_to_audio():
    morse_string = morse_output.get("1.0", "end-1c")
    morse_waveform = morse_to_waveform(morse_string, sample_rate)
    # Normalize the waveform to the range of int16
    morse_waveform = np.int16(morse_waveform / np.max(np.abs(morse_waveform)) * 32767)
    # Save the waveform to a WAV file
    with wave.open('morse_encoded.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(morse_waveform.tobytes())

def decode_audio_to_morse(file_path):
    wav_file = wave.open(file_path, "rb") 

    sample_rate = wav_file.getframerate()  # Samples per second
    n_frames = wav_file.getnframes()

    audio_data = wav_file.readframes(n_frames)
    audio_signal = np.frombuffer(audio_data, dtype=np.int16)
    audio_signal = audio_signal / np.max(np.abs(audio_signal))
    audio_signal = np.abs(audio_signal) 
    binary_signal = np.where(audio_signal > 0.00, 1, 0)
    result = []
    Len = []
    length = 0
    length2 = 0
    dash_threshold=1000
    for bit in binary_signal:
        if bit == 1:
            length += 1  # Count consecutive 1s
            if length2 > 0:
                Len.append(length2)
                if length2 > 2000 :
                    result.append(" / ") 
                elif length2 >400 and length2 < 2000:
                    result.append(' ')
                length2 = 0
        else:
            length2 +=1
            if length > 0:
                Len.append(length)
                if length < dash_threshold and length > 0 :
                    result.append('.')  # Longer duration is a dash
                
                elif length >= dash_threshold:
                    result.append('-')  # Very long duration indicates a space
                length = 0  # Reset length counter
    
    char_array = result
    result_string = ''.join(char_array)
    print(result_string)
    return result_string

def convert_text_to_morse():
    input_text = text_input.get("1.0", "end-1c")
    morse_output.delete("1.0", "end")
    morse_output.insert("1.0", text_to_morse(input_text))

def convert_morse_to_text():
    input_morse = morse_input.get("1.0", "end-1c")
    text_output.delete("1.0", "end")
    text_output.insert("1.0", morse_to_text(input_morse))

def open_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        morse_from_audio = decode_audio_to_morse(file_path)
        audio_morse_output.delete("1.0","end")
        audio_morse_output.insert("1.0", morse_to_text(morse_from_audio))

def character_play():
    text = text_input.get("1.0", "end-1c")
    char = text[-1]
    morse_char = text_to_morse(char)
    char_waveform = morse_to_waveform(morse_char, sample_rate)
    sd.play(char_waveform, sample_rate)

# Set up the GUI
root = tk.Tk()
root.title("Morse Code Translator")
root.geometry("800x600")  # Fixed size window
root.resizable(False, False)  # Disable resizing

# Set background color
root.configure(bg="#f0f8ff")

# Style configuration
label_bg = "#007acc"
label_fg = "white"
button_bg = "#4CAF50"
button_fg = "white"
text_bg = "#e6f7ff"
text_fg = "#333333"

# Text input
tk.Label(root, text="Text Input:", bg=label_bg, fg=label_fg, font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
text_input = tk.Text(root, height=5, width=50, bg=text_bg, fg=text_fg, font=("Arial", 14))
text_input.grid(row=0, column=1, padx=10, pady=10)
# Bind key release event to update Morse output dynamically
text_input.bind("<KeyRelease>", lambda event: (convert_text_to_morse(), character_play()))

# Morse output
tk.Label(root, text="Morse Output:", bg=label_bg, fg=label_fg, font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
morse_output = tk.Text(root, height=5, width=50, bg=text_bg, fg=text_fg, font=("Arial", 14))
morse_output.grid(row=1, column=1, padx=10, pady=10)

# Button to encode Morse code to audio
encode_audio_button = tk.Button(root, text="Encode Morse to Audio", command=encode_morse_to_audio, bg=button_bg, fg=button_fg, font=("Arial", 10, "bold"))
encode_audio_button.grid(row=3, column=1, pady=10, sticky="w")

# Audio file input button
audio_to_morse_button = tk.Button(root, text="Decode Morse from Audio", command=open_audio_file, bg=button_bg, fg=button_fg, font=("Arial", 10, "bold"))
audio_to_morse_button.grid(row=4, column=1, pady=10, sticky="w")

tk.Label(root, text="Morse Output from Audio", bg=label_bg, fg=label_fg, font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
audio_morse_output = tk.Text(root, height=5, width=50, bg=text_bg, fg=text_fg, font=("Arial", 14))
audio_morse_output.grid(row=5, column=1, padx=10, pady=10)

root.mainloop()
