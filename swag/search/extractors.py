from collections.abc import Iterable
from typing import Any

from swag.search.models import OperationRecord
from swag.search.text import join_search_text, normalize_text
from swag.spec.models import ApiSpecDocument
from swag.spec.parsing import HTTP_METHODS, optional_str, string_list


def extract_operations(document: ApiSpecDocument) -> list[OperationRecord]:
    """Extract searchable API operations from a parsed spec document."""
    operations: list[OperationRecord] = []
    paths = document.raw.get("paths", {})
    if not isinstance(paths, dict):
        return operations

    for path, path_item in paths.items():
        if not isinstance(path, str) or not isinstance(path_item, dict):
            continue
        path_parameters = _parameter_names(path_item.get("parameters"))
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operations.append(_build_operation_record(path, method, operation, path_parameters))

    return operations


def _build_operation_record(
    path: str,
    method: str,
    operation: dict[str, Any],
    path_parameters: list[str],
) -> OperationRecord:
    method_upper = method.upper()
    operation_id = optional_str(operation.get("operationId"))
    summary = optional_str(operation.get("summary"))
    description = optional_str(operation.get("description"))
    tags = string_list(operation.get("tags"))
    parameters = [*path_parameters, *_parameter_names(operation.get("parameters"))]
    request_refs = _request_refs(operation)
    response_refs = _response_refs(operation)

    path_text = normalize_text(path)
    operation_id_text = normalize_text(operation_id or "")
    summary_text = normalize_text(summary or "")
    description_text = normalize_text(description or "")
    tag_text = normalize_text(" ".join(tags))
    parameter_text = normalize_text(" ".join(parameters))
    ref_text = normalize_text(" ".join([*request_refs, *response_refs]))

    return OperationRecord(
        id=f"{method_upper}:{path}",
        path=path,
        method=method_upper,
        operation_id=operation_id,
        summary=summary,
        description=description,
        tags=tags,
        parameters=_unique(parameters),
        request_refs=_unique(request_refs),
        response_refs=_unique(response_refs),
        deprecated=bool(operation.get("deprecated", False)),
        path_text=path_text,
        operation_id_text=operation_id_text,
        summary_text=summary_text,
        description_text=description_text,
        tag_text=tag_text,
        parameter_text=parameter_text,
        ref_text=ref_text,
        search_text=join_search_text(
            method_upper,
            path_text,
            operation_id_text,
            summary_text,
            description_text,
            tag_text,
            parameter_text,
            ref_text,
        ),
    )


def _request_refs(operation: dict[str, Any]) -> list[str]:
    refs = _find_refs(operation.get("requestBody"))
    parameters = operation.get("parameters")
    if isinstance(parameters, list):
        for parameter in parameters:
            if isinstance(parameter, dict) and parameter.get("in") == "body":
                refs.extend(_find_refs(parameter.get("schema")))
    return _unique(refs)


def _response_refs(operation: dict[str, Any]) -> list[str]:
    return _unique(_find_refs(operation.get("responses")))


def _find_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            refs.append(ref)
        for child in value.values():
            refs.extend(_find_refs(child))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_find_refs(item))
    return refs


def _parameter_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for parameter in value:
        if isinstance(parameter, dict):
            name = parameter.get("name")
            if isinstance(name, str):
                location = parameter.get("in")
                names.append(f"{name} {location}" if isinstance(location, str) else name)
    return _unique(names)


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))
