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


# Initialize the OpenAI API key
openai.api_key = "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"

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
        chat_transcript = transcribe(self.audio_path)
        self.signals.result.emit(chat_transcript)

def transcribe(audio_path):
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
        chat_transcript = generate_note(self.transcript)
        self.signals.result.emit(chat_transcript)

def generate_note(transcript):
    global messages

    # Send the plain text version to the API
    structured_prompt = """
Please summarize the following medical transcription using the structured format below:

- Presenting Complaint (PC): Briefly describe the main reason for the consultation.
- History of Presenting Complaint (HPC): Detail the symptoms, their duration, and any treatments tried.
- Past Medical History (PMHx): List any relevant medical history.
- Drug History (DHx): Note any medications the patient is currently taking or has taken recently.
- Family History (FHx): Indicate any relevant family medical history.
- Social History (SHx): Describe lifestyle factors like smoking, alcohol use, etc.
- Systems Review (SR): Review other systems that might be relevant.
- Ideas, Concerns, Expectations (ICE): Outline what the patient thinks is going on, any concerns they have, and what they expect from the treatment.

Transcript: {}
    """.format(transcript)

    new_message = {
        "role": "user",
        "content": structured_prompt
    }
    updated_messages = messages + [new_message]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=updated_messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript



class TranscribeThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def run(self):
        chat_transcript = transcribe(self.audio_path)
        self.result.emit(chat_transcript)

class RecordAudioThread(QThread):
    finished = pyqtSignal(str)
    response_received = pyqtSignal(str)
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
          # Create an instance of RecordAudioThread
        self.record_audio_thread = RecordAudioThread()
        self.record_audio_thread.finished.connect(self.on_audio_recorded)
        self.record_audio_thread.error_occurred.connect(self.on_error_occurred)


        self.initUI()

    def initUI(self):
        #window icon
        self.setWindowIcon(QIcon('H.png'))
        #fixed size
        self.setFixedSize(250, 500)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        image = Image.open("H.png")
        image.save("H.png")
        logo = QPixmap('H.png').scaled(60, 60)
        logo_label = QLabel('H.png')
        logo_label.setPixmap(logo)
        
        layout = QVBoxLayout()
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor("#0e2433"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout.addWidget(logo_label)
        #centre logo
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Replace QPlainTextEdit with QTextEdit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        

         # Create a menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Add 'Settings' to File menu
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)

        # Add 'About' to File menu
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        file_menu.addAction(about_action)

        # Add 'Feedback' to File menu
        feedback_action = QAction('Feedback', self)
        feedback_action.triggered.connect(self.show_feedback_dialog)
        file_menu.addAction(feedback_action)

        button_layout = QHBoxLayout()

        self.record_button = QToolButton(self)
        self.record_button.setAutoRaise(True)
        self.record_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.record_button.setToolTip("<span style='color: black;'>Record</span>")
        self.record_button.setIcon(QIcon("record-on.png"))  # Add your record icon here
        self.record_button.setIconSize(QSize(24, 24))
        self.record_button.setFixedSize(30, 30)
        self.record_button.clicked.connect(self.record_audio)
        button_layout.addWidget(self.record_button)

        self.stop_button = QToolButton(self)
        self.stop_button.setAutoRaise(True)
        self.stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_button.setToolTip("<span style='color: black;'>Stop</span>")
        self.stop_button.setIcon(QIcon("noteclose.png"))  # Add your stop icon here
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.setFixedSize(30, 30)
        self.stop_button.clicked.connect(self.stop_audio)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QToolButton(self)
        self.clear_button.setAutoRaise(True)
        self.clear_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_button.setToolTip("<span style='color: black;'>Clear</span>")
        self.clear_button.setIcon(QIcon("clear-icon.png"))  # Add your clear icon here
        self.clear_button.setIconSize(QSize(24, 24))
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)
        
        self.generate_note_button = QToolButton(self)
        self.generate_note_button.setAutoRaise(True)
        self.generate_note_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.generate_note_button.setToolTip("<span style='color: black;'>Generate Note</span>")
        self.generate_note_button.setIcon(QIcon("listen-icon.png"))  # Add your generate note icon here
        self.generate_note_button.setIconSize(QSize(24, 24))
        self.generate_note_button.setFixedSize(30, 30)
        self.generate_note_button.clicked.connect(self.generate_note)
        button_layout.addWidget(self.generate_note_button)

        # Add Copy button
        self.copy_button = QToolButton(self)
        self.copy_button.setAutoRaise(True)
        self.copy_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.copy_button.setToolTip("<span style='color: black;'>Copy</span>")
        self.copy_button.setIcon(QIcon("chatbox.png"))  # Add your copy icon here
        self.copy_button.setIconSize(QSize(24, 24))
        self.copy_button.setFixedSize(30, 30)
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)

        layout.addLayout(button_layout)
        

        
        
        common_stylesheet = """
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
        self.record_button.setStyleSheet(common_stylesheet)
        self.stop_button.setStyleSheet(common_stylesheet)
        self.clear_button.setStyleSheet(common_stylesheet)
        self.generate_note_button.setStyleSheet(common_stylesheet)
        self.copy_button.setStyleSheet(common_stylesheet)
        
        central_widget.setLayout(layout)
    
    def on_error_occurred(self, error_message):
        self.record_button.setText(f"Error: {error_message}")
        self.record_button.setEnabled(True)
           
    def show_settings_dialog(self):
        dialog = SettingsDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            selected_source = dialog.source_combo.currentText()
            selected_mic = dialog.mic_combo.currentText()
            
            # Handle the selected source and microphone (not implemented)
            print(f"Selected source: {selected_source}")
            print(f"Selected microphone: {selected_mic}")

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "This is an example PyQt5 application.")

    def show_feedback_dialog(self):
        text, ok = QInputDialog.getText(self, "Feedback", "Enter your feedback:")
        if ok:
            # Handle the feedback (not implemented)
            pass

    def copy_text(self):
        global messages  # Make sure you have access to the global 'messages' list
        assistant_text = ""
        for message in messages:
            if message['role'] == 'assistant':
                assistant_text += message['content'] + "\n\n"
        clipboard = QApplication.clipboard()
        clipboard.setText(assistant_text)

        
    def clear_text(self):
        global messages  # Declare messages as global to access and modify it
        self.text_edit.clear()  # Clear the QPlainTextEdit widget
        self.transcript = ""  # Clear the transcript string
        messages = [{"role": "system", "content": 'You are an assistant called Health Assist, you help with administrative tasks.'}]  # Reset the messages list to the initial message


        

    
    def on_audio_recorded(self, audio_path):
        self.text_edit.append("<b>Transcription being processed...</b>")
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Assuming you've defined TranscribeThread and its signals elsewhere
        self.transcribe_thread = TranscribeThread(audio_path)
        self.transcribe_thread.result.connect(self.on_transcription_complete)
        self.transcribe_thread.start()

    def on_transcription_complete(self, chat_transcript):
        self.transcript += chat_transcript + "<br><br>"

        # Apply formatting when appending the text to QTextEdit
        formatted_chat_transcript = chat_transcript.replace("Presenting Complaint (PC):", "<b>Presenting Complaint (PC):</b>") \
                                                  .replace("History of Presenting Complaint (HPC):", "<b>History of Presenting Complaint (HPC):</b>") \
                                                  .replace("Past Medical History (PMHx):", "<b>Past Medical History (PMHx):</b>") \
                                                  .replace("Drug History (DHx):", "<b>Drug History (DHx):</b>") \
                                                  .replace("Family History (FHx):", "<b>Family History (FHx):</b>") \
                                                  .replace("Social History (SHx):", "<b>Social History (SHx):</b>") \
                                                  .replace("Systems Review (SR):", "<b>Systems Review (SR):</b>") \
                                                  .replace("Ideas, Concerns, Expectations (ICE):", "<b>Ideas, Concerns, Expectations (ICE):</b>")

        self.text_edit.append(formatted_chat_transcript)


    def generate_note(self):
        self.text_edit.append("<b>Generating clinic note...</b>")
        worker = GenerateNoteWorker(self.transcript)
        worker.signals.result.connect(self.on_transcription_complete)
        self.threadpool.start(worker)

    def record_audio(self):
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        #message in the message Qplaintextedit
        self.text_edit.append("<b>Transcription started...</b>")
        
        self.record_audio_thread.running = True
        self.record_audio_thread.start()

    def stop_audio(self):
        self.record_audio_thread.stop()
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.text_edit.append("<b>Transcription ended...</b>")
        self.record_button.setEnabled(True)


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        
        # Load saved settings
        self.settings = QSettings("YourCompany", "YourApp")
        saved_source = self.settings.value("source", "Microphone")
        saved_mic = self.settings.value("mic", "Default")
        saved_volume = int(self.settings.value("volume", 50))

        self.source_label = QLabel("Select Recording Input:")
        self.source_combo = QComboBox()
        self.source_combo.addItem("Microphone")
        self.source_combo.addItem("System Sound")
        self.source_combo.setCurrentText(saved_source)
        layout.addWidget(self.source_label)
        layout.addWidget(self.source_combo)

        self.mic_label = QLabel("Select Microphone:")
        self.mic_combo = QComboBox()

        # Retrieve and add available microphones
        available_mics = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)
        for mic in available_mics:
            self.mic_combo.addItem(mic.deviceName())
        
        self.mic_combo.setCurrentText(saved_mic)
        layout.addWidget(self.mic_label)
        layout.addWidget(self.mic_combo)

        self.volume_label = QLabel(f"Volume: {saved_volume}")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(saved_volume)
        self.volume_slider.valueChanged.connect(lambda: self.volume_label.setText(f"Volume: {self.volume_slider.value()}"))
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)

        self.test_button = QPushButton("Test Settings")
        self.test_button.clicked.connect(self.test_settings)
        layout.addWidget(self.test_button)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.save_settings)
        layout.addWidget(self.ok_button)
        self.source_combo.currentIndexChanged.connect(self.source_changed)
        self.setLayout(layout)

    def save_settings(self):
        self.settings.setValue("source", self.source_combo.currentText())
        self.settings.setValue("mic", self.mic_combo.currentText())
        self.settings.setValue("volume", self.volume_slider.value())
        self.accept()
        
    def source_changed(self):
        if self.source_combo.currentText() == "System Sound":
            QMessageBox.information(self, "System Sound Selected", "Please manually set your system's recording device to 'Stereo Mix' (Windows) or use a virtual audio driver like Soundflower (Mac) to capture system sound.")


    def test_settings(self):
        selected_mic = self.mic_combo.currentText()
        volume = self.volume_slider.value() / 100  # Assuming the slider is from 0 to 100
        duration = 3  # seconds

        # Assuming the sample rate is 44100 and the audio is mono
        sample_rate = 44100
        audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        # Adjust the volume
        audio_data = audio_data * volume

        # Calculate RMS
        rms = np.sqrt(np.mean(np.square(audio_data)))
        
        # Show a message box with the calculated RMS. The closer RMS is to 0, the quieter the sound.
        QMessageBox.information(self, "Test Result", f"Audio RMS level: {rms}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())