import sys, os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, Slot, QUrl, QTimer
from PySide6.QtGui import QPixmap, QPixmapCache
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class Player(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Media widgets
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_pixmap = None

        self.video_widget = QVideoWidget()
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # Layout
        self.layout = QStackedLayout()
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.video_widget)
        self.layout.setCurrentWidget(self.image_label)

        self.setLayout(self.layout)
    
    def play_image(self, path):
        if QPixmapCache.find(path):
            self.original_pixmap = QPixmapCache.find(path)
        else:
            self.original_pixmap = QPixmap(path)
            QPixmapCache.insert(path, self.original_pixmap)
        self.update_image()

        self.layout.setCurrentWidget(self.image_label)
        self.media_player.stop()
        self.media_player.setSource(QUrl())  # Clear media source
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
    
    def update_image(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.image_label.setPixmap(self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def play_video(self, path):
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.pause()
    
    def media_status_changed(self):
        if self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.BufferedMedia:
            self.media_player.play()
            self.layout.setCurrentWidget(self.video_widget)
            self.media_player.mediaStatusChanged.disconnect(self.media_status_changed)
    
    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)
    
    def closeEvent(self, event):
        event.accept()
        QApplication.quit()


class Console(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.queue = []
        self.current_index = -1

        # Buttons
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.load_btn = QPushButton("Load")
        self.fullscreen_btn = QPushButton("Toggle Fullscreen")

        self.prev_btn.setDisabled(True)
        self.next_btn.setDisabled(True)

        self.prev_btn.clicked.connect(lambda: self.change_slide(-1))
        self.next_btn.clicked.connect(lambda: self.change_slide(1))
        self.load_btn.clicked.connect(self.load_queue)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        # List view
        self.list_view = QListWidget()
        self.list_view.itemClicked.connect(lambda item: self.item_clicked(item))

        # Layouts
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.prev_btn)
        top_row_layout.addWidget(self.next_btn)
        top_row_layout.setSpacing(40)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(self.load_btn)
        bottom_row_layout.addWidget(self.fullscreen_btn)
        bottom_row_layout.setSpacing(40)

        layout = QVBoxLayout()
        layout.addLayout(top_row_layout)
        layout.addWidget(self.list_view)
        layout.addLayout(bottom_row_layout)
        layout.setSpacing(40)
        layout.setContentsMargins(30, 30, 30, 30)

        self.setLayout(layout)
    
    @Slot(QListWidgetItem)
    def item_clicked(self, item):
        self.current_index = self.list_view.row(item)
        self.change_slide(0)

    @Slot(int)
    def change_slide(self, step):
        # Update current index
        self.current_index = (self.current_index + step) % len(self.queue)
        self.list_view.setCurrentRow(self.current_index)

        # Update button states
        if self.current_index == 0:
            self.prev_btn.setDisabled(True)
        else:
            self.prev_btn.setDisabled(False)

        if self.current_index == len(self.queue) - 1:
            self.next_btn.setDisabled(True)
        else:
            self.next_btn.setDisabled(False)

        self.play_current()
    
    def play_current(self):
        current_file = self.queue[self.current_index]
        
        # Check if image or video
        if current_file.endswith(".jpg") or current_file.endswith(".png"):
            player_window.play_image(current_file)
        elif current_file.endswith(".mp4"):
            player_window.play_video(current_file)

    def load_queue(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt)")
        if not file_path:
            QMessageBox.information(self, "No File Selected", "No file was selected.")
            return

        # Clear previous queue
        self.queue.clear()
        self.current_index = -1

        self.list_view.clear()
        self.prev_btn.setDisabled(True)
        self.next_btn.setDisabled(True)

        # Read and cache queue
        if not self.read_queue(file_path):
            return
        
        self.cache_queue()

        # Load queue into list view
        self.list_view.addItems([os.path.basename(path) for path in self.queue])
        
        # Start playing
        self.current_index = 0
        self.change_slide(0)
    
    def cache_queue(self):
        QPixmapCache.setCacheLimit(1024000)  # 1000 MB
        for path in self.queue:
            if path.endswith(".jpg") or path.endswith(".png"):
                if not QPixmapCache.find(path):
                    pixmap = QPixmap(path)
                    QPixmapCache.insert(path, pixmap)

    def read_queue(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()

                # Strip quotes if present
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1]
                
                # Check whether file is in a supported format
                if not line.lower().endswith(".jpg") and not line.lower().endswith(".png") and not line.lower().endswith(".mp4"):
                    QMessageBox.warning(self, "Unsupported Format", f"File '{line}' is not a supported format.")
                    return False
                
                # Check whether file exists
                if not os.path.isfile(line):
                    QMessageBox.warning(self, "File Not Found", f"File '{line}' does not exist.")
                    return False
                
                self.queue.append(line)
        return True

    def toggle_fullscreen(self):
        if player_window.isFullScreen():
            player_window.showNormal()
        else:
            player_window.showFullScreen()
    
    def closeEvent(self, event):
        event.accept()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(open("style.qss").read())

    # Retrieve screens
    screens = app.screens()

    console_window = Console()
    console_window.setWindowTitle("LivePlayer Console")
    console_window.setFixedSize(550, 600)
    console_window.show()

    player_window = Player()
    player_window.setWindowTitle("LivePlayer Player")
    player_window.setMinimumSize(640, 360)
    player_window.resize(640, 360)
    player_window.show()
    
    if len(screens) > 1:
        player_window.move(screens[1].geometry().topLeft())

    sys.exit(app.exec())
