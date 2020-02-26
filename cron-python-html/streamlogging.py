import sys
from typing import TextIO


class Logger:
    def __init__(self, out=sys.stdout, warn=sys.stdout, err=sys.stderr):
        self._out = out
        self._warn = warn
        self._err = err
        self._subsections = []
        self.prefix_warn = "~ WARN ~ " if self._warn is self._out else ""
        self.prefix_err = "# ERROR # " if self._err is self._out else ""

    def _write(self, stream: TextIO, msg: str, prefix: str = ""):
        if prefix:
            stream.write(prefix)

        if len(self._subsections):
            stream.write("[")
            stream.write(", ".join(self._subsections))
            stream.write("] ")

        stream.write(msg)
        stream.write("\n")

    def out(self, msg: str):
        self._write(self._out, msg)

    def warn(self, msg: str):
        self._write(self._warn, msg, self.prefix_warn)

    def err(self, msg: str):
        self._write(self._err, msg, self.prefix_warn)

    def flush(self):
        self._out.flush()

        for stream in (self._warn, self._err):
            if stream is not self._out:
                stream.flush()

    def sublogger(self, subsectionname: str) -> "Logger":
        subl = Logger(out=self._out, warn=self._warn, err=self._err)
        subl._subsections.extend(self._subsections + [subsectionname])
        return subl
