# VisionAid

An AI-powered scene description tool for visually impaired users. Point a phone camera at the surroundings, and VisionAid describes what is ahead — out loud.

## How it works

1. Capture a frame from the device's rear camera
2. Validate the frame, then send it to a multimodal LLM (Google Gemini 2.5 Flash) with a prompt asking for a short, hazard-focused description
3. Read the description aloud via text-to-speech

## Features

- **Audio-first output** — the description is spoken automatically, with a large replay button as a fallback for browsers that block autoplay
- **Invalid-frame gate** — before calling the model, the frame is converted to grayscale and its mean brightness checked. Images that are too dark or likely blocked by a finger (mean brightness < 15) are rejected with a retake prompt, avoiding a wasted API call
- **Change-aware descriptions** — the previous description is carried into the next prompt, so when a user keeps scanning the same scene the model reports what *changed* (an object approaching, an obstacle moving) rather than repeating itself
- **Double-tap guard** — a 5-second cooldown between accepted frames, so an accidental double tap does not fire two model calls
- **High-contrast UI** — dark background with a high-contrast result card, sized for low-vision readability
- **Status indicator** — an animated indicator while the model is processing, so the user knows the app is working

## Tech stack

| Layer                | Choice                                          |
| -------------------- | ----------------------------------------------- |
| UI                   | Streamlit                                       |
| Vision & description | Google Gemini 2.5 Flash (`google-generativeai`) |
| Image handling       | Pillow                                          |
| Speech               | gTTS                                            |
| Camera input         | streamlit-back-camera-input                     |

## Running locally

```bash
pip install -r requirements.txt
```

Add your Gemini API key to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

Then start the app:

```bash
streamlit run app.py
```

> Designed for mobile use — open it in a phone browser and grant camera access.

## Notes

The interface and the model prompt are in Chinese: the tool was built for Chinese-speaking users, and the descriptions are deliberately kept under 50 characters so they can be absorbed in one spoken sentence.

This is a personal project exploring how a multimodal model can be wired into an accessibility-oriented interface, not a production product. It has been tested on a small number of devices and has no offline fallback if the model call fails.

<!-- TODO: add a screenshot -->
