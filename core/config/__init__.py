#
# Copyright (c) 2023-2024 by Dribia Data Research.
# This file is part of project Brainer,
# and is released under the MIT License Agreement.
# See the LICENSE file for more information.
#
"""**Project configuration**.

This module holds both application and environmental configurations.

We use Pydantic's
`Settings <https://pydantic-docs.helpmanual.io/usage/settings/>`_
to read and parse configurations from the environment, and
`DriConfig <https://dribia.github.io/driconfig/>`_ to read and parse
YAML application configurations.

    - Application configurations:
        - Are defined as attributes in :class:`~.config.AppConfig`.
        - Do not depend on the environment.
        - Only contain nonsensible information (e.g. model parameters).
        - Are read from a YAML config file (not from the environment).
    - Environment configurations:
        - Are defined as attributes in :class:`~.config.GlobalConfig`
          or its subclasses (e.g. :class:`~.config.DevConfig`).
        - Can be environment-dependant.
        - May contain sensible information such as usernames,
          passwords or URLs to customer resources.
        - Can be loaded from a ``.env`` file in the root
          directory of the project, which **must not be added to VCS**.
          Alternatively, they can be read from environment variables.

The :obj:`.config` object should be used throughout the code to access
configuration values.

If you want to organize your application configurations into different
YAML files, you should create one interface per file, mimicking the
definition of :class:`.AppConfig`.

Finally, to override any of the environmental configuration defined in
:class:`.GlobalConfig` or its subclasses, an environment variable can
be defined in the OS, with the same name of the configuration defined
in the config class, and prefixed with the :obj:`.ENV_PREFIX`.

"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pydantic
from driconfig import DriConfig
from google.auth.transport.requests import AuthorizedSession
from pydantic import BaseSettings, DirectoryPath
from pydantic.env_settings import SettingsSourceCallable

from ..types.pydantic import SQLiteDsn
from .enums import CBModelStorage, Environment, LogLevel
from .interfaces import LoggerOptions

ENV_PREFIX = "BRAINER"
"""Environment variables prefix for project configurations.

Environment variables can be used to override any of the configurations
defined in :class:`~.config.GlobalConfig` or its subclasses.
However, to reduce the chance of having repeated variable names within
different projects, we need to add a prefix to the variable names in
order to be taken into account when building the project's
configuration.

For instance, to override the :attr:`~.config.GlobalConfig.ENV`
attribute with an environment variable, we should define:

.. code-block:: console

    $ export BRAINER_ENV=PRO

"""


class AppConfig(DriConfig):
    """**Application configurations interface**.

    This class is an interface with the project's ``config.yaml``
    configuration file.

    Interfaces representing each of the YAML file sections can be
    defined as Pydantic models in :mod:`~.config.interfaces`.

    When adding configurations in the ``config.yaml`` config file one
    should define the corresponding attribute on this model so that
    the new configuration can be accessed from code.

    Let's say we add the following section to our config file:

    .. code-block:: yaml

        TABLE_NAMES:
            - USERS:
                NAME: users
                KEY: user_id
            - ITEMS:
                NAME: items
                KEY: item_id

    At this point we can choose how deeply we define the model for our
    new configuration. Starting with the simplest definition, we could
    do:

    ::

        from typing import Any, List

        class AppConfig(DriConfig):

            ...

            TABLE_NAMES: List[Any]

    We could also give more detail about the structure of the new
    YAML section:

    ::

        from typing import Any, Dict, List

        class AppConfig(DriConfig):

            ...

            TABLE_NAMES: List[Dict[str, Dict[str, str]]]

    And finally (and recommended), we could write models to interface
    our new config section:

    ::

        # brainer.core.config.interfaces.py

        class TableConfig(BaseInterface):

            NAME: str
            KEY: str

        class TableNames(BaseInterface):

            USERS: TableConfig
            ITEMS: TableConfig

    And add it as an attribute of :class:`.AppConfig`:

    ::

        from .interfaces import TableNames

        class AppConfig(DriConfig):

            ...

            TABLE_NAMES: TableNames

    With whichever option we have chosen, now we should be able to
    access the new config section in the :obj:`.config` object:

    ::

        from brainer.core import config

        config.APP_CONFIG.TABLE_NAMES

    """

    def __init__(self):
        """This class has no initialization parameters.

        :meta private:
        """
        super(AppConfig, self).__init__()

    class Config:
        """Custom configuration class."""

        config_folder = Path(__file__).parents[2] / "config"
        """Path to the folder containing the YAML config file."""
        config_file_name = "config.yaml"
        """Name of the YAML config file."""

    LOGGER_OPTIONS: LoggerOptions
    """Options to pass to Brainer's logger
    object on creation.
    """


class GlobalConfig(BaseSettings):
    """**Environment configurations interface**.

    This class contains every environment-dependant configuration
    of the project. A few examples could be:

    * Sensible information such as usernames or passwords.
    * Path routes that might change depending on the environment.
    * Configurations that would be useful to be changed depending
      on the environment, such as the application's logging level.

    In order to add a configuration value, simply add it as an
    attribute to this class, with its corresponding type and a
    default value, if desired.

    If the default value is not informed it means that the
    configuration value is *required*. This class will search
    for the value in:

    * An ``.env`` file located at the root folder of the project.
    * An OS environment variable defined with the same name of the
      configuration, and prefixed with :obj:`.ENV_PREFIX`.

    If none of the above is found and the configuration value is
    required, an exception will be raised.

    """

    class Config:
        """Settings configuration class."""

        case_sensitive = True
        env_file: Path = Path(__file__).parents[3] / ".env"
        env_prefix = f"{ENV_PREFIX}_"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Modify sources preference wrt Pydantic defaults."""
            return env_settings, init_settings, file_secret_settings

    APP_CONFIG: AppConfig = AppConfig()
    """Application configuration object containing the attributes read
    from the YAML config file.
    """

    ENV: Optional[Environment] = Environment.DEV
    """Application environment."""

    PATH_DATA: DirectoryPath = Path(__file__).parents[3] / "data"
    """Path to the data folder."""

    PATH_DATA_DB: Path = Path("db")
    """Path to the db data sub-folder."""
    PATH_DATA_EXTERNAL: Path = Path("external")
    """Path to the external data sub-folder."""
    PATH_DATA_INTERIM: Path = Path("interim")
    """Path to the interim data sub-folder."""
    PATH_DATA_LOG: Path = Path("log")
    """Path to the log data sub-folder."""
    PATH_DATA_MODELS: Path = Path("models")
    """Path to the models sub-folder."""
    PATH_DATA_PROCESSED: Path = Path("processed")
    """Path to the processed data sub-folder."""
    PATH_DATA_RAW: Path = Path("raw")
    """Path to the raw data sub-folder."""
    PATH_DATA_RESULTS: Path = Path("results")
    """Path to the results data sub-folder."""

    @pydantic.validator(
        "PATH_DATA_DB",
        "PATH_DATA_EXTERNAL",
        "PATH_DATA_INTERIM",
        "PATH_DATA_LOG",
        "PATH_DATA_MODELS",
        "PATH_DATA_PROCESSED",
        "PATH_DATA_RAW",
        "PATH_DATA_RESULTS",
    )
    def dynamic_on_data_path(cls, v, values, config, field):
        """Make data sub-folders dynamic on the data folder value."""
        if v == field.default and "PATH_DATA" in values:
            return DirectoryPath.validate(values["PATH_DATA"] / v)
        return DirectoryPath.validate(v)

    LOG_LEVEL: LogLevel = LogLevel.INFO
    """Logging level."""
    LOG_FILENAME: str = f"{ENV_PREFIX.lower()}.log"
    """Logging filename, which will be placed in
    :attr:`~.PATH_DATA_LOG`
    """

    """Path to credentials file for the Brainer BigQuery project."""
    DATABASE_NAME: str = ENV_PREFIX
    """Database name."""
    DATABASE_PATH: Optional[Path]
    """Database path."""
    DATABASE_URI: Optional[str]
    """Database URI."""
    GCLOUD_PROJECT_ID: Optional[str] = "brainer-390415"
    """BigQuery project ID."""
    GCLOUD_DATASET_ANALYTICS: Optional[str] = "dribia"
    """BigQuery Analytics dataset name."""
    GCLOUD_DATASET_ANALYTICS_ML: Optional[str] = "dribia_ml"
    """BigQuery Analytics ML dataset name."""
    GCLOUD_BUCKET_NAME: Optional[str] = "brainer_models"
    """Bucket name."""
    BIGQUERY_HTTP: AuthorizedSession | None = None
    """BigQuery _http."""

    STORAGE_BACKEND: Optional[CBModelStorage] = CBModelStorage.LOCAL
    """Storage backend."""

    SCHEMAS_PATH = Path(__file__).parents[3] / "schemas_json"
    """Path to the folder containing the JSON schemas for tables
    to create via python.
    """
    DATE_START: Optional[date] = date.fromisoformat("2023-05-15")
    """Date from which to start the data retrieval."""

    @pydantic.validator("DATE_START", always=True)
    def parse_date_start(cls, v: Optional[str]) -> date:
        """Parse date start."""
        if isinstance(v, str):
            return date.fromisoformat(v)
        elif isinstance(v, date):
            return v
        else:
            raise ValueError("Date start must be a string or a date.")

    @pydantic.validator("DATABASE_PATH")
    def dynamic_on_data_db_path(cls, v: Optional[Path], values: Dict[str, Any]) -> Path:
        """Make the DB path dynamic on the data/db folder."""
        if v is not None:
            return v
        return values.get("PATH_DATA_DB", Path(".")) / values["DATABASE_NAME"]

    @pydantic.validator("DATABASE_URI", always=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble the database connection URI."""
        if isinstance(v, str):
            return v
        return SQLiteDsn(
            None, scheme="sqlite", path=str(values["DATABASE_PATH"].absolute())
        )


class DevConfig(GlobalConfig):
    """Configuration overrides for the DEV environment."""

    class Config:
        """Config overrides for the DEV environment."""

        env_prefix: str = f"{ENV_PREFIX}_{Environment.DEV.name}_"

    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    """The log level is set to :attr:`~.config.enums.LogLevel.DEBUG`
    in the :attr:`~.config.enums.Environment.DEV` environment.
    """


class ProConfig(GlobalConfig):
    """Configuration overrides for the PRO environment."""

    LOG_LEVEL: LogLevel = LogLevel.INFO
    """The log level is set to :attr:`~.config.enums.LogLevel.INFO`
    in the :attr:`~.config.enums.Environment.PRO` environment.
    """


class UnitTestConfig(GlobalConfig):
    """Configuration overrides for the UNITTEST environment."""

    LOG_LEVEL: LogLevel = LogLevel.TRACE
    """The log level is set to :attr:`~.config.enums.LogLevel.TRACE`
    in the :attr:`~.config.enums.Environment.UNITTEST` environment.
    """
    DATABASE_URI: SQLiteDsn = SQLiteDsn(None, scheme="sqlite", path=":memory:")
    """We use an in-memory SQLite database in the
    :attr:`~.config.enums.Environment.PRO` environment.
    """
    BIGQUERY_HTTP: AuthorizedSession = AuthorizedSession("")


class FactoryConfig:
    """**Configuration factory**.

    Returns a config instance depending on the ENV variable.

    """

    def __init__(self, env: Environment):
        """Configuration factory parameters.

        The configuration factory depends only on the defined
        environment.

        Args:
            env: Environment.

        """
        self.env: Environment = env

    def __call__(self, **values):
        """Instances of the factory config are callable.

        Every keyword parameter passed when calling the instance
        will be used as an initialization parameter of the
        corresponding configuration class instance.

        Args:
            **values: Keyword arguments for the config instance.

        Returns: The configuration class instance of the corresponding
          environment.

        """
        if self.env is Environment.DEV:
            return DevConfig(**values)
        elif self.env is Environment.PRO:
            return ProConfig(**values)
        elif self.env is Environment.UNITTEST:
            return UnitTestConfig(**values)
        else:
            raise RuntimeError("Environment not recognized.")


config = FactoryConfig(GlobalConfig().ENV)(**GlobalConfig().dict(exclude_unset=True))
"""Configuration object to be used anywhere in the project's code.

It contains both the application and the environment configurations:

.. testsetup::

    from brainer.core.config import AppConfig
    from brainer.core.config import GlobalConfig

.. doctest::

    >>> from brainer.core import config
    ...
    >>> isinstance(config, GlobalConfig)
    True
    >>> isinstance(config.APP_CONFIG, AppConfig)
    True

:meta hide-value:
"""
