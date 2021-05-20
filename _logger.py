import logging


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent logging from propagating to the root logger
        logger.propagate = 0
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
        console.setFormatter(formatter)
    return logger
