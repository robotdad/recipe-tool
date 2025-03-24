"""Logging utilities for the Recipe Executor."""

import logging
import logging.handlers
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


class LogManager:
    """
    Centralized logging manager for Recipe Executor.
    
    This class handles log file setup, configuration, and provides
    access to different loggers for various components of the system.
    """
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEBUG_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    
    # Default paths
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_INFO_LOG = "info.log"
    DEFAULT_ERROR_LOG = "error.log"
    DEFAULT_DEBUG_LOG = "debug.log"
    
    def __new__(cls, *args, **kwargs):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: Optional[str] = None, reset_logs: bool = True):
        """
        Initialize the log manager.
        
        Args:
            log_dir: Directory to store log files in
            reset_logs: Whether to reset the log files on startup
        """
        # Only initialize once
        if LogManager._initialized:
            return
            
        self.log_dir = log_dir or self.DEFAULT_LOG_DIR
        self.reset_logs = reset_logs
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Reset logs if requested
        if self.reset_logs:
            self._reset_logs()
            
        # Set up the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Configure the main application logger
        self._configure_app_logger()
        
        # Mark as initialized
        LogManager._initialized = True
    
    def _reset_logs(self) -> None:
        """Reset log files by removing and recreating the log directory."""
        log_path = Path(self.log_dir)
        if log_path.exists():
            # Create a backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"{self.log_dir}_backup_{timestamp}"
            
            # Only create backup if there are existing logs
            if any(log_path.iterdir()):
                os.makedirs(backup_dir, exist_ok=True)
                for log_file in log_path.glob("*.log"):
                    shutil.copy2(log_file, os.path.join(backup_dir, log_file.name))
                
            # Clear log files
            for log_file in log_path.glob("*.log"):
                log_file.unlink()
    
    def _configure_app_logger(self) -> None:
        """Set up the main application logger with file handlers."""
        app_logger = logging.getLogger("recipe-executor")
        app_logger.setLevel(logging.INFO)
        app_logger.propagate = False  # Don't propagate to root logger
        
        # Clear any existing handlers
        for handler in app_logger.handlers[:]:
            app_logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        app_logger.addHandler(console_handler)
        
        # Create info file handler
        info_file = os.path.join(self.log_dir, self.DEFAULT_INFO_LOG)
        info_handler = logging.handlers.RotatingFileHandler(
            info_file, maxBytes=10485760, backupCount=5
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        app_logger.addHandler(info_handler)
        
        # Create error file handler
        error_file = os.path.join(self.log_dir, self.DEFAULT_ERROR_LOG)
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=10485760, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        app_logger.addHandler(error_handler)
        
        # Create debug file handler
        debug_file = os.path.join(self.log_dir, self.DEFAULT_DEBUG_LOG)
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_file, maxBytes=10485760, backupCount=5
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter(self.DEBUG_LOG_FORMAT))
        app_logger.addHandler(debug_handler)
        
        # Store the logger
        self._loggers["app"] = app_logger
    
    def get_logger(self, name: str = "app") -> logging.Logger:
        """
        Get a logger by name.
        
        Args:
            name: Name of the logger to get. Default is the main app logger.
            
        Returns:
            The requested logger
        """
        if name == "app":
            return self._loggers["app"]
        
        # Create a new component logger if needed
        if name not in self._loggers:
            logger = logging.getLogger(f"recipe-executor.{name}")
            logger.setLevel(logging.INFO)
            
            # Component loggers inherit handlers from the parent logger
            # but we want to ensure they're properly configured
            if not logger.handlers:
                logger.propagate = True
            
            self._loggers[name] = logger
            
        return self._loggers[name]
    
    def set_level(self, level: Union[int, str], name: str = "app") -> None:
        """
        Set the logging level for a logger.
        
        Args:
            level: The logging level to set
            name: Name of the logger to set the level for
        """
        # Convert string levels to ints
        if isinstance(level, str):
            level = getattr(logging, level.upper())
            
        logger = self.get_logger(name)
        logger.setLevel(level)
        
        # Update console handler level if this is the app logger
        if name == "app":
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(
                    handler, logging.FileHandler
                ):
                    handler.setLevel(level)
    
    def log_llm_prompt(self, model: str, prompt: str, step_id: Optional[str] = None) -> None:
        """
        Log an LLM prompt at the debug level.
        
        Args:
            model: The model being used
            prompt: The prompt being sent
            step_id: Optional step ID for context
        """
        logger = self.get_logger("llm")
        context = f" for step {step_id}" if step_id else ""
        logger.debug(f"LLM PROMPT{context} (model: {model}):\n{'-'*80}\n{prompt}\n{'-'*80}")
    
    def log_llm_response(self, model: str, response: str, step_id: Optional[str] = None) -> None:
        """
        Log an LLM response at the debug level.
        
        Args:
            model: The model being used
            response: The response received
            step_id: Optional step ID for context
        """
        logger = self.get_logger("llm")
        context = f" for step {step_id}" if step_id else ""
        logger.debug(f"LLM RESPONSE{context} (model: {model}):\n{'-'*80}\n{response}\n{'-'*80}")
        
    def log_llm_error(self, model: str, error: Exception, raw_response: Any = None, step_id: Optional[str] = None) -> None:
        """
        Log an LLM error with the raw response for debugging.
        
        Args:
            model: The model being used
            error: The exception that occurred
            raw_response: The raw response from the model (if available)
            step_id: Optional step ID for context
        """
        logger = self.get_logger("llm")
        error_logger = self.get_logger("error")
        context = f" for step {step_id}" if step_id else ""
        
        # Log the basic error at error level
        error_logger.error(f"LLM ERROR{context} (model: {model}): {str(error)}")
        
        # Log more detailed information at debug level
        logger.debug(f"LLM ERROR DETAILS{context} (model: {model}):\n{'-'*80}\n{str(error)}\n{'-'*80}")
        
        # If we have raw response data, log it for debugging
        if raw_response is not None:
            if hasattr(raw_response, 'tool_calls') and raw_response.tool_calls:
                logger.debug(f"LLM RAW TOOL CALLS{context}:\n{'-'*80}")
                for i, tool_call in enumerate(raw_response.tool_calls):
                    logger.debug(f"Tool Call {i+1}:")
                    if hasattr(tool_call, 'args'):
                        logger.debug(f"Args: {tool_call.args}")
                    logger.debug(f"{'-'*40}")
            elif hasattr(raw_response, 'content'):
                logger.debug(f"LLM RAW CONTENT{context}:\n{'-'*80}\n{raw_response.content}\n{'-'*80}")
            else:
                try:
                    logger.debug(f"LLM RAW RESPONSE{context}:\n{'-'*80}\n{str(raw_response)}\n{'-'*80}")
                except Exception as e:
                    logger.debug(f"Could not log raw response: {e}")
    
    def debug_execution(self, message: str) -> None:
        """
        Log an execution debug message.
        
        Args:
            message: The message to log
        """
        self.get_logger("execution").debug(message)
    
    def log_execution_context(self, variables: Dict, step_id: Optional[str] = None) -> None:
        """
        Log the current execution context at the debug level.
        
        Args:
            variables: Current context variables
            step_id: Optional step ID for context
        """
        import json
        
        logger = self.get_logger("execution")
        context = f" for step {step_id}" if step_id else ""
        
        # Filter out any sensitive variables (like API keys)
        filtered_vars = {
            k: "***REDACTED***" if "key" in k.lower() or "token" in k.lower() else v
            for k, v in variables.items()
        }
        
        try:
            vars_json = json.dumps(filtered_vars, indent=2, default=str)
            logger.debug(f"EXECUTION CONTEXT{context}:\n{'-'*80}\n{vars_json}\n{'-'*80}")
        except Exception as e:
            logger.debug(f"Error serializing execution context: {e}")


# Convenience functions

def get_logger(name: str = "app") -> logging.Logger:
    """
    Get a logger from the LogManager.
    
    Args:
        name: Name of the logger to get
        
    Returns:
        The requested logger
    """
    return LogManager().get_logger(name)


def set_log_level(level: Union[int, str], name: str = "app") -> None:
    """
    Set the logging level for a logger.
    
    Args:
        level: The logging level to set
        name: Name of the logger to set the level for
    """
    LogManager().set_level(level, name)


def log_llm_prompt(model: str, prompt: str, step_id: Optional[str] = None) -> None:
    """
    Log an LLM prompt at the debug level.
    
    Args:
        model: The model being used
        prompt: The prompt being sent
        step_id: Optional step ID for context
    """
    LogManager().log_llm_prompt(model, prompt, step_id)


def log_llm_response(model: str, response: str, step_id: Optional[str] = None) -> None:
    """
    Log an LLM response at the debug level.
    
    Args:
        model: The model being used
        response: The response received
        step_id: Optional step ID for context
    """
    LogManager().log_llm_response(model, response, step_id)


def log_llm_error(model: str, error: Exception, raw_response: Any = None, step_id: Optional[str] = None) -> None:
    """
    Log an LLM error with the raw response for debugging.
    
    Args:
        model: The model being used
        error: The exception that occurred
        raw_response: The raw response from the model (if available)
        step_id: Optional step ID for context
    """
    LogManager().log_llm_error(model, error, raw_response, step_id)


def debug_execution(message: str) -> None:
    """
    Log an execution debug message.
    
    Args:
        message: The message to log
    """
    LogManager().debug_execution(message)


def log_execution_context(variables: Dict, step_id: Optional[str] = None) -> None:
    """
    Log the current execution context at the debug level.
    
    Args:
        variables: Current context variables
        step_id: Optional step ID for context
    """
    LogManager().log_execution_context(variables, step_id)