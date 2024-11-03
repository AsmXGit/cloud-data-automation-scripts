import enum
import typing
import uuid
from datetime import date, datetime, time

from dacite import Config
from dateutil import parser

if typing.TYPE_CHECKING:
    from .main import AvroModel  # pragma: no cover

# Define custom types for parsing
DateTimeParseType = typing.Union[str, datetime]
DateParseType = typing.Union[str, date]
TimeParseType = typing.Union[str, time]
BytesParseType = typing.Union[str, bytes]
UUIDParseType = typing.Union[str, uuid.UUID]

def parse_datetime(value: DateTimeParseType) -> datetime:
    """
    Parses a value into a datetime object if it's a string; otherwise, returns the datetime as-is.

    Args:
        value: A string or datetime instance representing a date and time.

    Returns:
        A datetime instance parsed from the input value.
    """
    if isinstance(value, str):
        try:
            return parser.parse(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid datetime format: {value}") from e
    return value

def parse_date(value: DateParseType) -> date:
    """
    Parses a value into a date object if it's a string; otherwise, returns the date as-is.

    Args:
        value: A string or date instance.

    Returns:
        A date instance parsed from the input value.
    """
    if isinstance(value, str):
        try:
            dt = parser.parse(value)
            return dt.date()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format: {value}") from e
    return value

def parse_time(value: TimeParseType) -> time:
    """
    Parses a value into a time object if it's a string; otherwise, returns the time as-is.

    Args:
        value: A string or time instance.

    Returns:
        A time instance parsed from the input value.
    """
    if isinstance(value, str):
        try:
            dt = parser.parse(value)
            return dt.time()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time format: {value}") from e
    return value

def parse_bytes(value: BytesParseType) -> bytes:
    """
    Encodes a string into bytes; if the input is already bytes, returns it as-is.

    Args:
        value: A string or bytes instance.

    Returns:
        A bytes instance.
    """
    if isinstance(value, str):
        return value.encode()
    return value

def parse_uuid(value: UUIDParseType) -> uuid.UUID:
    """
    Converts a string into a UUID object; if the input is already a UUID, returns it as-is.

    Args:
        value: A string or UUID instance.

    Returns:
        A UUID instance parsed from the input value.
    """
    if isinstance(value, str):
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid UUID format: {value}") from e
    return value

def generate_dacite_config(model: typing.Type["AvroModel"]) -> Config:
    """
    Generates a Config object for dacite with self-reference and type hooks for parsing.

    Args:
        model: An AvroModel class from which to generate the dacite Config.

    Returns:
        A dacite Config object with customized settings for type handling.
    """
    # Ensure that the Avro schema is generated to populate model metadata
    model.generate_schema()
    
    dacite_user_config = getattr(model._metadata, 'dacite_config', None)  # Access user-defined config if available

    # Default dacite configuration settings with necessary type hooks
    dacite_config = {
        "check_types": False,
        "cast": [],
        "forward_references": {
            model._klass.__name__: model._klass,  # Reference self type in case of self-referential models
        },
        "type_hooks": {
            datetime: parse_datetime,
            date: parse_date,
            time: parse_time,
            bytes: parse_bytes,
            uuid.UUID: parse_uuid,
        },
    }

    # Integrate any user-defined dacite configurations
    if dacite_user_config:
        dacite_config.update(dacite_user_config)

    config = Config(**dacite_config)

    # Ensure casting support for specific types regardless of user configuration
    config.cast.extend([typing.Tuple, tuple, enum.Enum])  # Enforce casting to tuple and enum types
    return config
