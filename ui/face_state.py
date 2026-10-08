from dataclasses import dataclass


@dataclass
class FaceState:
    blink_state: float = 0.0
    blink_direction: int = 0
    smiling: bool = False
    talking: bool = False
    eye_offset_x: float = 0.0
    eye_offset_y: float = 0.0
    question_opacity: float = 0.0
