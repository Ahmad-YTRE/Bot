"""
: ! Aegis !
    + Discord: itsfizys
    + Community: https://discord.gg/aerox (AeroX Development )
    + for any queries reach out Community or DM me.
"""

import sys
import pytz
from datetime import datetime
import traceback
import io

config = {
    'logLevel': 'debug',
    'defaultContext': 'APP',
    'timezone': 'Asia/Kolkata',
    'colors': {
        'info': '#2F6FD6',
        'success': '#0FA37F',
        'warning': '#C47A00',
        'error': '#C2362B',
        'debug': '#6B6B6B',
    },
    'textColors': {
        'message': '#D8DEE9',
        'timestamp': '#7A7A7A',
        'dimmed': '#4C4C4C',
        'badge': '#E5E9F0',
    },
}

def rgb(hex_color):
    """Returns a function that wraps text in the given hex foreground colour using ANSI escape codes."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return lambda t: f"\x1b[38;2;{r};{g};{b}m{t}\x1b[0m"

def bg(bg_hex, fg_hex):
    """Returns a function that wraps text with ANSI background + foreground colours, adding padding."""
    bg_hex = bg_hex.lstrip('#')
    fg_hex = fg_hex.lstrip('#')
    br = int(bg_hex[0:2], 16)
    bgc = int(bg_hex[2:4], 16)
    bb = int(bg_hex[4:6], 16)
    fr = int(fg_hex[0:2], 16)
    fg = int(fg_hex[2:4], 16)
    fb = int(fg_hex[4:6], 16)
    return lambda t: f"\x1b[48;2;{br};{bgc};{bb}m\x1b[38;2;{fr};{fg};{fb}m {t} \x1b[0m"

class TextColours:
    """Pre-built colouriser functions for common text roles."""
    def __init__(self):
        self.message = rgb(config['textColors']['message'])
        self.timestamp = rgb(config['textColors']['timestamp'])
        self.dimmed = rgb(config['textColors']['dimmed'])

text = TextColours()

class Logger:
    """
    Structured console logger with coloured, badged output.
    Ported from the user's JavaScript reference.
    """
    def __init__(self):
        self.levels = {'debug': 0, 'info': 1, 'success': 2, 'warn': 3, 'error': 4}
        log_level_str = config.get('logLevel', 'debug')
        self.console_log_level = self.levels.get(log_level_str, 0)
        
        self.badges = {
            'info': bg(config['colors']['info'], config['textColors']['badge']),
            'success': bg(config['colors']['success'], config['textColors']['badge']),
            'warn': bg(config['colors']['warning'], config['textColors']['badge']),
            'error': bg(config['colors']['error'], config['textColors']['badge']),
            'debug': bg(config['colors']['debug'], config['textColors']['badge']),
        }
        try:
            self.tz = pytz.timezone(config['timezone'])
        except Exception:
            self.tz = pytz.UTC

    def _time(self):
        """Returns the current time formatted as HH:MM:SS in the configured timezone."""
        return datetime.now(self.tz).strftime('%H:%M:%S')

    def _parse(self, args):
        """Parses variadic log arguments into a structured format."""
        context = config['defaultContext']
        error = None
        a = list(args)

        if a and isinstance(a[-1], Exception):
            error = a.pop()
        
        if a and isinstance(a[0], str) and a[0].isupper() and len(a[0]) <= 12:
            context = a.pop(0)

        msg_parts = []
        for x in a:
            if isinstance(x, (dict, list)):
                import json
                try:
                    msg_parts.append(json.dumps(x, indent=2))
                except:
                    msg_parts.append(str(x))
            else:
                msg_parts.append(str(x))
        
        msg = " ".join(msg_parts)
        return context, msg, error

    def _log(self, level, *args):
        """Core log method."""
        if self.levels[level] < self.console_log_level:
            return

        context, msg, error = self._parse(args)

        line = (
            f"{text.timestamp(self._time())} "
            f"{self.badges[level](context)} "
            f"{text.message(msg)}"
        )

        if level in ['error', 'warn']:
            sys.stderr.write(line + "\n")
            sys.stderr.flush()
        else:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()

        if error:
            output = io.StringIO()
            traceback.print_exception(type(error), error, error.__traceback__, file=output)
            tb_str = output.getvalue()
            sys.stdout.write(text.dimmed(tb_str) + "\n")
            sys.stdout.flush()

    def info(self, *a): self._log('info', *a)
    def success(self, *a): self._log('success', *a)
    def warn(self, *a): self._log('warn', *a)
    def error(self, *a): self._log('error', *a)
    def debug(self, *a): self._log('debug', *a)

logger = Logger()
