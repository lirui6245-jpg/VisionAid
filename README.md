# VisionAid

An AI-powered scene description tool for visually impaired users. Point a phone camera at the surroundings, and VisionAid describes what is ahead — out loud.

## How it works

1. Capture a frame from the device's rear camera
2. Send the frame to a multimodal LLM (Google Gemini 2.5 Flash) with a prompt asking for a short, hazard-focused description
3. Read the description aloud via text-to-speech

## Features

- **Audio-first output** — the description is spoken automatically, with a large replay button as a fallback for browsers that block autoplay
- **Invalid-frame gate** — before calling the model, the frame is converted to grayscale and its mean brightness checked. Images that are too dark or likely blocked by a finger (mean brightness < 15) are rejected with a retake prompt, avoiding a wasted API call
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

This is an independent learning project exploring how a multimodal model can be wired into an accessibility-oriented interface. It is not a production product.

## Screenshot
