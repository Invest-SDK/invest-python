import logging
from ast import Module
from pathlib import Path
from typing import Dict

import astor
from iprotopy import PackageGenerator as DefaultPackageGenerator
from iprotopy.domestic_importer import DomesticImporter
from iprotopy.protos_generator import ProtosGenerator

from scripts.generate_models.code_generators.constants import PROTO_SUFFIX
from scripts.generate_models.code_generators.file_generator import SourceGenerator
from scripts.generate_models.code_generators.imports_resolver import (
    Importer,
    ProtobufImporter,
)

from .base_service_source_generator import BaseServiceSourceGenerator

logger = logging.getLogger(__name__)


class PackageGenerator(DefaultPackageGenerator):
    def __init__(self):
        super().__init__()
        self._extende_types()

    def _extende_types(self):
        self._type_mapper._standard_types_mapping.update(
            {
                "string": "str",
                "bytes": "bytes",
                "bool": "bool",
                "double": "float",
                "float": "float",
                "int32": "int",
                "sint32": "int",
                "sfixed32": "int",
                "uint32": "int",
                "fixed32": "int",
                "int64": "int",
                "sint64": "int",
                "sfixed64": "int",
                "uint64": "int",
                "fixed64": "int",
            }
        )

    # noinspection PyMethodOverriding
    def generate_sources(self, proto_dir: Path, out_dir: Path, base_lib_dir: Path):
        importer = Importer()
        protos_generator = ProtosGenerator(importer)
        protos_generator.generate_protos(proto_dir, out_dir)

        out_dir.mkdir(parents=True, exist_ok=True)
        proto_files = list(proto_dir.rglob("*.proto"))
        modules: Dict[Path, Module] = {}

        self._create_lib_dependencies(base_lib_dir, importer)

        protobuf_importer = ProtobufImporter(self._parser, PROTO_SUFFIX, proto_files)

        for proto_file in proto_files:
            pyfile = proto_file.relative_to(proto_dir).with_suffix(".py")
            logger.debug(pyfile)
            source_generator = SourceGenerator(
                proto_file,
                out_dir,
                pyfile,
                self._parser,
                self._type_mapper,
                importer,
                protobuf_importer,
            )
            module = source_generator.generate_source()
            modules[proto_file] = module

        importer.remove_circular_dependencies()

        for proto_file in proto_files:
            pyfile = proto_file.relative_to(proto_dir).with_suffix(".py")
            imports = importer.get_imports(pyfile)
            module = modules[proto_file]
            self._insert_imports(module, imports)
            result_src = astor.to_source(module)
            filepath = out_dir / pyfile
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                f.write(result_src)

    def _create_base_service(self, importer, out_dir):
        pyfile = (
            Path(out_dir / "base_service")
            .relative_to(Path().absolute())
            .with_suffix(".py")
        )
        base_service_source_generator = BaseServiceSourceGenerator(
            DomesticImporter(importer, pyfile)
        )
        module = base_service_source_generator.create_source()
        filepath = pyfile
        imports = importer.get_imports(filepath)
        self._insert_imports(module, imports)
        result_src = astor.to_source(module)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(result_src)
