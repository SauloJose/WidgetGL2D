from dataclasses import dataclass
from typing import Any, Optional, Tuple, List

@dataclass
class DrawCall:
    draw_type: str
    obj: Any
    x: float
    y: float
    angle: float = 0.0
    scale: float = 1.0         # Escala unificada
    scale_x: Optional[float] = None  # Escala específica em X
    scale_y: Optional[float] = None  # Escala específica em Y
    alpha: float = 1.0
    layer: int = 0
    color: Optional[Tuple[float, float, float, float]] = None
    points: Optional[List[Tuple[float, float]]] = None
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    radius: Optional[float] = None
    fill: bool = False  # Novo parâmetro para controle de preenchimento

    def __post_init__(self):
        # Se scale_x ou scale_y não foram fornecidos, usa o valor de scale
        if self.scale_x is None:
            self.scale_x = self.scale
        if self.scale_y is None:
            self.scale_y = self.scale