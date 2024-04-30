#
# Copyright (c) 2023-2024 by Dribia Data Research.
# This file is part of project Brainer,
# and is released under the MIT License Agreement.
# See the LICENSE file for more information.
#
"""**Core package**.

Basic core functionality involving error definition, config parsing,
and general utility functions.

A good rule of thumb is that methods from the outside of the core
package will use core package methods, but core package methods
will never use methods from the outside.

We provide the config and logger instance at this first level to
reduce repetition:

.. doctest::

   >>> from brainer.core import config

instead of:

::

   >>> from brainer.core.config import config

However, other objects (e.g. types) must be accessed from their
own submodule:

.. doctest::

   >>> from brainer.core.types.pydantic import SQLiteDsn

"""

from . import exceptions, types, utils
from .config import config
from .logger import logger

__all__ = ["config", "exceptions", "logger", "types", "utils"]
