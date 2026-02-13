import logging
from rich.logging import RichHandler
from rich.console import Console

# Configure rich logging for this module
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)

def get_logger(name: str):
    """
    Get a configured logger instance for the specified module.

    Args:
        name (str): Name of the module/logger

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Allow all levels for individual loggers
    return logger