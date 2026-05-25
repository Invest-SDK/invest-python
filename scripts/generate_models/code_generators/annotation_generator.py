from iprotopy.annotation_generator import AnnotationGenerator as BaseAnnotationGenerator


class AnnotationGenerator(BaseAnnotationGenerator):
    def process_annotation(self, annotation_type: str, **kwargs) -> str:
        try:
            annotation_type, field_import = self._type_mapper.map(annotation_type)
            if field_import is not None:
                self._importer.add_import(field_import)
        except ValueError:
            if "." in annotation_type:
                class_name = annotation_type.split(".")[0]
                self._importer.import_dependency(class_name)
            else:
                self._importer.import_dependency(annotation_type)
            annotation_type = (
                f"'{annotation_type}'"
                if not kwargs.get("outer_class_name")
                else f"'{kwargs.get('outer_class_name')}.{annotation_type}'"
            )

        return annotation_type
