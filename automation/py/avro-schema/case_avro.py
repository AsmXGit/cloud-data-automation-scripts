import typing
import casefy
from .fields.field_utils import ENUM

# Define case transformation constants
CAMELCASE = "camelcase"
CAPITALCASE = "capitalcase"
CONSTCASE = "constcase"
LOWERCASE = "lowercase"
PASCALCASE = "pascalcase"
PATHCASE = "pathcase"
SNAKECASE = "snakecase"
SPINALCASE = "spinalcase"
UPPERSPINALCASE = "upperkebabcase"
TRIMCASE = "trimcase"
UPPERCASE = "uppercase"
ALPHANUMCASE = "alphanumcase"

# Map case types to case transformation functions
CASE_TO_FUNC = {
    CAMELCASE: casefy.camelcase,
    CAPITALCASE: casefy.capitalcase,
    CONSTCASE: casefy.constcase,
    LOWERCASE: casefy.lowercase,
    PASCALCASE: casefy.pascalcase,
    PATHCASE: lambda value: casefy.separatorcase(value, separator="/"),
    SNAKECASE: casefy.snakecase,
    SPINALCASE: casefy.kebabcase,
    UPPERSPINALCASE: casefy.upperkebabcase,
    TRIMCASE: str.strip,
    UPPERCASE: casefy.uppercase,
    ALPHANUMCASE: casefy.alphanumcase,
}

def case_item(item: typing.Dict[str, typing.Any], case_type: str) -> typing.Dict[str, typing.Any]:
    """
    Transforms the case of 'name' fields in a schema item dictionary based on the specified case type.
    
    Args:
        item: A dictionary representing a field or item in the schema.
        case_type: The type of case transformation to apply.

    Returns:
        A new dictionary with transformed 'name' field values and nested case transformations applied where appropriate.
    """
    case_func = CASE_TO_FUNC.get(case_type)
    if not case_func:
        raise ValueError(f"Unsupported case type '{case_type}'. Valid types are: {list(CASE_TO_FUNC.keys())}")

    transformed_item = {}
    for key, value in item.items():
        if key == "name":
            # Apply case transformation to the 'name' key
            transformed_item[key] = case_func(value)
        elif isinstance(value, dict) and "name" in value:
            # Recurse into nested records
            transformed_item[key] = case_record(value, case_type=case_type)
        elif isinstance(value, list):
            # Apply transformation to each element in lists of dictionaries
            transformed_item[key] = [
                case_record(element, case_type=case_type) if isinstance(element, dict) else element
                for element in value
            ]
        else:
            # Preserve other fields as-is
            transformed_item[key] = value

    return transformed_item

def case_record(avro_schema_dict: typing.Dict[str, typing.Any], case_type: str) -> typing.Dict[str, typing.Any]:
    """
    Transforms the case of 'fields' in a schema record dictionary based on the specified case type.
    
    Args:
        avro_schema_dict: A dictionary representing the entire schema or a nested schema record.
        case_type: The type of case transformation to apply.

    Returns:
        A new dictionary with transformed field names and nested structures.
    """
    if avro_schema_dict.get("type") == ENUM:
        # Enums are left unchanged, as their names should not be case-transformed
        return avro_schema_dict

    fields = avro_schema_dict.get("fields")
    if fields:
        avro_schema_dict["fields"] = [case_item(field, case_type) for field in fields]

    return avro_schema_dict if fields else case_item(avro_schema_dict, case_type)
