import sys, os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QPixmapCache


class Player(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Media widgets
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.original_pixmap = None

        # Layout
        layout = QStackedLayout()
        layout.addWidget(self.image_label)

        self.setLayout(layout)
    
    def play_image(self, path):
        if QPixmapCache.find(path):
            self.original_pixmap = QPixmapCache.find(path)
        else:
            self.original_pixmap = QPixmap(path)
            QPixmapCache.insert(path, self.original_pixmap)
        self.update_image()
    
    def update_image(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.image_label.setPixmap(self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))
    
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
        self.exit_btn = QPushButton("Exit")

        self.prev_btn.setDisabled(True)
        self.next_btn.setDisabled(True)

        self.prev_btn.clicked.connect(lambda: self.change_slide(-1))
        self.next_btn.clicked.connect(lambda: self.change_slide(1))
        self.load_btn.clicked.connect(self.load_queue)
        self.exit_btn.clicked.connect(self.exit)

        for btn in [self.next_btn, self.prev_btn, self.load_btn, self.exit_btn]:
            btn.setFixedHeight(60)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # List view
        self.list_view = QListWidget()
        self.list_view.itemClicked.connect(lambda item: self.set_slide(item))

        # Layouts
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.prev_btn)
        top_row_layout.addWidget(self.next_btn)
        top_row_layout.setSpacing(40)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(self.load_btn)
        bottom_row_layout.addWidget(self.exit_btn)
        bottom_row_layout.setSpacing(40)

        layout = QVBoxLayout()
        layout.addLayout(top_row_layout)
        layout.addWidget(self.list_view)
        layout.addLayout(bottom_row_layout)
        layout.setSpacing(40)
        layout.setContentsMargins(30, 30, 30, 30)

        self.setLayout(layout)

    @Slot(int)
    def change_slide(self, step):
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

    @Slot(QListWidgetItem)
    def set_slide(self, item):
        self.current_index = self.list_view.row(item)

        self.change_slide(0)

    def load_queue(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt)")
        if file_path:
            self.read_queue(file_path)
        self.cache_queue()
    
    def cache_queue(self):
        QPixmapCache.setCacheLimit(1024000)  # 1000 MB
        for path in self.queue:
            if path.endswith(".jpg") or path.endswith(".png"):
                if not QPixmapCache.find(path):
                    pixmap = QPixmap(path)
                    QPixmapCache.insert(path, pixmap)

    def exit(self):
        QApplication.quit()

    def read_queue(self, file_path):
        self.queue.clear()
        self.current_index = -1

        self.list_view.clear()
        self.prev_btn.setDisabled(True)
        self.next_btn.setDisabled(True)

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
                    return
                
                # Check whether file exists
                if not os.path.isfile(line):
                    QMessageBox.warning(self, "File Not Found", f"File '{line}' does not exist.")
                    return
                
                self.queue.append(line)
        
        # Load queue into list view
        self.list_view.addItems([os.path.basename(path) for path in self.queue])
        
        # Start playing
        self.current_index = 0
        self.change_slide(0)

    def play_current(self):
        current_file = self.queue[self.current_index]
        
        # Check if image or video
        if current_file.endswith(".jpg") or current_file.endswith(".png"):
            player_window.play_image(current_file)
    
    def closeEvent(self, event):
        event.accept()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(open("style.qss").read())

    console_window = Console()
    console_window.setWindowTitle("LivePlayer Console")
    console_window.setFixedSize(500, 600)
    console_window.show()

    player_window = Player()
    player_window.setWindowTitle("LivePlayer Player")
    player_window.setMinimumSize(640, 360)
    player_window.resize(640, 360)
    player_window.show()

    sys.exit(app.exec())
