
# Health R - Medical Transcription App 🩺

Health R is an open-source medical transcription app that uses AI to generate structured clinical notes from audio recordings.

![Project Logo](link_to_logo_image)

An open-source medical transcription app that uses AI to generate structured clinical notes from audio recordings.

## Table of Contents
- [Features](#features)
- [Usage](#usage)
- [AI Models Used](#ai-models-used)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Requirements](#requirements)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Contributing](#contributing)
- [Credits](#credits)


## 💊 Features
- 🎤 **Record Audio**: Capture audio from your microphone or system audio.
- 🤖 **AI Transcription**: Convert your recordings into text using Whisper AI.
- 📄 **Generate Clinical Notes**: Structure your transcribed text into clinical note sections (HPI, PMH, etc.) using GPT-3.
- 📋 **Export Notes**: Easily export and share your generated notes.
- ⚙️ **Configurable Settings**: Customize audio sources, microphone selection, volume levels, and more.

## 👩‍⚕️ Usage
### 🎙 Recording Audio
1. Click the record button to start capturing audio.
2. Click stop to end the recording.
3. AI will automatically transcribe the audio to text.

### 📝 Generating Notes
1. Once the audio is transcribed, click the "generate note" button.
2. LLM will structure the text into clinical note sections.
3. Formatted note sections will appear in a text area.

### 📎 Exporting Notes
1. Click the copy button to copy the generated note to the clipboard.
2. Paste it into any app or platform to save and share the note.

## 🤖 AI Models Used
- **Whisper**: For speech-to-text functionality.
- **GPT-3**: For text content generation and structuring.

## 💻 Requirements
- Python 3
- PyQt5 for GUI
- Whisper API for transcription
- OpenAI API key for GPT-3


## 🤖 AI Models Used
- Whisper - speech-to-text
- GPT-3 - text content generation

## ⚙️ Configuration
> Insert images or GIFs here to demonstrate configuration steps

Settings allow configuring:
- Audio input source
- Microphone selection
- Volume level
- Other app settings

## 🛣️ Roadmap
> A list or graphical representation of future features, improvements, and bug fixes.

- [ ] Feature 1
- [x] Feature 2 (completed)
- [ ] Bug fix 1

## 💻 Requirements
- Python 3
- PyQt5
  - QtCore
  - QtWidgets
  - QtGui
  - QtMultimedia
- openai
- numpy
- sounddevice
- soundfile
- sys
- PIL (Python Imaging Library)

## 🩺 Disclaimer
Health Assist is not intended for diagnostic use. Please consult a qualified healthcare provider for any medical advice.

<!-- LICENSE -->

## License

Distributed under the [AGPLv3 License](https://www.gnu.org/licenses/agpl-3.0.en.html). See `LICENSE` for more information.

. For commercial licensing, please contact.


## 🙌 Contributing

We welcome contributions to improve Health Assist! If you find any bugs or have suggestions for new features, please feel free to submit a pull request.

## 🌟 Credits
- **openai** for their incredible models and API.




