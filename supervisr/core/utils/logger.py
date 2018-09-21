"""supervisr core logger"""
from logging import NOTSET, addLevelName, getLoggerClass, setLoggerClass
from pprint import pprint

# Default levels:
# Level		Numeric value
# CRITICAL	50
# ERROR		40
# WARNING	30
# INFO		20
# DEBUG		10
# NOTSET	0

SUCCESS = 25

class SupervisrLogger(getLoggerClass()):
    """Logger class with custom levels for CLI interaction"""

    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)
        addLevelName(SUCCESS, "SUCCESS")

    def success(self, msg, *args, **kwargs):
        """Logging method for CLI success messages"""
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

    # pylint: disable=unused-argument
    def pretty(self, msg, *args, **kwargs):
        """Print message with pprint"""
        pprint(msg)


setLoggerClass(SupervisrLogger)
