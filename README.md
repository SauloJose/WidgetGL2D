# GL2DWidget: 2D Rendering Widget with OpenGL and PyQt5

`GL2DWidget` is a highly customizable widget based on `QOpenGLWidget` that provides a platform for high-performance 2D rendering using OpenGL. Ideal for visual simulations, such as robotics simulators, the widget allows you to draw 2D objects, including images, geometric shapes, text, and more, with full control over the rendering process.

---

## ⚙️ Features

- **Custom 2D Rendering**: Draw images, geometric shapes, lines, circles, text, polygons, arrows, and more.
- **Optimized Performance**: Supports texture caching and Framebuffer Objects (FBOs) for efficient rendering.
- **Full Control**: Integrates with PyQt5, allowing you to capture keyboard and mouse events and customize the interface.
- **Modular Design**: Easy to extend and customize for your specific needs.

---

## 🛠️ Installation

### Requirements

- Python 3.x
- PyQt5
- PyOpenGL
- NumPy
- Pillow (PIL)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/GL2DWidget.git
   cd GL2DWidget
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Usage

### Initializing the Widget

You can easily add `GL2DWidget` to any PyQt5 application:

```python
from PyQt5.QtWidgets import QApplication, QMainWindow
from GL2DWidget import GL2DWidget

app = QApplication([])

# Create a main window
window = QMainWindow()
widget = GL2DWidget(window, 800, 600)  # Widget size
window.setCentralWidget(widget)

window.show()
app.exec_()
```

### Rendering Content

After initializing the widget, use the `paintGL` method to draw graphical elements. The rendering can be customized as needed.

---

## 🎮 Example

### Drawing a Rectangle

```python
widget.back_buffer.draw_rect(50, 50, 200, 100, color=(1, 0, 0, 1), layer=1)
widget.render_frame()
```

### Drawing Text

```python
widget.back_buffer.draw_text(100, 100, "Example Text", color=(1, 1, 1, 1), layer=1)
widget.render_frame()
```

---

## 🛡️ How It Works

### Rendering Architecture

`GL2DWidget` uses a combination of OpenGL and PyQt5 to create a high-performance 2D rendering surface. It leverages:

- **Framebuffer Objects (FBOs)**: For efficient rendering with back buffers.
- **Texture Caching**: Stores rendered textures to avoid unnecessary recreation.
- **OpenGL Shaders**: Enables advanced visual effects.

### Layer System

The widget supports a layer system for drawing objects, allowing you to control the rendering order:

```python
widget.back_buffer.add_draw_call(draw_type="rect", x=10, y=10, scale_x=100, scale_y=100, color=(1, 0, 0, 1), layer=1)
```

---

## 📚 Testing

Run the `testWindow.py` script to test the widget:

```bash
python testWindow.py
```

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.