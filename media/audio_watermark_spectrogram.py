# -*- coding: utf-8 -*-
"""audio_watermark_spectrogram.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/gist/avipars/e41d76f01fd971f841ffa99f1ce110d4/audio_watermark_spectrogram.ipynb

# WAV Stegoanography / Watermarking

Slightly modified and adapted from this github repo: https://github.com/DrSDR/Audio-Spectrogram-


1.   Includes plots/graphics
2.   Now in jupyter notebook
3.   See intermediary results and pictures

# Install Dependencies
"""

!pip install Pillow
!pip install scipy
!pip install matplotlib

"""# File Upload"""

!mkdir outputs
from google.colab import files #upload and download

print("All of the files are saved temporarily on colab (till the runtime shuts down)")

print("Upload your watermark image (png preferred)")
watermarked = files.upload()

watermarked_val = list(watermarked.values())[0]
watermarked_path = list(watermarked.keys())[0]

print("Upload original audio file (wav)")
original_audio = files.upload()

original_audio_val = list(original_audio.values())[0]
original_audio_path = list(original_audio.keys())[0]

# @title
# for debugging or if you already uploaded the files and don't want to do that again, uncomment the following and run it

#watermarked_path = "watermark.png"
# original_audio_path = "colaco_jingle_stereo.wav"

"""# Configuration

"""

# @title Settings { run: "auto" }
print("to_flip = Mirror the Image")
print("to_rotate90 = Rotate image 90 degrees")
print("to_resize = Resize the Image or not (if latter, ignore the new width and new height)")
to_flip = True # @param {"type":"boolean","placeholder":"Flip the image"}
to_rotate90 = False # @param {"type":"boolean","placeholder":"Rotate image 90 degrees"}
to_resize = True # @param {"type":"boolean","placeholder":"Resize the image or not"}

print("channel: What channel should the watermark go on")
channel = "Right" # @param ["Left", "Right"]
if channel == "Left":
  watermark_channel = 0
else:
  watermark_channel = 1

print("from 0 to 1, how birght the watermark will be")
watermark_strength = 0.2 # @param {type:"slider", min:0, max:1, step:0.1}

# @title Resizing
from PIL import Image # image magic

img = Image.open(watermarked_path)
width, height = img.size

print(f"Original size W:{width}x H:{height}")

new_width = 400 # @param {"type":"number","placeholder":"New Width", min:5}
new_height = 400 # @param {"type":"number","placeholder":"New Height", min:5}

if to_resize:
  img = img.resize((new_width, new_height))

"""#Processing image and audio"""

import numpy as np # fancy arrays
import matplotlib.pyplot as plt #plotting stuff
def load_and_process_image(img, to_flip, to_rotate90):
    data = np.array(img, dtype='float')
    data = 0.2989*data[:,:,0] + 0.5870*data[:,:,1] + 0.1140*data[:,:,2]   # convert to grayscale old fashioned way
    data = data / np.max(data) # normalize it

    if to_flip:
      data = np.flip(data, axis=0) # flip it

    if to_rotate90:
      data = np.rot90(data, k=1, axes=(0,1)) # rotate 90 degrees
    return data

image_data = load_and_process_image(img, to_flip, to_rotate90)
plt.imshow(image_data,cmap="gray")    # show image in colab
plt.show()

from scipy.io import wavfile
def create_watermark_signal(image_data, fs, og_fs=24000):
    h, w = image_data.shape
    phdata = np.random.randn(h, w)
    phdata = 23 * phdata
    phdata = np.exp(1j * phdata)
    data = image_data * phdata

    d2 = data
    d1 = np.flip(data, axis=1) # flip again
    d1 = d1[:, 0:-1]
    d1 = np.conjugate(d1)
    data = np.concatenate((d1, data), axis=1)
    data = np.fft.ifftshift(data, axes=1) # inverse fast fourier transform
    data = np.fft.ifft(data, axis=1)

    data = data.flatten()
    data = np.real(data)
    data = data / np.max(data)
    data = np.multiply(data, 32767) #16 bit integer bound
    data = data.astype(np.int16)

    # Adjust the length of the watermark signal to match the input audio
    target_length = int(len(data) * (fs / og_fs))  # og_fs = 24000 is the original fs in the provided code
    data = np.interp(np.linspace(0, len(data), target_length), np.arange(len(data)), data)
    return data

def embed_watermark(input_wav, output_wav, watermark_signal, watermark_channel=1, watermark_strength=0.1):
    """
    watermark_channel 0 = left
    watermark_channel 1 = right
    """

    # Load the input WAV file
    fs, audio = wavfile.read(input_wav) #fs = Sample rate of WAV file.

    # ensure the audio is stereo, if not then have the same audio track go to both
    if len(audio.shape) == 1:
        print("Audio is mono, converting to stereo")
        audio = np.column_stack((audio, audio))

    # Adjust watermark length to match audio length
    if len(watermark_signal) > len(audio):
        print("Warning: Watermark length is longer than audio length. Padding with zeros.")
        watermark_signal = watermark_signal[:len(audio)]
    else:

        watermark_signal = np.pad(watermark_signal, (0, len(audio) - len(watermark_signal)))

    # Embed the watermark in the specified channel from start
    audio[:, watermark_channel] = audio[:, watermark_channel] + (watermark_signal * watermark_strength).astype(np.int16)
    wavfile.write(output_wav, original_fs, audio)     # Save the watermarked audio
    return audio

"""Now we can save the new output"""

import time # filename { run: "auto" }
print("Processing the audio and image...")

original_fs, original_audio = wavfile.read(original_audio_path) #fs = Sample rate of WAV file.
print(f"Sampling rate {original_fs}")

watermark_signal = create_watermark_signal(image_data, 24000)
output_wav = 'outputs/watermarked_output{}.wav'.format(str(int(time.time()))[-5:])
watermarked_audio = embed_watermark(original_audio_path, output_wav,watermark_signal, watermark_channel,watermark_strength)

# make a 30 second one first
watermarked_audio = watermarked_audio[:original_fs * 30]
# save that and then if i like it, ill wait for the full
short_output_wav = 'outputs/short_watermarked_output{}.wav'.format(str(int(time.time()))[-5:])
print(f"short Watermarked audio saved as {short_output_wav}")

wavfile.write(short_output_wav, original_fs, watermarked_audio)
files.download(short_output_wav)

print(f"Watermarked audio saved as {output_wav}")

files.download(output_wav)

"""#Spectrogram and other Graphs"""

# plots
from scipy.signal import spectrogram # for graphs


def plot_spectrogram(audio_data, sample_rate, title="Spectrogram", duration=None):
  """
  Plots the spectrogram of the provided audio data.

  Args:
      audio_data: The audio data as a NumPy array.
      sample_rate: The sample rate of the audio data.
      title: The title for the spectrogram plot (default: "Spectrogram").
  """
  frequencies, times, Sxx = spectrogram(audio_data, sample_rate, nperseg=1024)
  Sxx_dB = 10 * np.log10(Sxx) # decibels are on the logarithmic scale

  plt.figure(figsize=(10, 6))
  plt.pcolormesh(times, frequencies, Sxx_dB, shading='gouraud', cmap='inferno')
  plt.ylabel('Hz')
  plt.xlabel('Time [sec]')
  plt.colorbar(label='Intensity [dB]')
  plt.tight_layout()

  plt.title(title)
  plt.show()


def channels(audio_data):
  if len(audio_data.shape) == 2:   # Check if stereo and plot accordingly
    left_channel, right_channel = audio_data.T
    plot_spectrogram(left_channel, original_fs, title="Left Channel Spectrogram")
    plot_spectrogram(right_channel, original_fs, title="Right Channel Spectrogram")
  else:
    plot_spectrogram(audio_data, original_fs)

# Extract the first 10 seconds of audio data
num_samples_10sec = original_fs * 10
first_10sec_audio_og = original_audio[:num_samples_10sec]
first_10sec_audio_watermarked = watermarked_audio[:num_samples_10sec]
# Load the WAV file
original_fs, original_audio = wavfile.read(original_audio_path) #fs = Sample rate of WAV file.
print("original")
channels(first_10sec_audio_og)
print("watermarked")
channels(first_10sec_audio_watermarked)

def plot_waveform(original_audio, watermarked_audio, fs):
    """
    This won't reveal the watermark but is kinda cool to see if you dont have audio editing software
    """
    fig, axs = plt.subplots(2, 1, figsize=(12, 20))
    # Plot waveforms
    axs[0].plot(original_audio[:, 0], label='Original Ch0')
    axs[0].plot(original_audio[:, 1], label='Original Ch1')
    axs[0].set_title('Original Audio Waveform')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Hz')
    axs[0].legend()

    axs[1].plot(watermarked_audio[:, 0], label='Watermarked Ch0')
    axs[1].plot(watermarked_audio[:, 1], label='Watermarked Ch1')
    axs[1].set_title('Watermarked Audio Waveform')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Hz')
    axs[1].legend()

    plt.tight_layout()
    plt.show()

plot_waveform(original_audio, watermarked_audio, original_fs)