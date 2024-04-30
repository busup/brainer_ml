#
# Copyright (c) 2023-2024 by Dribia Data Research.
# This file is part of project Brainer,
# and is released under the MIT License Agreement.
# See the LICENSE file for more information.
#
"""**Custom Pydantic type definitions**.

This module contains custom types based on
`Pydantic <https://pydantic-docs.helpmanual.io/>`_.

"""

import re
import typing
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Pattern, Set

if TYPE_CHECKING:  # pragma: nocover
    from pydantic.fields import ModelField
    from pydantic.main import BaseConfig
    from pydantic.typing import AnyCallable

    CallableGenerator = Generator[AnyCallable, None, None]

from pydantic import utils, validators
from pydantic.errors import (
    UrlExtraError,
    UrlHostError,
    UrlSchemeError,
    UrlSchemePermittedError,
)

_sqlite_uri_regex_cache = None


def sqlite_uri_regex() -> Pattern[str]:
    """Regular expression for SQLite URIs."""
    global _sqlite_uri_regex_cache
    if _sqlite_uri_regex_cache is None:
        _sqlite_uri_regex_cache = re.compile(
            r"(?:(?P<scheme>[a-z][a-z0-9+\-.]+)://)?"  # scheme
            r"(?P<host>/)?"  # host needs to be '/'
            r"(?P<path>[^\s?#]*)?"  # path
            r"(?:\?(?P<query>[^\s#]+))?",  # query
            re.IGNORECASE,
        )
    return _sqlite_uri_regex_cache


class SQLiteDsn(str):
    """SQLite URI validator."""

    strip_whitespace = True
    """Split according to blanks."""
    min_length = 1
    """Minimum length."""
    max_length = 2**16
    """Maximum length."""
    allowed_schemes: Set[str] = {"sqlite"}
    """Set of allowed schemes."""

    __slots__ = ("scheme", "path", "query")

    def __new__(cls, uri: Optional[str], **kwargs) -> "SQLiteDsn":
        """New method following Pydantic's AnyUrl pattern."""
        return str.__new__(cls, cls.build(**kwargs) if uri is None else uri)

    def __init__(
        self,
        url: Optional[str],
        *,
        scheme: str,
        path: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        """Instance attributes configuration.

        Args:
            url: SQLite URI.
            scheme: SQLite URI scheme (sqlite, sqlite2 or file).
            path: SQLite URI path to the SQLite DB file.
            query: Optional query for connection parameters.
        """
        str.__init__(url)
        self.scheme = scheme
        """SQLite URI scheme (sqlite, sqlite2 or file)."""
        self.path = path
        """SQLite URI path to the SQLite DB file."""
        self.query = query
        """Optional query for connection parameters."""

    @classmethod
    def build(
        cls,
        *,
        scheme: str,
        path: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs: str,
    ) -> str:
        """Build the SQLite URI string from its parts.

        Args:
            scheme: SQLite URI scheme (sqlite, sqlite2 or file).
            path: SQLite URI path to the SQLite DB file.
            query: Optional query for connection parameters.
            kwargs: Other arguments.
        """
        url = scheme + "://"  # Normal scheme specification
        if path:
            url += "/"  # Host is then '/'
            url += path
        if query:
            url += "?" + query
        return url

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        """Necessary method for Pydantic validators."""
        utils.update_not_none(
            field_schema,
            minLength=cls.min_length,
            maxLength=cls.max_length,
            format="uri",
        )

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        """Necessary method for Pydantic validators."""
        yield cls.validate

    @classmethod
    def validate(
        cls, value: Any, field: "ModelField", config: "BaseConfig"
    ) -> "SQLiteDsn":
        """Validator method."""
        if value.__class__ == cls:
            return value
        value = validators.str_validator(value)
        if cls.strip_whitespace:
            value = value.strip()
        url: str = typing.cast(
            str, validators.constr_length_validator(value, field, config)
        )

        m = sqlite_uri_regex().match(url)
        assert m, "URL regex failed unexpectedly"

        parts = m.groupdict()
        parts = cls.validate_parts(parts)

        if m.end() != len(url):
            raise UrlExtraError(extra=url[m.end() :])

        return cls(
            url,
            scheme=parts["scheme"],
            path=parts["path"],
            query=parts["query"],
        )

    @classmethod
    def validate_parts(cls, parts: Dict[str, str]) -> Dict[str, str]:
        """Validate the SQLite URI parts."""
        scheme = parts["scheme"]
        if scheme is None:
            raise UrlSchemeError()

        if cls.allowed_schemes and scheme.lower() not in cls.allowed_schemes:
            raise UrlSchemePermittedError(cls.allowed_schemes)

        if parts["host"] is None:
            raise UrlHostError()

        return parts

    def __repr__(self) -> str:
        """Nicely reproduce instances."""
        extra = ", ".join(
            f"{n}={getattr(self, n)!r}"
            for n in self.__slots__
            if getattr(self, n) is not None
        )
        return f"{self.__class__.__name__}({super().__repr__()}, {extra})"
