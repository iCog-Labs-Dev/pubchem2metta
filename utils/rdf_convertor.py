import os
from biocypher._logger import logger
from rdflib import Graph
from pathlib import Path


class RDFConverter:
    def __init__(
        self, input_dir, input_format="ttl", output_format="xml", remove_old_files=False
    ):
        self.input_dir = input_dir
        self.input_format = input_format.lower()
        self.output_format = output_format.lower()
        self.remove_old_files = remove_old_files

    def convert_files(self):
        for _, _, files in os.walk(self.input_dir):
            for file_name in files:
                if file_name.endswith(f".{self.input_format}"):
                    ttl_path = os.path.join(self.input_dir, file_name)
                    xml_path = self.__get_output_path(ttl_path, self.output_format)

                    self.convert_file_and_delete(ttl_path, xml_path)

    def convert_file_and_delete(self, input_path, output_path):
        graph = Graph()
        graph.parse(input_path, format=self.input_format)
        graph.serialize(format=self.output_format, destination=output_path)

        if self.remove_old_files:
            os.remove(input_path)

        logger.info(f"Conversion complete: {input_path} -> {output_path}")

    def __get_output_path(self, input_path, new_extension):
        input_path = Path(input_path)
        return str(input_path.with_suffix(f".{new_extension}"))
