import typing
from ast import FunctionDef

from iprotopy.domestic_importer import DomesticImporter
from iprotopy.service_method_generator import (
    ServiceMethodGenerator as DefaultServiceMethodGenerator,
)
from proto_schema_parser.ast import Method

from scripts.generate_models.code_generators.base_generators import (
    BaseServiceMethodGenerator,
)
from scripts.generate_models.code_generators.imports_resolver import ProtobufImporter


class ServiceMethodGenerator(DefaultServiceMethodGenerator):
    _method_generators: typing.Dict[
        typing.Tuple[bool, bool], typing.Type[BaseServiceMethodGenerator]
    ] = {}

    def __init__(
        self,
        importer: DomesticImporter,
        protobuf_importer: ProtobufImporter,
        pyfile: str,
    ):
        super().__init__(importer)
        self._pyfile = pyfile
        self._protobuf_importer = protobuf_importer

    def process_service_method(self, method: Method) -> FunctionDef:
        is_input_stream = method.input_type.stream
        is_output_stream = method.output_type.stream

        method_generator = self._method_generators[(is_input_stream, is_output_stream)](
            self._importer, self._protobuf_importer, self._pyfile
        )

        return method_generator.create(method)
