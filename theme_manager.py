"""
DoubOS Theme Manager
Customize desktop appearance and colors
"""

import json
import os


class ThemeManager:
    """Manage DoubOS themes"""
    
    # Predefined themes
    THEMES = {
        'catppuccin_mocha': {
            'name': 'Catppuccin Mocha',
            'colors': {
                'bg': '#1e1e2e',
                'fg': '#cdd6f4',
                'accent': '#89b4fa',
                'accent2': '#f38ba8',
                'surface0': '#313244',
                'surface1': '#45475a',
                'surface2': '#585b70',
                'text': '#cdd6f4',
                'subtext': '#bac2de',
                'overlay': '#6c7086',
                'taskbar': '#11111b',
                'window': '#1e1e2e',
                'button': '#45475a',
                'button_hover': '#585b70',
                'border': '#313244',
                'success': '#a6e3a1',
                'warning': '#f9e2af',
                'error': '#f38ba8',
            }
        },
        
        'dracula': {
            'name': 'Dracula',
            'colors': {
                'bg': '#282a36',
                'fg': '#f8f8f2',
                'accent': '#bd93f9',
                'accent2': '#ff79c6',
                'surface0': '#44475a',
                'surface1': '#6272a4',
                'surface2': '#8be9fd',
                'text': '#f8f8f2',
                'subtext': '#e9e9f4',
                'overlay': '#6272a4',
                'taskbar': '#1a1b26',
                'window': '#282a36',
                'button': '#44475a',
                'button_hover': '#6272a4',
                'border': '#44475a',
                'success': '#50fa7b',
                'warning': '#f1fa8c',
                'error': '#ff5555',
            }
        },
        
        'gruvbox_dark': {
            'name': 'Gruvbox Dark',
            'colors': {
                'bg': '#282828',
                'fg': '#ebdbb2',
                'accent': '#83a598',
                'accent2': '#fe8019',
                'surface0': '#3c3836',
                'surface1': '#504945',
                'surface2': '#665c54',
                'text': '#ebdbb2',
                'subtext': '#d5c4a1',
                'overlay': '#7c6f64',
                'taskbar': '#1d2021',
                'window': '#282828',
                'button': '#3c3836',
                'button_hover': '#504945',
                'border': '#3c3836',
                'success': '#b8bb26',
                'warning': '#fabd2f',
                'error': '#fb4934',
            }
        },
        
        'nord': {
            'name': 'Nord',
            'colors': {
                'bg': '#2e3440',
                'fg': '#eceff4',
                'accent': '#88c0d0',
                'accent2': '#81a1c1',
                'surface0': '#3b4252',
                'surface1': '#434c5e',
                'surface2': '#4c566a',
                'text': '#eceff4',
                'subtext': '#d8dee9',
                'overlay': '#4c566a',
                'taskbar': '#2e3440',
                'window': '#2e3440',
                'button': '#3b4252',
                'button_hover': '#434c5e',
                'border': '#3b4252',
                'success': '#a3be8c',
                'warning': '#ebcb8b',
                'error': '#bf616a',
            }
        },
        
        'tokyo_night': {
            'name': 'Tokyo Night',
            'colors': {
                'bg': '#1a1b26',
                'fg': '#c0caf5',
                'accent': '#7aa2f7',
                'accent2': '#bb9af7',
                'surface0': '#24283b',
                'surface1': '#414868',
                'surface2': '#565f89',
                'text': '#c0caf5',
                'subtext': '#a9b1d6',
                'overlay': '#565f89',
                'taskbar': '#16161e',
                'window': '#1a1b26',
                'button': '#24283b',
                'button_hover': '#414868',
                'border': '#24283b',
                'success': '#9ece6a',
                'warning': '#e0af68',
                'error': '#f7768e',
            }
        },
        
        'solarized_dark': {
            'name': 'Solarized Dark',
            'colors': {
                'bg': '#002b36',
                'fg': '#839496',
                'accent': '#268bd2',
                'accent2': '#2aa198',
                'surface0': '#073642',
                'surface1': '#586e75',
                'surface2': '#657b83',
                'text': '#93a1a1',
                'subtext': '#839496',
                'overlay': '#586e75',
                'taskbar': '#001f27',
                'window': '#002b36',
                'button': '#073642',
                'button_hover': '#586e75',
                'border': '#073642',
                'success': '#859900',
                'warning': '#b58900',
                'error': '#dc322f',
            }
        },
        
        'monokai': {
            'name': 'Monokai',
            'colors': {
                'bg': '#272822',
                'fg': '#f8f8f2',
                'accent': '#66d9ef',
                'accent2': '#a6e22e',
                'surface0': '#3e3d32',
                'surface1': '#49483e',
                'surface2': '#75715e',
                'text': '#f8f8f2',
                'subtext': '#cfcfc2',
                'overlay': '#75715e',
                'taskbar': '#1e1f1c',
                'window': '#272822',
                'button': '#3e3d32',
                'button_hover': '#49483e',
                'border': '#3e3d32',
                'success': '#a6e22e',
                'warning': '#e6db74',
                'error': '#f92672',
            }
        },
        
        'one_dark': {
            'name': 'One Dark',
            'colors': {
                'bg': '#282c34',
                'fg': '#abb2bf',
                'accent': '#61afef',
                'accent2': '#c678dd',
                'surface0': '#2c313a',
                'surface1': '#3e4451',
                'surface2': '#528bff',
                'text': '#abb2bf',
                'subtext': '#5c6370',
                'overlay': '#4b5263',
                'taskbar': '#21252b',
                'window': '#282c34',
                'button': '#2c313a',
                'button_hover': '#3e4451',
                'border': '#181a1f',
                'success': '#98c379',
                'warning': '#e5c07b',
                'error': '#e06c75',
            }
        },
    }
    
    def __init__(self, config_file="doubos_theme.json"):
        self.config_file = config_file
        self.current_theme = 'catppuccin_mocha'
        self.load_theme()
        
    def load_theme(self):
        """Load theme from config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get('theme', 'catppuccin_mocha')
        except Exception as e:
            print(f"Error loading theme: {e}")
            self.current_theme = 'catppuccin_mocha'
            
    def save_theme(self):
        """Save theme to config"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'theme': self.current_theme}, f, indent=2)
        except Exception as e:
            print(f"Error saving theme: {e}")
            
    def set_theme(self, theme_name):
        """Set active theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.save_theme()
            return True
        return False
        
    def get_theme(self):
        """Get current theme"""
        return self.THEMES.get(self.current_theme, self.THEMES['catppuccin_mocha'])
        
    def get_theme_names(self):
        """Get list of available themes"""
        return list(self.THEMES.keys())
        
    def get_color(self, color_name):
        """Get specific color from current theme"""
        theme = self.get_theme()
        return theme['colors'].get(color_name, '#000000')
        
    def create_custom_theme(self, name, colors):
        """Create custom theme"""
        self.THEMES[name] = {
            'name': name,
            'colors': colors
        }
        
    def export_theme(self, theme_name, filename):
        """Export theme to file"""
        if theme_name in self.THEMES:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.THEMES[theme_name], f, indent=2)
                return True
            except Exception as e:
                print(f"Error exporting theme: {e}")
        return False
        
    def import_theme(self, filename):
        """Import theme from file"""
        try:
            with open(filename, 'r') as f:
                theme_data = json.load(f)
                name = theme_data.get('name', 'custom')
                self.THEMES[name] = theme_data
                return True
        except Exception as e:
            print(f"Error importing theme: {e}")
        return False
        
    def get_theme_preview(self, theme_name):
        """Get theme preview colors"""
        if theme_name in self.THEMES:
            theme = self.THEMES[theme_name]
            colors = theme['colors']
            return {
                'name': theme['name'],
                'primary': colors.get('accent', '#000000'),
                'secondary': colors.get('accent2', '#000000'),
                'background': colors.get('bg', '#000000'),
                'foreground': colors.get('fg', '#ffffff'),
            }
        return None


# Global theme manager instance
_theme_manager = None

def get_theme_manager():
    """Get global theme manager"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme_to_widget(widget, theme_manager=None):
    """Apply theme to tkinter widget"""
    if theme_manager is None:
        theme_manager = get_theme_manager()
        
    theme = theme_manager.get_theme()
    colors = theme['colors']
    
    try:
        widget.configure(
            bg=colors.get('bg', '#1e1e2e'),
            fg=colors.get('fg', '#cdd6f4')
        )
    except:
        pass
