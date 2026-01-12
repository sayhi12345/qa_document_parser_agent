import os
import logging
import json
import threading

ENV = os.getenv("ENV_PRESET", "prod")


class JSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        # 確保 msg 是 dict，不要二次 json.dumps()
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, ensure_ascii=False)  # 確保能輸出 emoji & 中文
        return super().format(record)


class Logger(object):
    # Singleton
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, class_name: str, log_path: str):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize(class_name, log_path)
        return cls._instance

    def _initialize(self, class_name: str, log_path: str):
        """ 初始化 Logger，確保只執行一次 """
        logging.basicConfig(filename=log_path, format='%(message)s', encoding='utf-8')
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel("INFO" if (ENV == "prod" or ENV == "test") else "DEBUG")

        # 避免重複添加 handler
        if not self.logger.handlers:
            loggingStreamHandler = logging.StreamHandler()
            loggingStreamHandler.setFormatter(JSONFormatter())
            self.logger.addHandler(loggingStreamHandler)
    
    def _log(self, level, status, url, message):
        msg = {
            "status": status,
            "content": {
                "url": url,
                "message": message,
            }
        }

        if level == "info":
            self.logger.info(msg)
        elif level == "warning":
            self.logger.warning(msg)
        elif level == "error":
            self.logger.error(msg)
        elif level == "debug":
            self.logger.debug(msg)
        else:
            raise ValueError("Invalid log level")
    # TODO: add more logging keys if needed
    def info(self, status, url, message):
        self._log("info", status, url, message)

    def warning(self, status, url, message):
        self._log("warning", status, url, message)

    def error(self, status, url, message):
        self._log("error", status, url, message)

    def debug(self, status, url, message):
        self._log("debug", status, url, message)

def get_logger(name: str, log_dir: str = None) -> Logger:
    """
    Factory function to create or retrieve a logger instance.
    
    Args:
        name: Logger name (typically module name)
        log_dir: Optional log directory override
        
    Returns:
        Logger instance
    """
    from datetime import datetime
    from config.misc import settings as misc_settings
    import os
    
    if log_dir is None:
        log_dir = misc_settings.log_dir
    
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    
    return Logger(name, log_path)


if __name__ == "__main__":
    pass