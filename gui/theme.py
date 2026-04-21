"""Theme management for dark/light mode support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Color palette for the application."""

    primary: str
    primary_light: str
    primary_dark: str
    bg_main: str
    bg_secondary: str
    bg_tertiary: str
    text_primary: str
    text_secondary: str
    text_disabled: str
    success: str
    warning: str
    danger: str
    info: str
    border: str
    border_light: str
    malicious: str
    clean: str
    quarantined: str


class DarkTheme:
    """Dark theme color scheme."""

    COLORS = ColorScheme(
        primary="#1f6feb",
        primary_light="#388bfd",
        primary_dark="#1854a6",
        bg_main="#0d1117",
        bg_secondary="#161b22",
        bg_tertiary="#21262d",
        text_primary="#c9d1d9",
        text_secondary="#8b949e",
        text_disabled="#6e7681",
        success="#238636",
        warning="#d29922",
        danger="#da3633",
        info="#1f6feb",
        border="#30363d",
        border_light="#21262d",
        malicious="#da3633",
        clean="#238636",
        quarantined="#d29922",
    )

    STYLESHEET = """
    QMainWindow, QDialog {{
        background-color: {bg_main};
        color: {text_primary};
    }}
    QPushButton {{
        background-color: {primary};
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {primary_light};
    }}
    QLineEdit, QTextEdit {{
        background-color: {bg_secondary};
        color: {text_primary};
        border: 1px solid {border};
        padding: 6px;
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {bg_secondary};
        color: {text_primary};
        padding: 8px 16px;
        border: 1px solid {border};
    }}
    QTabBar::tab:selected {{
        background-color: {bg_main};
        border-bottom: 2px solid {primary};
    }}
    QListWidget, QTableWidget {{
        background-color: {bg_secondary};
        color: {text_primary};
        border: 1px solid {border};
    }}
    QListWidget::item:selected {{
        background-color: {primary};
    }}
    QMenuBar {{
        background-color: {bg_secondary};
        color: {text_primary};
        border-bottom: 1px solid {border};
    }}
    QMenuBar::item:selected {{
        background-color: {bg_tertiary};
    }}
    QStatusBar {{
        background-color: {bg_secondary};
        color: {text_primary};
        border-top: 1px solid {border};
    }}
    """


class LightTheme:
    """Light theme color scheme."""

    COLORS = ColorScheme(
        primary="#0969da",
        primary_light="#54aeff",
        primary_dark="#0550ae",
        bg_main="#ffffff",
        bg_secondary="#f6f8fa",
        bg_tertiary="#eaeef2",
        text_primary="#24292f",
        text_secondary="#57606a",
        text_disabled="#8c959f",
        success="#1a7f0f",
        warning="#9e6a03",
        danger="#cf222e",
        info="#0969da",
        border="#d0d7de",
        border_light="#e5e7eb",
        malicious="#cf222e",
        clean="#1a7f0f",
        quarantined="#9e6a03",
    )

    STYLESHEET = """
    QMainWindow, QDialog {{
        background-color: {bg_main};
        color: {text_primary};
    }}
    QPushButton {{
        background-color: {primary};
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {primary_light};
    }}
    QLineEdit, QTextEdit {{
        background-color: {bg_main};
        color: {text_primary};
        border: 1px solid {border};
        padding: 6px;
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {bg_secondary};
        color: {text_primary};
        padding: 8px 16px;
        border: 1px solid {border};
    }}
    QTabBar::tab:selected {{
        background-color: {bg_main};
        border-bottom: 2px solid {primary};
    }}
    QListWidget, QTableWidget {{
        background-color: {bg_main};
        color: {text_primary};
        border: 1px solid {border};
    }}
    QListWidget::item:selected {{
        background-color: {primary};
        color: white;
    }}
    QMenuBar {{
        background-color: {bg_secondary};
        color: {text_primary};
        border-bottom: 1px solid {border};
    }}
    QMenuBar::item:selected {{
        background-color: {bg_tertiary};
    }}
    QStatusBar {{
        background-color: {bg_secondary};
        color: {text_primary};
        border-top: 1px solid {border};
    }}
    """


class ThemeManager:
    """Manages application themes."""

    DARK = "dark"
    LIGHT = "light"

    def __init__(self, theme_name: str = DARK):
        self.current_theme = theme_name
        self._themes = {
            self.DARK: DarkTheme,
            self.LIGHT: LightTheme,
        }

    def get_stylesheet(self) -> str:
        """Get the current theme's stylesheet."""
        theme_class = self._themes.get(self.current_theme, DarkTheme)
        colors = theme_class.COLORS
        stylesheet = theme_class.STYLESHEET

        return stylesheet.format(
            primary=colors.primary,
            primary_light=colors.primary_light,
            primary_dark=colors.primary_dark,
            bg_main=colors.bg_main,
            bg_secondary=colors.bg_secondary,
            bg_tertiary=colors.bg_tertiary,
            text_primary=colors.text_primary,
            text_secondary=colors.text_secondary,
            text_disabled=colors.text_disabled,
            success=colors.success,
            warning=colors.warning,
            danger=colors.danger,
            info=colors.info,
            border=colors.border,
            border_light=colors.border_light,
            malicious=colors.malicious,
            clean=colors.clean,
            quarantined=colors.quarantined,
        )

    def get_colors(self) -> ColorScheme:
        """Get the current theme's color scheme."""
        theme_class = self._themes.get(self.current_theme, DarkTheme)
        return theme_class.COLORS

    def set_theme(self, theme_name: str) -> None:
        """Switch to a different theme."""
        if theme_name in self._themes:
            self.current_theme = theme_name
        else:
            raise ValueError(f"Unknown theme: {theme_name}")

    def get_available_themes(self) -> list[str]:
        """Get list of available themes."""
        return list(self._themes.keys())
