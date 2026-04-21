import logging
import sys

# ANSI Escape Codes for Colors
# Note: 33 is Yellow/Brown, which commonly represents Orange in basic ANSI
COLORS = {
    'ORANGE': '\033[33m',
    'BLUE': '\033[34m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'RESET': '\033[0m'
}

# ANSI for bold
ANSI_BOLD = '\033[1m'

class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter that adds colors based on message tags.
    Tags: [CREATE], [UPDATE], [DELETE], [INFO]
    """
    def format(self, record):
        # Use super() to get the standard formatted message
        msg = super().format(record)
        # Handle LARGE tag: try to render big ASCII art via pyfiglet if installed
        if "[LARGE]" in msg:
            clean = msg.replace("[LARGE]", "").strip()
            try:
                from pyfiglet import Figlet
                fig = Figlet()
                rendered = fig.renderText(clean)
                return f"{COLORS['ORANGE']}{rendered}{COLORS['RESET']}"
            except Exception:
                # Fallback: bold the message if pyfiglet isn't available
                return f"{ANSI_BOLD}{COLORS['ORANGE']}{clean}{COLORS['RESET']}"

        # Handle BOLD tag: apply ANSI bold wrapper
        if "[BOLD]" in msg:
            clean = msg.replace("[BOLD]", "").strip()
            return f"{ANSI_BOLD}{clean}{COLORS['RESET']}"

        if "[CREATE]" in msg:
            return f"{COLORS['ORANGE']}{msg}{COLORS['RESET']}"
        elif "[UPDATE]" in msg:
            return f"{COLORS['BLUE']}{msg}{COLORS['RESET']}"
        elif "[DELETE]" in msg:
            return f"{COLORS['RED']}{msg}{COLORS['RESET']}"
        elif "[INFO]" in msg:
            return f"{COLORS['GREEN']}{msg}{COLORS['RESET']}"

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
        # If multiple args are passed but no %s in msg, join them like print()
        return f"{msg} " + " ".join(str(a) for a in args), ()
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

def log_bold(logger, msg, *args):
    """Logs a message with [BOLD] tag to render bold in ANSI-capable terminals."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[BOLD] {m}", *a)


def log_large(logger, msg, *args):
    """Logs a message with [LARGE] tag. If `pyfiglet` is installed, renders large ASCII art; otherwise falls back to bold."""
    m, a = _format_msg(msg, *args)
    logger.info(f"[LARGE] {m}", *a)
