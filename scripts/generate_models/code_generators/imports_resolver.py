import logging
from ast import Attribute, Load, Name, expr
from pathlib import Path
from typing import Dict, Set

from iprotopy.domestic_importer import DomesticImporter
from iprotopy.importer import Importer as BaseImporter
from proto_schema_parser import Parser
from proto_schema_parser.ast import File, Message

logger = logging.getLogger(__name__)


class Importer(BaseImporter):
    def __init__(self):
        super().__init__()
        self._defined_in_package: Dict[Path, Set[str]] = {}

    def define_dependency(self, name: str, package: Path):
        if name in self._definitions:
            logger.warning("Class %s already registered", name)
        self._definitions[name] = package
        defined = self._defined_in_package.get(package)
        if defined is None:
            defined = set()
            self._defined_in_package[package] = defined
        defined.add(name)

    def import_dependency(self, name: str, package: Path):
        if name in self._default_dependencies or name in self._defined_in_package.get(
            package, set()
        ):
            return

        dependencies = self._dependencies.get(package, set())
        dependencies.add(name)
        self._dependencies[package] = dependencies

    def remove_circular_dependencies(self):
        for package, deps in self._dependencies.items():
            local = self._defined_in_package.get(package, set())
            deps.difference_update(local)


class ProtobufImporter:
    def __init__(self, parser: Parser, suffix: str, pyfiles: list[Path]):
        self._parser = parser
        self._pyfiles = pyfiles
        self._suffix = suffix
        self._imports: dict[str, str] = self._init_imports()

    def get_attribute(
        self, element_name: str, protobuf_package_name: str, importer: DomesticImporter
    ) -> expr:
        if (
            element_name in self._imports
            and self._imports[element_name] != protobuf_package_name
        ):
            importer.import_dependency(self._imports[element_name])
            return Name(id=self._imports[element_name], ctx=Load())
        return Attribute(
            value=Name(id="self", ctx=Load()),
            attr="_protobuf",
            ctx=Load(),
        )

    def _read_proto(self, proto_file: Path) -> File:
        with open(proto_file) as f:
            text = f.read()
        file: File = self._parser.parse(text)
        return file

    def _init_imports(self) -> dict[str, str]:
        imports: dict[str, str] = {}
        for pyfile in self._pyfiles:
            file: File = self._read_proto(pyfile)
            for element in file.file_elements:
                if isinstance(element, Message):
                    imports[element.name] = f"{pyfile.stem}{self._suffix}"
        return imports
