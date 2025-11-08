import logging


def _make_logger():
    logger = logging.getLogger("starter_repo2")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = _make_logger()

def init_logger(*, level=logging.INFO):
    logger.setLevel(level)
    return logger
