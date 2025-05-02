from drawCall import * 
from Image import *

#Classe do back buffer
class BackBuffer2D:
    #Definição de layers
    LAYER_BACKGROUND = 0
    LAYER_OBJECTS = 1
    LAYER_DEBUG = 2

    #Tipos de desenho
    DRAW_IMAGE = "image"
    DRAW_PRIMITIVE = "primitive"
    DRAW_TEXT = "text"

    def __init__(self):
        self.draw_calls = []

    def clear(self):
        self.draw_calls.clear()
    
    def get_calls(self):
        return self.draw_calls.copy() #Retorna cópia para evitar modificações externas
    
    # == Métodos públicos de desenho
    def draw_rect(self, x, y, w, h, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG, fill = False):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="rect",
            x=x,
            y=y,
            scale_x=w,
            scale_y=h,
            color=color,
            layer=layer,
            fill = fill 
        )

    # Adicione este método para suporte a VBOs
    def draw_rect_vbo(self, x, y, w, h, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG, fill=False):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="rect_vbo",
            x=x,
            y=y,
            scale_x=w,
            scale_y=h,
            color=color,
            layer=layer,
            fill=fill
        )

    def draw_line(self, x1, y1, x2, y2, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="line",
            x=x1,
            y=y1,
            end_x=x2,
            end_y=y2,
            color=color,
            layer=layer
        )

    def draw_circle(self, x, y, radius, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="circle",
            x=x,
            y=y,
            radius=radius,
            color=color,
            layer=layer
        )

    def draw_polygon(self, x, y, points, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="polygon",
            x=x,
            y=y,
            points=points,
            color=color,
            layer=layer
        )

    def draw_arrow(self, x1, y1, x2, y2, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG):
        self.add_draw_call(
            draw_type=self.DRAW_PRIMITIVE,
            obj="arrow",
            x=x1,
            y=y1,
            end_x=x2,
            end_y=y2,
            color=color,
            layer=layer
        )

    def draw_text(self, x, y, text, color=(1.0, 1.0, 1.0, 1.0), layer=LAYER_DEBUG):
        self.add_draw_call(
            draw_type=self.DRAW_TEXT,
            obj=text,
            x=x,
            y=y,
            color=color,
            layer=layer
        )

    def draw_img(self, image_obj, x, y, angle=0.0, scale=1.0, alpha=1.0, layer=LAYER_OBJECTS):
        if not image_obj or not image_obj.is_valid():
            print("Aviso: Tentando desenhar imagem inválida")
            return

        self.add_draw_call(
            draw_type=self.DRAW_IMAGE,
            obj=image_obj,
            x=x,
            y=y,
            angle=angle,
            scale=scale,
            alpha=alpha,
            layer=layer
        )

    def add_draw_call(self, draw_type: str, obj, x: float, y: float, angle: float = 0.0,
                     scale: float = 1.0, scale_x: float = None, scale_y: float = None,
                     alpha: float = 1.0, layer: int = 0, color: tuple = None,
                     points: list = None, end_x: float = None, end_y: float = None,
                     radius: float = None, fill: bool = False):
        
        # Validação básica dos parâmetros
        if not isinstance(layer, int) or layer < 0:
            raise ValueError("Layer must be a non-negative integer")
        
        if color and (len(color) not in (3, 4) or not all(0.0 <= c <= 1.0 for c in color)):
            raise ValueError("Color must be a tuple of 3 or 4 floats between 0.0 and 1.0")
        
        # Tratamento consistente das escalas
        if scale_x is None and scale_y is None:
            scale_x = scale
            scale_y = scale
        elif scale_x is None:
            scale_x = scale_y
        elif scale_y is None:
            scale_y = scale_x

        self.draw_calls.append(DrawCall(
            draw_type=draw_type,
            obj=obj,
            x=x,
            y=y,
            angle=angle,
            scale=scale,
            alpha=alpha,
            layer=layer,
            color=color,
            points=points,
            end_x=end_x,
            end_y=end_y,
            radius=radius,
            scale_x=scale_x,
            scale_y=scale_y,
            fill = fill
        ))