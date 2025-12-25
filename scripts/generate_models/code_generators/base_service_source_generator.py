from ast import (
    AnnAssign,
    Assign,
    Attribute,
    Call,
    ClassDef,
    Constant,
    FunctionDef,
    ImportFrom,
    Load,
    Module,
    Name,
    Store,
    arg,
    arguments,
    stmt,
)

from iprotopy.domestic_importer import DomesticImporter


class BaseServiceSourceGenerator:
    def __init__(self, importer: DomesticImporter):
        self._importer = importer

    def create_source(self) -> Module:
        self._importer.add_import(
            ImportFrom(
                module="typing",
                names=[Name(id="Any", ctx=Load())],  # type: ignore[list-item]
                level=0,
            )
        )
        class_name = "BaseService"
        body: list[stmt] = [
            ClassDef(
                name=class_name,
                bases=[],
                keywords=[],
                body=[
                    AnnAssign(
                        target=Name(id="_protobuf_stub", ctx=Store()),
                        annotation=Name(id="Any", ctx=Load()),
                        value=Constant(value=None),
                        simple=1,
                    ),
                    FunctionDef(
                        name="__init__",
                        args=arguments(
                            posonlyargs=[],
                            args=[
                                arg(arg="self"),
                                arg(arg="channel"),
                                arg(arg="metadata"),
                            ],
                            kwonlyargs=[],
                            kw_defaults=[],
                            defaults=[],
                        ),
                        body=[
                            Assign(
                                targets=[
                                    Attribute(
                                        value=Name(id="self", ctx=Load()),
                                        attr="_stub",
                                        ctx=Store(),
                                    )
                                ],
                                value=Call(
                                    func=Attribute(
                                        value=Name(id="self", ctx=Load()),
                                        attr="_protobuf_stub",
                                        ctx=Load(),
                                    ),
                                    args=[Name(id="channel", ctx=Load())],
                                    keywords=[],
                                ),
                            ),
                            Assign(
                                targets=[
                                    Attribute(
                                        value=Name(id="self", ctx=Load()),
                                        attr="_metadata",
                                        ctx=Store(),
                                    )
                                ],
                                value=Name(id="metadata", ctx=Load()),
                            ),
                        ],
                        decorator_list=[],
                    ),
                ],
                decorator_list=[],
            )
        ]
        self._importer.define_dependency(class_name)
        return Module(body=body, type_ignores=[])
