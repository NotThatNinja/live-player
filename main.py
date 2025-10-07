import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListView
from PySide6.QtGui import QFont
from PySide6.QtCore import Slot


class Console(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("LivePlayer Console")
        self.setFixedSize(500, 600)

        # Buttons
        self.next_btn = QPushButton("Next")
        self.prev_btn = QPushButton("Previous")
        self.load_btn = QPushButton("Load")
        self.exit_btn = QPushButton("Exit")

        self.next_btn.clicked.connect(lambda: self.change_slide(1))
        self.prev_btn.clicked.connect(lambda: self.change_slide(1))
        self.load_btn.clicked.connect(self.load_queue)
        self.exit_btn.clicked.connect(self.exit)

        for btn in [self.next_btn, self.prev_btn, self.load_btn, self.exit_btn]:
            btn.setFixedHeight(100)

        # List view
        self.list_view = QListView()

        # Layouts
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.next_btn)
        top_row_layout.addWidget(self.prev_btn)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(self.load_btn)
        bottom_row_layout.addWidget(self.exit_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_row_layout)
        layout.addWidget(self.list_view)
        layout.addLayout(bottom_row_layout)

        self.setLayout(layout)

    @Slot(int)
    def change_slide(self, step):
        print(step)

    def load_queue(self):
        pass

    def exit(self):
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = Console()
    window.show()
    sys.exit(app.exec())
