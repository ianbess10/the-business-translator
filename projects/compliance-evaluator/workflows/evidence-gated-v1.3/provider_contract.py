"""Static audit for the conservative Structured Outputs subset used by v1.3."""

from __future__ import annotations

from typing import Any


ALLOWED_SCHEMA_KEYWORDS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
}
ALLOWED_TYPES = {"string", "number", "boolean", "integer", "object", "array"}
FORBIDDEN_COMPOSITION_KEYWORDS = {
    "allOf",
    "not",
    "dependentRequired",
    "dependentSchemas",
    "if",
    "then",
    "else",
}


def provider_subset_errors(response_format: dict[str, Any]) -> list[str]:
    """Return exact paths for provider-subset violations without making an API call."""

    errors: list[str] = []
    if set(response_format) != {"name", "strict", "schema"}:
        errors.append("response_format: wrapper keys must be name, strict and schema")
    if not isinstance(response_format.get("name"), str) or not response_format.get("name"):
        errors.append("response_format.name: must be a non-empty string")
    if response_format.get("strict") is not True:
        errors.append("response_format.strict: must be true")
    schema = response_format.get("schema")
    if not isinstance(schema, dict):
        errors.append("response_format.schema: must be an object")
        return errors
    if schema.get("type") != "object":
        errors.append("response_format.schema.type: root must be object")
    errors.extend(_schema_errors(schema, "response_format.schema"))
    return errors


def _schema_errors(schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    forbidden = sorted(set(schema) & FORBIDDEN_COMPOSITION_KEYWORDS)
    for keyword in forbidden:
        errors.append(f"{path}.{keyword}: unsupported composition keyword")
    for keyword in sorted(set(schema) - ALLOWED_SCHEMA_KEYWORDS):
        if keyword not in FORBIDDEN_COMPOSITION_KEYWORDS:
            errors.append(f"{path}.{keyword}: keyword is outside the v1.3 allowlist")

    schema_type = schema.get("type")
    if schema_type not in ALLOWED_TYPES:
        errors.append(f"{path}.type: unsupported or missing type {schema_type!r}")
        return errors

    enum = schema.get("enum")
    if enum is not None and (not isinstance(enum, list) or not enum):
        errors.append(f"{path}.enum: must be a non-empty list")

    if schema_type == "object":
        properties = schema.get("properties")
        required = schema.get("required")
        if not isinstance(properties, dict):
            errors.append(f"{path}.properties: object schemas require properties")
            properties = {}
        if schema.get("additionalProperties") is not False:
            errors.append(f"{path}.additionalProperties: must be false")
        if not isinstance(required, list):
            errors.append(f"{path}.required: all object fields must be required")
            required = []
        if set(required) != set(properties):
            errors.append(f"{path}.required: must contain every property exactly once")
        if len(required) != len(set(required)):
            errors.append(f"{path}.required: contains duplicate field names")
        for name, child in properties.items():
            child_path = f"{path}.properties.{name}"
            if not isinstance(child, dict):
                errors.append(f"{child_path}: property schema must be an object")
            else:
                errors.extend(_schema_errors(child, child_path))
    elif any(key in schema for key in ("properties", "required", "additionalProperties")):
        errors.append(f"{path}: non-object schema contains object-only keywords")

    if schema_type == "array":
        items = schema.get("items")
        if not isinstance(items, dict):
            errors.append(f"{path}.items: array schemas require one item schema")
        else:
            errors.extend(_schema_errors(items, f"{path}.items"))
    elif "items" in schema:
        errors.append(f"{path}.items: non-array schema contains items")
    return errors


def assert_provider_subset(response_format: dict[str, Any]) -> None:
    errors = provider_subset_errors(response_format)
    if errors:
        raise ValueError("Provider-subset audit failed: " + "; ".join(errors))
