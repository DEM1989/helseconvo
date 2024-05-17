from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QThread
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPlainTextEdit, QToolButton, QHBoxLayout, QApplication
from PyQt5.QtGui import QPalette, QColor, QIcon, QCursor, QPixmap
from PyQt5.QtCore import Qt, QSize
import openai
import numpy as np
import sounddevice as sd
import soundfile as sf
import sys
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QInputDialog, QMessageBox, QFileDialog, QTextEdit
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QSlider, QCheckBox
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap, QIcon, QFont, QPalette, QMovie, QCursor
from PyQt5.QtCore import QRunnable, pyqtSignal
from PIL import Image


from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QThread, Qt, QSettings
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTextEdit, QToolButton, QHBoxLayout, QApplication, QMenuBar, QAction, 
    QInputDialog, QMessageBox, QDialog, QLabel, QComboBox, QPushButton, QSlider
)
from PyQt5.QtGui import QPalette, QColor, QIcon, QCursor, QPixmap, QFont
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio
import openai
import numpy as np
import sounddevice as sd
import soundfile as sf
import sys
from PIL import Image
import os

# Initialize OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initial message
messages = [{"role": "system", "content": 'You are an assistant called Health Assist, you help with administrative tasks.'}]

class TranscribeSignals(QObject):
    result = pyqtSignal(str)

class TranscribeWorker(QRunnable):
    def __init__(self, audio_path):
        super(TranscribeWorker, self).__init__()
        self.audio_path = audio_path
        self.signals = TranscribeSignals()

    @pyqtSlot()
    def run(self):
        chat_transcript = self.transcribe(self.audio_path)
        self.signals.result.emit(chat_transcript)

    def transcribe(self, audio_path):
        global messages
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        messages.append({"role": "user", "content": transcript["text"]})
        return transcript["text"]

class GenerateNoteWorker(QRunnable):
    def __init__(self, transcript):
        super(GenerateNoteWorker, self).__init__()
        self.transcript = transcript
        self.signals = TranscribeSignals()

    @pyqtSlot()
    def run(self):
        chat_transcript = self.generate_note(self.transcript)
        self.signals.result.emit(chat_transcript)

    def generate_note(self, transcript):
        global messages
        structured_prompt = f"""
Please summarize the following medical transcription using the structured format below:

- Presenting Complaint (PC): Briefly describe the main reason for the consultation.
- History of Presenting Complaint (HPC): Detail the symptoms, their duration, and any treatments tried.
- Past Medical History (PMHx): List any relevant medical history.
- Drug History (DHx): Note any medications the patient is currently taking or has taken recently.
- Family History (FHx): Indicate any relevant family medical history.
- Social History (SHx): Describe lifestyle factors like smoking, alcohol use, etc.
- Systems Review (SR): Review other systems that might be relevant.
- Ideas, Concerns, Expectations (ICE): Outline what the patient thinks is going on, any concerns they have, and what they expect from the treatment.

Transcript: {transcript}
        """
        new_message = {"role": "user", "content": structured_prompt}
        updated_messages = messages + [new_message]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=updated_messages)
        system_message = response["choices"][0]["message"]
        messages.append(system_message)
        chat_transcript = "\n\n".join(f"{msg['role']}: {msg['content']}" for msg in messages if msg['role'] != 'system')
        return chat_transcript

class RecordAudioThread(QThread):
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        try:
            duration = 1800  # seconds
            sample_rate = 16000
            audio_path = "recorded_audio.wav"
            recorded_audio = []
            with sd.InputStream(samplerate=sample_rate, channels=1) as stream:
                for _ in range(int(duration * sample_rate // 1024)):
                    if not self.running:
                        break
                    audio_chunk, _ = stream.read(1024)
                    recorded_audio.append(audio_chunk)
            recorded_audio = np.concatenate(recorded_audio, axis=0)
            with sf.SoundFile(audio_path, mode='w', samplerate=sample_rate, channels=1) as file:
                file.write(recorded_audio)
            self.finished.emit(audio_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.transcript = ""
        self.record_audio_thread = RecordAudioThread()
        self.record_audio_thread.finished.connect(self.on_audio_recorded)
        self.record_audio_thread.error_occurred.connect(self.on_error_occurred)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('H.png'))
        self.setFixedSize(250, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        image = Image.open("H.png")
        image.save("H.png")
        logo = QPixmap('H.png').scaled(60, 60)
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        layout = QVBoxLayout()
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#0e2433"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        layout.addWidget(logo_label)
        logo_label.setAlignment(Qt.AlignCenter)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.create_menu_bar()
        self.create_buttons(layout)
        central_widget.setLayout(layout)

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        file_menu.addAction(about_action)
        feedback_action = QAction('Feedback', self)
        feedback_action.triggered.connect(self.show_feedback_dialog)
        file_menu.addAction(feedback_action)

    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        buttons = [
            ('record-on.png', 'Record', self.record_audio),
            ('noteclose.png', 'Stop', self.stop_audio),
            ('clear-icon.png', 'Clear', self.clear_text),
            ('listen-icon.png', 'Generate Note', self.generate_note),
            ('chatbox.png', 'Copy', self.copy_text)
        ]
        for icon, tooltip, callback in buttons:
            button = QToolButton(self)
            button.setAutoRaise(True)
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setToolTip(f"<span style='color: black;'>{tooltip}</span>")
            button.setIcon(QIcon(icon))
            button.setIconSize(QSize(24, 24))
            button.setFixedSize(30, 30)
            button.clicked.connect(callback)
            button.setStyleSheet(self.get_button_stylesheet())
            button_layout.addWidget(button)
        layout.addLayout(button_layout)

    def get_button_stylesheet(self):
        return """
            QToolButton {
                background-color: #F0F0F0;
                border: 2px solid #8f8f91;
                border-radius: 15px;
            }
            QToolButton:hover {
                border: 2px solid #3daaeb;
            }
            QToolButton:pressed {
                background-color: #F0F0F0;
            }
        """

    def show_settings_dialog(self):
        dialog = SettingsDialog()
        if dialog.exec_() == QDialog.Accepted:
            selected_source = dialog.source_combo.currentText()
            selected_mic = dialog.mic_combo.currentText()
            print(f"Selected source: {selected_source}")
            print(f"Selected microphone: {selected_mic}")

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "This is an example PyQt5 application.")

    def show_feedback_dialog(self):
        text, ok = QInputDialog.getText(self, "Feedback", "Enter your feedback:")
        if ok:
            print(f"Feedback: {text}")

    def copy_text(self):
        assistant_text = "\n\n".join(msg['content'] for msg in messages if msg['role'] == 'assistant')
        QApplication.clipboard().setText(assistant_text)

    def on_audio_recorded(self, audio_path):
        transcribe_worker = TranscribeWorker(audio_path)
        transcribe_worker.signals.result.connect(self.display_transcription)
        self.threadpool.start(transcribe_worker)

    def on_error_occurred(self, error_message):
        print(f"Error: {error_message}")

    def display_transcription(self, text):
        self.transcript = text
        self.text_edit.append(f"User: {text}")

    def record_audio(self):
        self.text_edit.append("Recording audio...")
        self.record_audio_thread.start()

    def stop_audio(self):
        self.record_audio_thread.stop()
        self.text_edit.append("Audio recording stopped.")

    def clear_text(self):
        self.text_edit.clear()

    def generate_note(self):
        generate_note_worker = GenerateNoteWorker(self.transcript)
        generate_note_worker.signals.result.connect(self.display_generated_note)
        self.threadpool.start(generate_note_worker)

    def display_generated_note(self, note):
        self.text_edit.append(note)

class SettingsDialog(QDialog):
    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()
        self.source_combo = QComboBox()
        self.mic_combo = QComboBox()
        layout.addWidget(QLabel("Select Audio Source:"))
        layout.addWidget(self.source_combo)
        layout.addWidget(QLabel("Select Microphone:"))
        layout.addWidget(self.mic_combo)
        for device in QAudioDeviceInfo.availableDevices(QAudio.AudioInput):
            self.source_combo.addItem(device.deviceName())
            self.mic_combo.addItem(device.deviceName())
        self.source_combo.currentIndexChanged.connect(self.update_microphone_combo)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        layout.addWidget(QLabel("Microphone Volume:"))
        layout.addWidget(self.slider)
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)
        self.setLayout(layout)

    def update_microphone_combo(self):
        selected_source = self.source_combo.currentText()
        self.mic_combo.clear()
        for device in QAudioDeviceInfo.availableDevices(QAudio.AudioInput):
            if device.deviceName() == selected_source:
                self.mic_combo.addItem(device.deviceName())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
