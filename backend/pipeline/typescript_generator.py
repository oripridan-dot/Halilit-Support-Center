"""
TypeScript Type Generator - Auto-generates frontend types from Pydantic models.

Ensures perfect sync between backend models and frontend TypeScript types.
"""

from pathlib import Path
from datetime import datetime
from typing import get_type_hints, get_origin, get_args, Any, Union, List, Dict, Optional
import inspect

from .models import (
    OptimizedProduct,
    BrandCatalog,
    CatalogIndex,
    BrandSummary,
    TierLevel,
    StockStatus,
)


def python_type_to_typescript(python_type: Any, optional: bool = False) -> str:
    """Convert Python type annotation to TypeScript type."""

    origin = get_origin(python_type)

    # Handle Optional
    if origin is Union:
        args = get_args(python_type)
        # Check if it's Optional (Union with None)
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            return python_type_to_typescript(non_none_args[0], optional=True)
        else:
            types = [python_type_to_typescript(a) for a in non_none_args]
            return " | ".join(types) + (" | null" if optional else "")

    # Handle List
    if origin is list:
        args = get_args(python_type)
        if args:
            inner = python_type_to_typescript(args[0])
            return f"{inner}[]"
        return "any[]"

    # Handle Dict
    if origin is dict:
        args = get_args(python_type)
        if len(args) == 2:
            key_type = python_type_to_typescript(args[0])
            val_type = python_type_to_typescript(args[1])
            return f"Record<{key_type}, {val_type}>"
        return "Record<string, any>"

    # Handle basic types
    type_map = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
        Any: "any",
    }

    if python_type in type_map:
        result = type_map[python_type]
        return f"{result} | null" if optional else result

    # Handle enums
    if hasattr(python_type, '__members__'):
        values = [f'"{v.value}"' for v in python_type]
        return " | ".join(values)

    # Handle nested models
    if hasattr(python_type, '__annotations__'):
        return python_type.__name__

    # Fallback
    return "any"


def model_to_interface(model_class: type) -> str:
    """Convert a Pydantic model to TypeScript interface."""

    lines = [f"export interface {model_class.__name__} {{"]

    # Get type hints
    hints = {}
    for cls in reversed(model_class.__mro__):
        if hasattr(cls, '__annotations__'):
            hints.update(cls.__annotations__)

    # Get field info from Pydantic
    fields = {}
    if hasattr(model_class, 'model_fields'):
        fields = model_class.model_fields

    for field_name, field_type in hints.items():
        if field_name.startswith('_'):
            continue

        # Check if optional
        is_optional = False
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            if type(None) in args:
                is_optional = True

        # Check if has default
        if field_name in fields:
            field_info = fields[field_name]
            if hasattr(field_info, 'default') and field_info.default is not None:
                is_optional = True

        ts_type = python_type_to_typescript(field_type)
        optional_marker = "?" if is_optional else ""

        lines.append(f"  {field_name}{optional_marker}: {ts_type};")

    lines.append("}")
    return "\n".join(lines)


def generate_types(output_path: Path) -> None:
    """Generate TypeScript types file from Pydantic models."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Header
    content = [
        "/**",
        " * Auto-generated TypeScript types from Pydantic models.",
        f" * Generated: {datetime.utcnow().isoformat()}",
        " * DO NOT EDIT MANUALLY - run `python -m backend.pipeline types` to regenerate",
        " */",
        "",
    ]

    # Enums
    content.append("// Enums")
    content.append("")

    content.append(
        "export type TierLevel = 'diamond' | 'gold' | 'silver' | 'bronze';")
    content.append("")

    content.append(
        "export type StockStatus = 'in_stock' | 'out_of_stock' | 'pre_order' | 'discontinued' | 'unknown';")
    content.append("")

    # Interfaces
    content.append("// Interfaces")
    content.append("")

    # Image type (inline for simplicity)
    content.append("export interface ImageAsset {")
    content.append("  url: string;")
    content.append("  alt: string;")
    content.append("  width?: number | null;")
    content.append("  height?: number | null;")
    content.append("}")
    content.append("")

    # Spec item
    content.append("export interface SpecItem {")
    content.append("  key: string;")
    content.append("  value: string;")
    content.append("  unit?: string;")
    content.append("}")
    content.append("")

    # Main models
    models = [OptimizedProduct, BrandSummary, BrandCatalog, CatalogIndex]

    for model in models:
        content.append(model_to_interface(model))
        content.append("")

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))


if __name__ == "__main__":
    from .config import config
    generate_types(config.TYPES_OUTPUT_PATH)
    print(f"Generated types at {config.TYPES_OUTPUT_PATH}")
