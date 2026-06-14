from typing import Any

from swag.operation.models import (
    MediaTypeSchema,
    OperationDetail,
    ParameterDetail,
    RequestBodyDetail,
    ResponseDetail,
)
from swag.operation.ref_resolver import resolve_refs
from swag.spec.models import ApiSpecDocument
from swag.spec.parsing import HTTP_METHODS, optional_str, string_list

_PARAMETER_META_KEYS = {"name", "in", "required", "description", "schema"}


def extract_operation_detail(
    document: ApiSpecDocument,
    service_id: str,
    method: str,
    path: str,
) -> OperationDetail | None:
    """Build the full contract of one operation, with local ``$ref`` resolved.

    Returns ``None`` when the method+path pair is absent from the document.
    """
    method_lower = method.lower()
    if method_lower not in HTTP_METHODS:
        return None

    paths = document.raw.get("paths")
    if not isinstance(paths, dict):
        return None
    path_item = paths.get(path)
    if not isinstance(path_item, dict):
        return None
    operation = path_item.get(method_lower)
    if not isinstance(operation, dict):
        return None

    root = document.raw
    is_swagger2 = document.spec_version == "swagger2"

    parameters, body_from_params = _collect_parameters(path_item, operation, root, is_swagger2)
    request_body = body_from_params if is_swagger2 else _openapi3_request_body(operation.get("requestBody"), root)

    return OperationDetail(
        service_id=service_id,
        path=path,
        method=method.upper(),
        operation_id=optional_str(operation.get("operationId")),
        summary=optional_str(operation.get("summary")),
        description=optional_str(operation.get("description")),
        tags=string_list(operation.get("tags")),
        deprecated=bool(operation.get("deprecated", False)),
        parameters=parameters,
        request_body=request_body,
        responses=_collect_responses(operation.get("responses"), root, is_swagger2),
    )


def _collect_parameters(
    path_item: dict[str, Any],
    operation: dict[str, Any],
    root: dict[str, Any],
    is_swagger2: bool,
) -> tuple[list[ParameterDetail], RequestBodyDetail | None]:
    """Merge path-level and operation-level parameters (operation wins by name+in).

    For Swagger 2 the ``in: body`` parameter is lifted into a RequestBodyDetail.
    Each parameter is fully ``$ref``-resolved before reading its schema.
    """
    merged: dict[tuple[str, str], ParameterDetail] = {}
    body: RequestBodyDetail | None = None
    for raw_parameter in [*_as_list(path_item.get("parameters")), *_as_list(operation.get("parameters"))]:
        parameter = resolve_refs(raw_parameter, root)
        name = parameter.get("name") if isinstance(parameter, dict) else None
        location = parameter.get("in") if isinstance(parameter, dict) else None
        if not isinstance(name, str) or not isinstance(location, str):
            continue
        if is_swagger2 and location == "body":
            body = _swagger2_body(parameter)
            continue
        merged[(name, location)] = _build_parameter(parameter, is_swagger2)
    return list(merged.values()), body


def _build_parameter(parameter: dict[str, Any], is_swagger2: bool) -> ParameterDetail:
    if is_swagger2:
        json_schema: dict[str, Any] | None = {
            key: value for key, value in parameter.items() if key not in _PARAMETER_META_KEYS
        } or None
    else:
        schema = parameter.get("schema")
        json_schema = schema if isinstance(schema, dict) else None
    return ParameterDetail(
        name=str(parameter["name"]),
        location=str(parameter["in"]),
        required=bool(parameter.get("required", False)),
        description=optional_str(parameter.get("description")),
        json_schema=json_schema,
    )


def _swagger2_body(parameter: dict[str, Any]) -> RequestBodyDetail:
    schema = parameter.get("schema")
    content = (
        [MediaTypeSchema(content_type="application/json", json_schema=schema)] if isinstance(schema, dict) else []
    )
    return RequestBodyDetail(
        description=optional_str(parameter.get("description")),
        required=bool(parameter.get("required", False)),
        content=content,
    )


def _openapi3_request_body(request_body: Any, root: dict[str, Any]) -> RequestBodyDetail | None:
    resolved = resolve_refs(request_body, root)
    if not isinstance(resolved, dict):
        return None
    return RequestBodyDetail(
        description=optional_str(resolved.get("description")),
        required=bool(resolved.get("required", False)),
        content=_media_types(resolved.get("content")),
    )


def _collect_responses(responses: Any, root: dict[str, Any], is_swagger2: bool) -> list[ResponseDetail]:
    if not isinstance(responses, dict):
        return []
    details: list[ResponseDetail] = []
    for status_code, response in responses.items():
        resolved = resolve_refs(response, root)
        if not isinstance(resolved, dict):
            continue
        if is_swagger2:
            schema = resolved.get("schema")
            content = (
                [MediaTypeSchema(content_type="application/json", json_schema=schema)]
                if isinstance(schema, dict)
                else []
            )
        else:
            content = _media_types(resolved.get("content"))
        details.append(
            ResponseDetail(
                status_code=str(status_code),
                description=optional_str(resolved.get("description")),
                content=content,
            )
        )
    return details


def _media_types(content: Any) -> list[MediaTypeSchema]:
    """Build media-type schemas from already ``$ref``-resolved content."""
    if not isinstance(content, dict):
        return []
    media_types: list[MediaTypeSchema] = []
    for content_type, media in content.items():
        if not isinstance(content_type, str) or not isinstance(media, dict):
            continue
        schema = media.get("schema")
        media_types.append(
            MediaTypeSchema(content_type=content_type, json_schema=schema if isinstance(schema, dict) else None)
        )
    return media_types


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
