from io import StringIO
from pathlib import Path

import pytest
from voice_annotation_tool.annotation import Annotation
from voice_annotation_tool.project import Project


@pytest.fixture
def project():
    project = Project()
    project.audio_folder = Path("/tmp/audio")
    project.tsv_file = Path("/tmp/project.tsv")
    project.add_annotation(Annotation({"path": "path", "sentence": "text"}))
    return project


def test_creation(project):
    assert project


def test_export_csv(project):
    output = StringIO()
    project.exportCSV(output)
    output.seek(0)
    assert output.read() == "/tmp/audio/path;text\r\n"


def test_export_json(project):
    output = StringIO()
    project.exportJson(output)
    output.seek(0)
    assert output.read() == '[{"path": "text"}]'


def test_import_csv(project):
    project.importCSV(StringIO("path;new"))
    assert project.annotations[0].sentence == "new"


def test_import_json(project):
    project.importJson(StringIO('[{"path": "new"}]'))
    assert project.annotations[0].sentence == "new"


def test_save(project: Project):
    buffer = StringIO()
    project.save(buffer)
    buffer.seek(0)
    assert (
        buffer.read()
        == '{"tsv_file": "project.tsv", "audio_folder": "audio", "modified_annotations": []}'
    )


def test_save_annotations(project: Project):
    buffer = StringIO()
    project.save_annotations(buffer)
    buffer.seek(0)
    assert (
        buffer.read()
        == "client_id\tpath\tsentence\tup_votes\tdown_votes\tage\tgender\taccent\r\n\tpath\ttext\t0\t0\t\t\t\r\n"
    )


def test_load(project: Project):
    pass
