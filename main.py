import sys, os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PySide6.QtCore import Slot


class Console(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.queue = []
        self.current_index = -1

        # Window settings
        self.setWindowTitle("LivePlayer Console")
        self.setFixedSize(500, 600)

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

        # List view
        self.list_view = QListWidget()
        self.list_view.setSelectionMode(QListWidget.NoSelection)
        self.list_view.itemDoubleClicked.connect(lambda item: self.set_slide(item))

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

        # Update list view selection
        self.list_view.setSelectionMode(QListWidget.SingleSelection)
        self.list_view.setCurrentRow(self.current_index)
        self.list_view.setSelectionMode(QListWidget.NoSelection)

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
        pass


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(open("style.qss").read())

    window = Console()
    window.show()
    sys.exit(app.exec())
