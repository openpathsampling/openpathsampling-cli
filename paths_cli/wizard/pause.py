import time
import contextlib
from collections import namedtuple

PauseStyle = namedtuple("PauseStyle", ['short', 'long', 'section'])

PAUSE_STYLES = {
    'testing': PauseStyle(0.01, 0.03, 0.05),
    'default': PauseStyle(0.1, 0.5, 0.75),
    'nopause': PauseStyle(0.0, 0.0, 0.0),
}

_PAUSE_STYLE = PAUSE_STYLES['default']


@contextlib.contextmanager
def pause_style(style):
    """Context manager for pause styles.

    Parameters
    ----------
    style : :class:`.PauseStyle`
        pause style to use within the context
    """
    old_style = get_pause_style()
    try:
        set_pause_style(style)
        yield
    finally:
        set_pause_style(old_style)


def get_pause_style():
    """Get the current pause style"""
    return _PAUSE_STYLE


def set_pause_style(style):
    """Set the pause style

    Parameters
    ----------
    pause_style : :class:`.PauseStyle` or str
        pause style to use, can be a string if the style is registered in
        pause.PAUSE_STYLES
    """
    global _PAUSE_STYLE
    if isinstance(style, str):
        try:
            _PAUSE_STYLE = PAUSE_STYLES[style]
        except KeyError as exc:
            raise RuntimeError(f"Unknown pause style: '{style}'") from exc
    else:
        _PAUSE_STYLE = style


def section(wizard):
    """Section break (pause and possible visual cue).
    """
    time.sleep(_PAUSE_STYLE.section)
    wizard.console.draw_hline()


def long(wizard):
    """Long pause from the wizard"""
    time.sleep(_PAUSE_STYLE.long)


def short(wizard):
    """Short pause from the wizard"""
    time.sleep(_PAUSE_STYLE.short)
