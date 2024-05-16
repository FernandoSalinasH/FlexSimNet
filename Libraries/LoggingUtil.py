import multiprocessing
import logging
from logging.handlers import QueueHandler, QueueListener

class LoggingUtil:
    
    def worker_init(q):
        # all records from worker processes go to qh and then into q
        qh = QueueHandler(q)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(qh)
        
    def logger_init(logger_name: str, file_name: str = "app.log") -> logging.Logger:
        q = multiprocessing.Queue()

        logger = logging.getLogger(logger_name)
        logFormatter = logging.Formatter("%(asctime)s - [%(name)s][%(levelname)s] %(message)s")
    
        # Create a console handler and set the formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logFormatter)

        # Create a file handler and set the formatter
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(logFormatter)
        
        # Create a QueueListener to handle records from the queue and send them to the handlers
        ql = QueueListener(q, console_handler, file_handler)
        ql.start()

        # Set the log level of the logger
        logger.setLevel(logging.DEBUG)

        # Add the console and file handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
        return ql, q, logger