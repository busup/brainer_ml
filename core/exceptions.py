#
# Copyright (c) 2023-2024 by Dribia Data Research.
# This file is part of project Brainer,
# and is released under the MIT License Agreement.
# See the LICENSE file for more information.
#
"""**Custom exceptions**.

Contains definitions for any custom exception raised
by ``brainer``.

Exceptions should consistently inherit the Python Language native ones.
This is, if you write a custom exception for an argument error to
one of your package functions, it should inherit from :exc:`ValueError`.

"""


class NotExistingTable(KeyError):
    """Error raised when table_id does not exist."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class InvalidTableName(ValueError):
    """Error raised when table name is not valid."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class ZeroWeightsError(ZeroDivisionError):
    """Error raised when table name is not valid."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class NotExistingJSONSchema(KeyError):
    """Error raised when a json schema does not exist."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class NotExistingVersion(ValueError):
    """Error raised when the version of the weights does not exist."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class InvalidCopernicusCredentials(ValueError):
    """Error raised when Copernicus API credentials are invalid."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg


class CatBoostError(ValueError):
    """Error raised when there is a CatBoost Error."""

    def __init__(self, msg):
        """Set error instance parameters."""
        self.msg = msg
