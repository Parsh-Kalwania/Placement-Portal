"""
Logging configuration for the placement portal API.
Sets up loggers for different modules and handlers for file and console output.
"""

import logging
import logging.handlers
import os
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Define log file paths
LOG_FILE = LOGS_DIR / 'portal.log'
ERROR_LOG_FILE = LOGS_DIR / 'errors.log'
AUTH_LOG_FILE = LOGS_DIR / 'auth.log'


def get_logger(name, log_file=None, level=logging.DEBUG):
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name (typically __name__)
        log_file (str): Optional path to log file for this logger
        level (int): Logging level (default: DEBUG)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def setup_loggers():
    """
    Set up all application loggers.
    Should be called once at application startup.
    """
    
    # Main application logger
    app_logger = get_logger('placement_portal', log_file=LOG_FILE)
    
    # Models logger
    models_logger = get_logger('placement_portal.models', log_file=LOG_FILE)
    
    # Views logger
    views_logger = get_logger('placement_portal.views', log_file=LOG_FILE)
    
    # Authentication logger
    auth_logger = get_logger('placement_portal.auth', log_file=AUTH_LOG_FILE)
    
    # Error logger
    error_logger = get_logger('placement_portal.errors', log_file=ERROR_LOG_FILE)
    
    # Drives logger
    drives_logger = get_logger('placement_portal.drives', log_file=LOG_FILE)
    
    # Users logger
    users_logger = get_logger('placement_portal.users', log_file=LOG_FILE)
    
    # Applications logger
    apps_logger = get_logger('placement_portal.applications', log_file=LOG_FILE)
    
    return {
        'app': app_logger,
        'models': models_logger,
        'views': views_logger,
        'auth': auth_logger,
        'errors': error_logger,
        'drives': drives_logger,
        'users': users_logger,
        'applications': apps_logger,
    }


# Initialize loggers on import
_loggers = setup_loggers()


def get_logger_for_module(module_name):
    """
    Get a logger for a specific module.
    
    Args:
        module_name (str): Module name to get logger for
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f'placement_portal.{module_name}')
