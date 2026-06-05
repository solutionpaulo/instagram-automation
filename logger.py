"""Logging estruturado com níveis e timestamps.

Substitui todos os print() da aplicação. Use get_logger() para obter
a instância global e setup_logger() para configurar o nível.
"""

import logging
import sys
from typing import Optional

LOG_LEVELS = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARN": logging.WARNING, "ERROR": logging.ERROR}

_logger: Optional[logging.Logger] = None


def setup_logger(name: str = "ig_automation", level: str = "INFO") -> logging.Logger:
    """Configura e retorna o logger global da aplicação.

    Args:
        name: Nome do logger.
        level: Nível de log (DEBUG, INFO, WARN, ERROR).

    Returns:
        Instância configurada do logging.Logger.
    """
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-5s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Obtém o logger global, criando-o se necessário."""
    if _logger is None:
        return setup_logger()
    return _logger
