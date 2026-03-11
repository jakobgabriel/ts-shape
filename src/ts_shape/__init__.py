"""ts-shape: Shape your timeseries data."""

import logging
from logging import NullHandler

# Library best practice: add NullHandler so that consuming applications
# control logging output.  See https://docs.python.org/3/howto/logging.html
logging.getLogger(__name__).addHandler(NullHandler())
