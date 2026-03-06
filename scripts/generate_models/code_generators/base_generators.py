from ast import (
    AsyncFunctionDef,
    Attribute,
    Call,
    Constant,
    FunctionDef,
    Load,
    Name,
    Subscript,
    alias,
    arg,
    arguments,
    expr,
)
from typing import Optional

from iprotopy.domestic_importer import DomesticImporter
from iprotopy.imports import ImportFrom
from iprotopy.service_method_generator import (
    BaseServiceMethodGenerator as DefaultBaseServiceMethodGenerator,
)
from proto_schema_parser.ast import Option

from scripts.generate_models.code_generators.imports_resolver import ProtobufImporter


# noinspection PyAbstractClass
class BaseServiceMethodGenerator(DefaultBaseServiceMethodGenerator):
    tracking_id_getter: str | None = None
    error_handler: Optional[str] = None
    error_hub_handler: Optional[str] = None
    is_async: bool = False

    def __init__(
        self,
        importer: DomesticImporter,
        protobuf_importer: ProtobufImporter,
        pyfile: str,
    ):
        super().__init__(importer)
        self._pyfile = pyfile
        self._protobuf_importer = protobuf_importer

    def _add_function_body_imports(self):
        self._importer.add_import(
            ImportFrom(
                module="t_tech.invest",
                names=[
                    alias(name="_grpc_helpers"),
                ],
                level=0,
            )
        )
        self._importer.add_import(
            ImportFrom(
                module="t_tech.invest._errors",
                names=[
                    alias(name=self.error_handler or ""),
                ],
                level=0,
            )
        )
        if self.error_hub_handler:
            self._importer.add_import(
                ImportFrom(
                    module="t_tech.invest._error_hub",
                    names=[
                        alias(name=self.error_hub_handler),
                    ],
                    level=0,
                )
            )
        if self.tracking_id_getter:
            self._importer.add_import(
                ImportFrom(
                    module="t_tech.invest.logging",
                    names=[
                        alias(name=self.tracking_id_getter),
                        alias(name="log_request"),
                    ],
                    level=0,
                )
            )

    def _get_annotation(self, class_type: str, is_stream: bool) -> expr:
        self._importer.import_dependency(class_type)
        if is_stream:
            if self.is_async:
                iterator_cls_name = "AsyncIterable"
            else:
                iterator_cls_name = "Iterable"
            self._importer.add_import(
                ImportFrom(
                    module="typing", names=[alias(name=iterator_cls_name)], level=0
                )
            )
            return Subscript(
                value=Name(id=iterator_cls_name, ctx=Load()),
                slice=Constant(value=class_type),
                ctx=Load(),
            )
        return Constant(value=class_type)

    def _get_args(self, input_class: str) -> arguments:
        input_annotation = self._get_annotation(input_class, self._is_input_stream)
        if not self._is_input_stream:
            default_request = Call(
                func=Name(id=input_class, ctx=Load()),
                args=[],
                keywords=[],
            )
        else:
            default_request = None
        return arguments(
            posonlyargs=[],
            args=[
                arg(arg="self"),
                arg(
                    arg=self._input_arg_name,
                    annotation=input_annotation,
                ),
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[default_request] if default_request else [],
        )

    def create(self, method):
        input_class = method.input_type.type
        output_class = method.output_type.type

        args = self._get_args(input_class)

        output_annotation = self._get_annotation(output_class, self._is_output_stream)
        body = self._get_function_body(method)
        self._add_function_body_imports()

        decorator_list: list[expr] = []

        if Option(name="deprecated", value=True) in method.elements:
            self._importer.add_import(
                ImportFrom(
                    module="deprecation", names=[alias(name="deprecated")], level=0
                )
            )
            decorator_list.append(
                Call(
                    func=Name(id="deprecated", ctx=Load()),
                    args=[],
                    keywords=[],
                )
            )

        if self.error_hub_handler:
            decorator_list.append(
                Call(
                    func=Name(id=self.error_hub_handler, ctx=Load()),
                    args=[],
                    keywords=[],
                )
            )

        decorator_list.append(
            Call(
                func=Name(id=str(self.error_handler), ctx=Load()),
                args=[Constant(value=method.name)],
                keywords=[],
            )
        )
        if self.is_async:
            return AsyncFunctionDef(
                name=method.name,
                args=args,
                body=body,
                decorator_list=decorator_list,
                returns=output_annotation,
            )
        return FunctionDef(
            name=method.name,
            args=args,
            body=body,
            decorator_list=decorator_list,
            returns=output_annotation,
        )

    def _get_dataclass_from_protobuf_call(self, request_class_name: str) -> Call:
        return Call(
            func=Name(id="_grpc_helpers.dataclass_to_protobuf", ctx=Load()),
            args=[
                Name(id="request", ctx=Load()),
                Call(
                    func=Attribute(
                        value=self._protobuf_importer.get_attribute(
                            request_class_name, self._pyfile, self._importer
                        ),
                        attr=request_class_name,
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            ],
            keywords=[],
        )


class BaseSyncServiceAnyUnaryFunctionGenerator(BaseServiceMethodGenerator):
    tracking_id_getter: str = "get_tracking_id_from_call"
    error_handler: str = "handle_request_error"


class BaseSyncServiceAnyStreamFunctionGenerator(BaseServiceMethodGenerator):
    error_handler: str = "handle_request_error_gen"
    error_hub_handler: str = "handle_error_hub_gen"


class BaseAIOServiceAnyUnaryFunctionGenerator(BaseServiceMethodGenerator):
    tracking_id_getter: str = "get_tracking_id_from_coro"
    error_handler: str = "handle_aio_request_error"
    is_async: bool = True


class BaseAIOServiceAnyStreamFunctionGenerator(BaseServiceMethodGenerator):
    error_handler: str = "handle_aio_request_error_gen"
    error_hub_handler: str = "handle_aio_error_hub_gen"
    is_async: bool = True
