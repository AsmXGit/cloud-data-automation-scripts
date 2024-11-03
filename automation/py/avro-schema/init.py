"""
Package-level exports for Avro schema management library.

This file defines the package's public API by specifying all imports 
to be exposed when importing the package. Fields, serialization methods, 
and models are grouped logically for clarity and maintainability.
"""

# Field Types
from .fields.field_utils import (
    ARRAY,
    BOOLEAN,
    BYTES,
    DATE,
    DECIMAL,
    DOUBLE,
    ENUM,
    FIXED,
    FLOAT,
    INT,
    LOGICAL_DATE,
    LOGICAL_DATETIME_MICROS,
    LOGICAL_DATETIME_MILIS,
    LOGICAL_TIME_MICROS,
    LOGICAL_TIME_MILIS,
    LOGICAL_UUID,
    LONG,
    MAP,
    NULL,
    PYTHON_TYPE_TO_AVRO,
    RECORD,
    STRING,
    TIME_MICROS,
    TIME_MILLIS,
    TIMESTAMP_MICROS,
    TIMESTAMP_MILLIS,
    UUID,
)

# Field Classes
from .fields.fields import (
    AvroField,
    BooleanField,
    BytesField,
    ContainerField,
    DateField,
    DatetimeField,
    DatetimeMicroField,
    DecimalField,
    DictField,
    DoubleField,
    EnumField,
    FixedField,
    FloatField,
    ImmutableField,
    IntField,
    ListField,
    LiteralField,
    LongField,
    NoneField,
    RecordField,
    SelfReferenceField,
    StringField,
    TimeMicroField,
    TimeMilliField,
    TupleField,
    UnionField,
    UUIDField,
)

# Model Classes and Utilities
from .main import AvroModel
from .model_generator.generator import BaseClassEnum, ModelGenerator, ModelType

# Serialization Modules
from .serialization import AVRO, AVRO_JSON, SerializationType, deserialize, serialize

# Types and Converters
from .types import DateTimeMicro, Float32, Int32, TimeMicro, condecimal, confixed

# Public API Definition
__all__ = [
    # Core Model Classes
    "AvroModel",
    "BaseClassEnum",
    "ModelType",
    "ModelGenerator",
    
    # Data Types
    "Int32",
    "Float32",
    "TimeMicro",
    "DateTimeMicro",
    "condecimal",
    "confixed",
    
    # Primitive Field Types
    "BOOLEAN",
    "NULL",
    "INT",
    "FLOAT",
    "LONG",
    "DOUBLE",
    "BYTES",
    "STRING",
    "ARRAY",
    "ENUM",
    "MAP",
    "FIXED",
    "DATE",
    "UUID",
    "DECIMAL",
    "RECORD",
    
    # Logical Types
    "TIME_MILLIS",
    "TIME_MICROS",
    "TIMESTAMP_MILLIS",
    "TIMESTAMP_MICROS",
    "LOGICAL_DATE",
    "LOGICAL_TIME_MILIS",
    "LOGICAL_TIME_MICROS",
    "LOGICAL_DATETIME_MILIS",
    "LOGICAL_DATETIME_MICROS",
    "LOGICAL_UUID",
    
    # Avro Field Mappings
    "PYTHON_TYPE_TO_AVRO",
    
    # Field Classes
    "ImmutableField",
    "StringField",
    "IntField",
    "LongField",
    "BooleanField",
    "DoubleField",
    "FloatField",
    "BytesField",
    "NoneField",
    "ContainerField",
    "ListField",
    "TupleField",
    "DictField",
    "UnionField",
    "LiteralField",
    "FixedField",
    "EnumField",
    "SelfReferenceField",
    "DateField",
    "DatetimeField",
    "DatetimeMicroField",
    "TimeMilliField",
    "TimeMicroField",
    "UUIDField",
    "DecimalField",
    "RecordField",
    "AvroField",
    
    # Serialization
    "AVRO",
    "AVRO_JSON",
    "SerializationType",
    "serialize",
    "deserialize",
]
