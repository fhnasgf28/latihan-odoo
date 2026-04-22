import logging
import sys
import re

# ANSI Escape Codes for Colors and Styles
COLORS = {
    'ORANGE': '\033[33m',
    'BLUE': '\033[34m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'WHITE': '\033[97m', # Bright White
    # Vibrant 256-colors for Testing Messages (Distinct & Bright)
    'VIBRANT_ORANGE': '\033[1;38;5;214m', # For Tag Text
    'BRIGHT_SKY': '\033[1;38;5;51m',      # Testing1 Message Color
    'BRIGHT_LIME': '\033[1;38;5;118m',    # Testing2 Message Color
    'BRIGHT_PINK': '\033[1;38;5;201m',    # Testing3 Message Color
    # Backgrounds for Tags
    'BG_BRIGHT_GREEN': '\033[102m',
    'BG_BRIGHT_PINK': '\033[105m',
    'BG_BRIGHT_YELLOW': '\033[103m',
    'BG_BRIGHT_RED': '\033[101m',
    'BG_ORANGE': '\033[48;5;208m',
    'BOLD': '\033[1m',
    'RESET': '\033[0m'
}

class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter that adds colors and BOLD styling.
    Updated with specific background colors for testing levels.
    """
    def _highlight_values(self, text, return_color):
        """Finds text in `backticks` and colors it white, then returns to return_color."""
        if "`" not in text:
            return text
        # Replace `value` with ORANGE + value + return_color (to resume msg color)
        return re.sub(r"`(.*?)`", f"{COLORS['VIBRANT_ORANGE']}\\1{return_color}", text)

    def format(self, record):
        # Use super() to get the standard formatted message
        msg = super().format(record)
        
        # Standard Tags
        if "[CREATE]" in msg:
            msg = self._highlight_values(msg, COLORS['ORANGE'])
            return f"{COLORS['BOLD']}{COLORS['ORANGE']}{msg}{COLORS['RESET']}"
        elif "[UPDATE]" in msg:
            msg = self._highlight_values(msg, COLORS['BLUE'])
            return f"{COLORS['BOLD']}{COLORS['BLUE']}{msg}{COLORS['RESET']}"
        elif "[DELETE]" in msg:
            msg = self._highlight_values(msg, COLORS['RED'])
            return f"{COLORS['BOLD']}{COLORS['RED']}{msg}{COLORS['RESET']}"
        elif "[INFO]" in msg:
            msg = self._highlight_values(msg, COLORS['GREEN'])
            return f"{COLORS['BOLD']}{COLORS['GREEN']}{msg}{COLORS['RESET']}"
        
        # Testing tags with Requested Backgrounds
        
        elif "[TESTING1]" in msg:
            # BG Green, Msg Sky Blue
            tag_part = f"{COLORS['BG_BRIGHT_GREEN']}{COLORS['VIBRANT_ORANGE']}[TESTING1]{COLORS['RESET']}"
            msg_content = msg.replace('[TESTING1]', '')
            msg_part = f"{COLORS['BRIGHT_SKY']}{self._highlight_values(msg_content, COLORS['BRIGHT_SKY'])}{COLORS['RESET']}"
            return f"{tag_part}{msg_part}"
            
        elif "[TESTING2]" in msg:
            # BG Pink, Msg Lime Green
            tag_part = f"{COLORS['BG_BRIGHT_PINK']}{COLORS['VIBRANT_ORANGE']}[TESTING2]{COLORS['RESET']}"
            msg_content = msg.replace('[TESTING2]', '')
            msg_part = f"{COLORS['BRIGHT_LIME']}{self._highlight_values(msg_content, COLORS['BRIGHT_LIME'])}{COLORS['RESET']}"
            return f"{tag_part}{msg_part}"
            
        elif "[TESTING3]" in msg:
            # BG Yellow, Msg Pink
            tag_part = f"{COLORS['BG_BRIGHT_YELLOW']}{COLORS['VIBRANT_ORANGE']}[TESTING3]{COLORS['RESET']}"
            msg_content = msg.replace('[TESTING3]', '')
            msg_part = f"{COLORS['BRIGHT_PINK']}{self._highlight_values(msg_content, COLORS['BRIGHT_PINK'])}{COLORS['RESET']}"
            return f"{tag_part}{msg_part}"

        elif "[USERERROR]" in msg:
            # BG Orange, Msg Bold Red
            tag_part = f"{COLORS['BG_ORANGE']}{COLORS['BOLD']}[USERERROR]{COLORS['RESET']}"
            msg_content = msg.replace('[USERERROR]', '')
            msg_part = f"{COLORS['BOLD']}{COLORS['RED']}{self._highlight_values(msg_content, COLORS['RED'])}{COLORS['RESET']}"
            return f"{tag_part}{msg_part}"
        
        return msg

def get_logger(name):
    """
    Returns a logger configured with a ColorFormatter.
    Prevents duplicate handlers and ensures clean terminal output.
    """
    logger = logging.getLogger(name)
    
    # Check if we already added a ColorFormatter to avoid duplicate output
    has_custom_handler = any(
        isinstance(h.formatter, ColorFormatter) for h in logger.handlers
    )
    
    if not has_custom_handler:
        # Create a stream handler for the terminal (stdout)
        handler = logging.StreamHandler(sys.stdout)
        
        # Define a clean format similar to Odoo standard
        formatter = ColorFormatter('%(asctime)s %(levelname)s %(name)s: %(message)s', 
                                   datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        # Disable propagation to prevent duplicate logs in the terminal 
        # (avoiding the parent Odoo logger from printing the same message)
        logger.propagate = False
        
        # Set level to INFO by default for this custom logger
        logger.setLevel(logging.INFO)
        
    return logger

# --- Helper Functions ---

def _format_msg(msg, *args):
    if args and isinstance(msg, str) and "%" not in msg:
        # If multiple args are passed, wrap them in backticks to trigger WHITE color in formatter
        return f"{msg} " + " ".join(f"`{a}`" for a in args), ()
    return msg, args

def log_create(logger, msg, *args):
    """Logs a creation event with [CREATE] tag in Orange."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[CREATE] {m}", *a)

def log_update(logger, msg, *args):
    """Logs an update event with [UPDATE] tag in Blue."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[UPDATE] {m}", *a)

def log_delete(logger, msg, *args):
    """Logs a deletion event with [DELETE] tag in Red."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[DELETE] {m}", *a)

def log_info(logger, msg, *args):
    """Logs an info event with [INFO] tag in Green."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[INFO] {m}", *a)

def log_testing1(logger, msg, *args):
    """Logs a testing event: Bright Green BG Tag + Bright Sky Blue Message."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[TESTING1] {m}", *a)

def log_testing2(logger, msg, *args):
    """Logs a testing event: Bright Pink BG Tag + Bright Lime Green Message."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[TESTING2] {m}", *a)

def log_testing3(logger, msg, *args):
    """Logs a testing event: Bright Yellow BG Tag + Bright Pink Message."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[TESTING3] {m}", *a)

def log_usererror(logger, msg, *args):
    """Logs a user error event with [USERERROR] tag: Bright Red BG Tag + Bold Red Message."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[USERERROR] {m}", *a)
