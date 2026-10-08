pip freeze > requirements.txt
pip install -r requirements.txt

# Robo Assistant — refactored

## Структура

```text
robo_assistant/
├── main.py
├── config.py
├── resources.py
├── requirements.txt
├── app/
│   └── robo_assistant.py
├── domain/
│   └── timer.py
├── services/
│   └── audio_service.py
└── ui/
    ├── face_animation.py
    ├── face_painter.py
    ├── face_state.py
    └── timer_panel.py
```

## Запуск

Покладіть `positive-notification.mp3` поруч із `main.py`.

```bash
pip install -r requirements.txt
python main.py
```

## Зміна розміру

Відкрийте `config.py`:

```python
@dataclass(frozen=True)
class WindowConfig:
    ...
    SCALE: float = 1.0
```

Наприклад:

```python
SCALE = 1.5
```

дасть приблизно `195x128`, а:

```python
SCALE = 2.0
```

дасть `260x170`.

Тобто для звичайного масштабування не потрібно змінювати координати очей, розміри кнопок, шрифти тощо — вони масштабуються автоматично.

## Чому так

- `domain/timer.py` — бізнес-логіка Pomodoro без Qt.
- `services/audio_service.py` — робота зі звуком.
- `ui/face_painter.py` — тільки малювання.
- `ui/face_animation.py` — тільки анімація.
- `ui/timer_panel.py` — створення контролів таймера.
- `app/robo_assistant.py` — координація компонентів.
- `config.py` — конфігурація.
- `main.py` — точка входу.

При додаванні, наприклад, нового типу анімації краще додати окремий компонент у `ui`, а не збільшувати `RoboAssistant`.
