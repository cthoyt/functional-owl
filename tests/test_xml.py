import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

import curies
import robot_obo_tool
import rdflib
from functional_owl import dsl, write_ontology

converter = curies.Converter.from_prefix_map(
    {
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "a": "https://example.org/a:",
        "b": "https://example.org/b:",
    }
)


class TestXML(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.xml_path = self.directory.joinpath("output.owl")
        self.ofn_path = self.directory.joinpath("output.ofn")
        self.xml_oracle_path = self.directory.joinpath("output-oracle.owl")
        self.ttl_path = self.directory.joinpath("output.ttl")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_declaration_class(self) -> None:
        axioms = [
            dsl.Declaration("a:1", "Class"),
        ]
        self.assert_it("", axioms)

    def test_subclass_of(self) -> None:
        axioms = [
            dsl.Declaration("a:1", "Class"),
            dsl.Declaration("b:1", "Class"),
            dsl.SubClassOf("a:1", "b:1"),
        ]
        self.assert_it("", axioms)

    def assert_it(self, expected: str, axioms: list[dsl.Box]) -> None:
        iri = "https://example.org/test.owl"
        write_ontology(prefixes=converter, axioms=axioms, file=self.xml_path, format="xml", iri=iri)
        expected = dedent(expected)
        actual = self.xml_path.read_text()
        if expected == actual:
            return
        write_ontology(prefixes=converter, axioms=axioms, file=self.ofn_path, format="ofn", iri=iri)
        try:
            robot_obo_tool.convert(self.ofn_path, self.xml_oracle_path)
        except Exception:
            self.fail(f"failed to convert OFN:\n\n{self.ofn_path.read_text()}")

        g = rdflib.Graph()
        g.parse(self.xml_oracle_path, format="xml")
        g.serialize(self.ttl_path, format="ttl")
        self.assertEqual(
            expected,
            actual,
            msg=f"Should have been something like {self.xml_oracle_path.read_text()}\n\n{self.ttl_path.read_text()}",
        )
