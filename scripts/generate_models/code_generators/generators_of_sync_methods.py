import ast
import re
import typing
from ast import (
    Assign,
    Attribute,
    Call,
    Constant,
    Expr,
    For,
    FunctionDef,
    GeneratorExp,
    Load,
    Name,
    Return,
    Store,
    Tuple,
    Yield,
    comprehension,
    keyword,
)

from iprotopy.service_method_generator import (
    ServiceMethodStreamStreamFunctionGenerator as DefaultMethodStrmStrmFuncGenerator,
    ServiceMethodStreamUnaryFunctionGenerator as DefaultMethodStrmUnrFuncGenerator,
    ServiceMethodUnaryStreamFunctionGenerator as DefaultMethodUnrStrmFuncGenerator,
    ServiceMethodUnaryUnaryFunctionGenerator as DefaultMethodUnrUnrFuncGenerator,
)
from proto_schema_parser.ast import Method

from scripts.generate_models.code_generators.base_generators import (
    BaseServiceMethodGenerator,
    BaseSyncServiceAnyStreamFunctionGenerator,
    BaseSyncServiceAnyUnaryFunctionGenerator,
)

from .service_method_generator import (
    ServiceMethodGenerator as DefaultServiceMethodGenerator,
)


class ServiceMethodUnaryUnaryFunctionGenerator(
    BaseSyncServiceAnyUnaryFunctionGenerator,
    DefaultMethodUnrUnrFuncGenerator,
):
    def __get_function_body(self, method: Method) -> list[ast.stmt]:
        method_name = method.name
        request_class_name = method.input_type.type
        response_class_name = method.output_type.type
        body = [
            Assign(
                targets=[Name(id="protobuf_request", ctx=Store())],
                value=self._get_dataclass_from_protobuf_call(request_class_name),
            ),
            Assign(
                targets=[
                    Tuple(
                        elts=[
                            Name(id="response", ctx=Store()),
                            Name(id="call", ctx=Store()),
                        ],
                        ctx=Store(),
                    )
                ],
                value=Call(
                    func=Attribute(
                        value=Attribute(
                            value=Attribute(
                                value=Name(id="self", ctx=Load()),
                                attr="_stub",
                                ctx=Load(),
                            ),
                            attr=method_name,
                            ctx=Load(),
                        ),
                        attr="with_call",
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[
                        keyword(
                            arg="request",
                            value=Name(id="protobuf_request", ctx=Load()),
                        ),
                        keyword(
                            arg="metadata",
                            value=Attribute(
                                value=Name(id="self", ctx=Load()),
                                attr="_metadata",
                                ctx=Load(),
                            ),
                        ),
                    ],
                ),
            ),
            Return(
                value=Call(
                    func=Name(id="protobuf_to_dataclass", ctx=Load()),
                    args=[
                        Name(id="response", ctx=Load()),
                        Name(id=response_class_name, ctx=Load()),
                    ],
                    keywords=[],
                )
            ),
        ]
        return body

    def _get_function_body(self, method):
        body = self.__get_function_body(method)
        body[0].value.func.id = "_grpc_helpers.dataclass_to_protobuf"  # type: ignore
        body[-1].value.func.id = "_grpc_helpers.protobuf_to_dataclass"  # type: ignore
        log_request = Expr(
            value=Call(
                func=Name(id="log_request", ctx=Load()),
                args=[
                    Call(
                        func=Name(id="get_tracking_id_from_call", ctx=Load()),
                        args=[Name(id="call", ctx=Load())],
                        keywords=[],
                    ),
                    Constant(value=method.name),
                ],
                keywords=[],
            )
        )
        body.insert(-1, log_request)
        return body


class ServiceMethodStreamUnaryFunctionGenerator(
    BaseSyncServiceAnyUnaryFunctionGenerator,
    DefaultMethodStrmUnrFuncGenerator,
):
    ...


class ServiceMethodUnaryStreamFunctionGenerator(
    BaseSyncServiceAnyStreamFunctionGenerator,
    DefaultMethodUnrStrmFuncGenerator,
):
    def __get_function_body(self, method: Method) -> list[ast.stmt]:
        method_name = method.name
        request_class_name = method.input_type.type
        response_class_name = method.output_type.type
        body: list[ast.stmt] = [
            For(
                target=Name(id="response", ctx=Store()),
                iter=Call(
                    func=Attribute(
                        value=Attribute(
                            value=Name(id="self", ctx=Load()), attr="_stub", ctx=Load()
                        ),
                        attr=method_name,
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[
                        keyword(
                            arg="request",
                            value=self._get_dataclass_from_protobuf_call(
                                request_class_name
                            ),
                        ),
                        keyword(
                            arg="metadata",
                            value=Attribute(
                                value=Name(id="self", ctx=Load()),
                                attr="_metadata",
                                ctx=Load(),
                            ),
                        ),
                    ],
                ),
                body=[
                    Expr(
                        value=Yield(
                            value=Call(
                                func=Name(id="protobuf_to_dataclass", ctx=Load()),
                                args=[
                                    Name(id="response", ctx=Load()),
                                    Name(id=response_class_name, ctx=Load()),
                                ],
                                keywords=[],
                            )
                        )
                    )
                ],
                orelse=[],
            )
        ]
        return body

    def _get_function_body(self, method):
        body = self.__get_function_body(method)
        body[0].iter.keywords[0].value.func.id = "_grpc_helpers.dataclass_to_protobuf"  # type: ignore
        body[0].body[0].value.value.func.id = "_grpc_helpers.protobuf_to_dataclass"  # type: ignore
        return body


class ServiceMethodStreamStreamFunctionGenerator(
    BaseSyncServiceAnyStreamFunctionGenerator,
    DefaultMethodStrmStrmFuncGenerator,
):
    def __get_function_body(self, method: Method) -> list[ast.stmt]:
        method_name = method.name
        request_class_name = method.input_type.type
        response_class_name = method.output_type.type
        body: list[ast.stmt] = [
            For(
                target=Name(id="response", ctx=Store()),
                iter=Call(
                    func=Attribute(
                        value=Attribute(
                            value=Name(id="self", ctx=Load()), attr="_stub", ctx=Load()
                        ),
                        attr=method_name,
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[
                        keyword(
                            arg="request_iterator",
                            value=GeneratorExp(
                                elt=self._get_dataclass_from_protobuf_call(
                                    request_class_name
                                ),
                                generators=[
                                    comprehension(
                                        target=Name(id="request", ctx=Store()),
                                        iter=Name(id="requests", ctx=Load()),
                                        ifs=[],
                                        is_async=0,
                                    )
                                ],
                            ),
                        ),
                        keyword(
                            arg="metadata",
                            value=Attribute(
                                value=Name(id="self", ctx=Load()),
                                attr="_metadata",
                                ctx=Load(),
                            ),
                        ),
                    ],
                ),
                body=[
                    Expr(
                        value=Yield(
                            value=Call(
                                func=Name(id="protobuf_to_dataclass", ctx=Load()),
                                args=[
                                    Name(id="response", ctx=Load()),
                                    Name(id=response_class_name, ctx=Load()),
                                ],
                                keywords=[],
                            )
                        )
                    )
                ],
                orelse=[],
            )
        ]
        return body

    def _get_function_body(self, method):
        body = self.__get_function_body(method)
        body[0].iter.keywords[  # type: ignore
            0
        ].value.elt.func.id = "_grpc_helpers.dataclass_to_protobuf"
        body[0].body[0].value.value.func.id = "_grpc_helpers.protobuf_to_dataclass"  # type: ignore
        return body


class SyncServiceMethodGenerator(DefaultServiceMethodGenerator):
    _method_generators: typing.Dict[
        typing.Tuple[bool, bool], typing.Type[BaseServiceMethodGenerator]
    ] = {
        (False, False): ServiceMethodUnaryUnaryFunctionGenerator,
        (True, False): ServiceMethodStreamUnaryFunctionGenerator,
        (False, True): ServiceMethodUnaryStreamFunctionGenerator,
        (True, True): ServiceMethodStreamStreamFunctionGenerator,
    }

    def process_service_method(self, method: Method) -> FunctionDef:
        func_def = super().process_service_method(method)
        func_def.name = (
            re.sub(r"(?<!^)(?=[A-Z])", "_", method.name).replace("-", "_").lower()
        )  # to snake_case
        return func_def
