
# Health Assist Transcription App

**Health Assist** is an open source medical transcription application that uses AI to generate structured clinical notes from audio recordings.

The app provides an easy way for healthcare professionals to convert audio from patient encounters into text and formatted medical notes, saving time and increasing efficiency.

## How it Works

- The app provides buttons to record audio from a microphone or system audio source.
- After recording the audio, clicking the "Transcribe" button will use the **Whisper AI** engine to convert speech to text.
- Then clicking "Generate Note" will pass the plain text transcript to the **GPT-3 API**, which will format it into a structured clinical note with sections like _Past Medical History_ and _Medications_.
- The formatted note can then be copied from the app and pasted into the patient's electronic medical record.

## Features

- Simple user interface with buttons to record, transcribe, and generate notes
- Integration with **Whisper** for accurate speech-to-text
- **GPT-3 API** generates notes with relevant sections and headings
- Notes can be easily copied and exported for documentation
- Open source codebase can be customized as needed
- Settings allow configuring audio source, microphone, etc.

## Requirements

- Python 3
- PyQt5 for the desktop app framework
- API keys for Whisper and OpenAI GPT-3 models

## FAQ

**Is this app HIPAA compliant for protected health information?**
No, this open source app does not meet HIPAA compliance standards out of the box. For use with patient data, proper security, access control, and compliance features would need to be implemented.

**What AI models are used?**
Whisper is used for speech-to-text and GPT-3 is used for generating the clinical note text.

**Can I use my own audio data to train the AI?**
No, the app uses the pretrained Whisper and GPT-3 models without any ability to customize or re-train them.

**How accurate is the generated transcription and notes?**
Accuracy will depend on audio quality and speaking clarity. The AI models are not 100% perfect, so some manual review is recommended.

**Can I integrate this with my clinic's EMR system?**
Not directly, but the generated notes can be copied/pasted into any text field in an EMR. Some development would be required to build a direct integration.

**Is there a cloud version, or is it local-only?**
Currently it is only a local desktop application, not deployed as a cloud service. It could be extended to a web version.

**What licensing applies and can I use this commercially?**
It is open source under GPLv3 license. For commercial use, please contact the project authors for commercial licensing.
