from PyQt5.QtWidgets import QApplication, QMainWindow
from GL2DWidget import GL2DWidget
import sys

def main():
    app = QApplication(sys.argv)

    # Create a main window
    window = QMainWindow()
    window.setWindowTitle("GL2DWidget Test")

    # Add GL2DWidget to the main window
    widget = GL2DWidget(window, width=800, height=600)
    window.setCentralWidget(widget)

    # Ensure OpenGL context is initialized
    widget.show()  # Necessário para garantir que o contexto OpenGL seja criado
    app.processEvents()  # Processa eventos pendentes para inicializar o contexto

    if not widget.context() or not widget.context().isValid():
        print("[Error][main]: OpenGL context is not valid. Exiting application.")
        sys.exit(1)  # Encerra o programa com código de erro

    # Example: Draw a red rectangle
    widget.back_buffer.draw_rect(50, 50, 200, 100, color=(1, 0, 0, 1), layer=1)

    # Example: Draw a blue circle
    widget.back_buffer.draw_circle(400, 300, 50, color=(0, 0, 1, 1), layer=2)

    # Example: Draw a green line
    widget.back_buffer.draw_line(100, 100, 300, 300, color=(0, 1, 0, 1), layer=3)

    # Example: Draw text
    widget.back_buffer.draw_text(200, 400, "Hello, GL2DWidget!", color=(1, 1, 1, 1), layer=4)

    # Render the frame
    widget.render_frame()

    # Show the window
    window.show()

    # Start the application loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
