# Steganography
PHC-303 course project on Audio steganography 

An implementation and evaluation of multiple steganography techniques for digital audio signals, focusing on trade-offs between capacity, imperceptibility, and robustness. The project allows hiding text, audio, or image payloads in audio files using LSB, DCT, and phase coding methods, and provides a framework for testing resilience against signal attacks.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Methodology](#methodology)
- [Performance Evaluation](#performance-evaluation)
- [Acknowledgments](#acknowledgments)

---

## Features

- Simple LSB (Least Significant Bit) steganography for both 1-bit and 2-bit embedding.
- Frequency-domain DCT (Discrete Cosine Transform) method for robust hiding.
- Phase coding technique using FFT for imperceptible data embedding.
- Support for hiding text, image, and audio payloads.
- Robustness analysis framework to test data hiding methods against compression, noise, and filtering.

---

## Project Structure

```
.
├── scriptimage.py              # Text-in-image LSB embedding
├── scriptimg2img.py            # Image-in-image LSB embedding
├── scriptaudio2audio.py        # Audio-in-audio LSB embedding
├── scriptimg2audio.py          # Image-in-audio LSB embedding
├── scriptimg2audio2b.py        # Enhanced 2-bit LSB for audio
├── scriptdcttxt2audio.py       # DCT-based text-in-audio embedding
├── dctidctalgo.py              # Manual/reference DCT/IDCT implementation
├── scriptphasecoding.py        # Phase coding with FFT for text embedding in audio
├── createaudio.py              # WAV audio file generator (testing utility)
├── subtractimage.py            # Visual difference maps for image analysis
├── imagecompress.py            # Image pre-processing utility
├── robustanalysis.py           # Framework for robustness evaluation (attacks, BER)
└── README.md                   # This file
```

---

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/audio-steganography-project.git
   cd audio-steganography-project
   ```

2. Make sure you have Python (>=3.7) and these dependencies:
   - numpy
   - scipy
   - Pillow (PIL)
   - scikit-image (for noise/blur)
   - pydub (for audio conversion)
   
   Install all requirements:
   ```
   pip install -r requirements.txt
   ```

---

## Usage

### 1. LSB Methods

- **Text in Image:**  
  ```
  python scriptimage.py --carrier cover_image.png --payload secret.txt --output stego_image.png
  ```

- **Image in Image:**  
  ```
  python scriptimg2img.py --carrier cover_image.png --payload secret_image.png --output stego_image.png
  ```

- **Audio in Audio (1-bit/2-bit):**  
  ```
  python scriptaudio2audio.py --carrier cover.wav --payload secret.wav --output stego.wav
  python scriptimg2audio2b.py --carrier cover.wav --payload secret.txt --output stego.wav
  ```

### 2. DCT Method

- **Text in Audio using DCT:**  
  ```
  python scriptdcttxt2audio.py --carrier cover.wav --payload secret.txt --output stego_dct.wav
  ```

### 3. Phase Coding

- **Text in Audio using FFT-based Phase Coding:**  
  ```
  python scriptphasecoding.py --carrier cover.wav --payload secret.txt --output stego_phase.wav
  ```

### 4. Supporting Utilities

- **Generate sample audio:**  
  ```
  python createaudio.py --length 10 --output test.wav
  ```

- **Compress images:**  
  ```
  python imagecompress.py --input large_image.png --output compressed.png --quality 70
  ```

- **Visual difference maps:**  
  ```
  python subtractimage.py --original cover.png --stego stego.png --output diff.png
  ```

### 5. Robustness Analysis

- Apply robustness attacks and compute BER:
  ```
  python robustanalysis.py --input stego.wav --attack noise --level 0.02 --output attacked.wav
  python robustanalysis.py --input stego.wav --attack lowpass --cutoff 3000 --output filtered.wav
  python robustanalysis.py --input stego.wav --attack mp3 --bitrate 96 --output mp3_reconverted.wav
  ```

---

## Methodology

For full details on the algorithms and implementation rationale, see `steganography_report_full.pdf`.

- **LSB**: Directly modifies LSB(s) of carrier samples (audio/image) to store payload data. Header stores payload length for reliable extraction.
- **DCT**: Embeds bits by quantizing and adjusting the parity of mid-frequency DCT coefficients. Robust to precision loss and most attacks.
- **Phase Coding**: Modifies phase of selected FFT bins in audio frames. Human auditory perception makes phase changes less detectable.

---

## Performance Evaluation

- Use the `robustanalysis.py` framework to apply attacks and measure Bit Error Rate (BER) for embedded and extracted payloads.
- Capacity, imperceptibility, and robustness data are provided in the project report for comparison between methods.
