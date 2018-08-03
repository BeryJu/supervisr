"""supervisr core logger"""

from logging import NOTSET, addLevelName, getLoggerClass, setLoggerClass

# Default levels:
# Level		Numeric value
# CRITICAL	50
# ERROR		40
# WARNING	30
# INFO		20
# DEBUG		10
# NOTSET	0


class SupervisrLogger(getLoggerClass()):
    """Logger class with custom levels for CLI interaction"""

    SUCCESS = 25

    def __init__(self, name, level=NOTSET):
        super().__init__(name, level)

        addLevelName(self.SUCCESS, "SUCCESS")

    def success(self, msg, *args, **kwargs):
        """Logging method for CLI success messages"""
        if self.isEnabledFor(self.SUCCESS):
            self._log(self.SUCCESS, msg, args, **kwargs)


setLoggerClass(SupervisrLogger)
