import os
from pathlib import Path
from PySide6.QtWidgets import QPushButton
import pytest
from voice_annotation_tool.opened_project_frame import AnnotationListModel, OpenedProjectFrame
from voice_annotation_tool.project import Project, Annotation

annotation_data = {
    "client_id": "id",
    "path": "",
    "text": "",
    "up_votes": 0,
    "down_votes": 0,
    "age": "twenties",
    "gender": "male",
    "accent": "accent",
    "modified": False,
}

@pytest.fixture
def project_frame():
    frame = OpenedProjectFrame()
    project = Project("")
    for annotation_num in range(3):
        path = Path("/tmp/path_" + str(annotation_num))
        path.touch()
        annotation_data["path"] = str(path)
        project.add_annotation(Annotation(annotation_data))
    frame.load_project(project)
    return frame

def test_annotation_list(project_frame):
    model : AnnotationListModel = project_frame.annotationList.model()
    assert model.rowCount() == 3

def test_metadata_header_filled_on_open(project_frame):
    assert project_frame.accentEdit.text() == "accent"
    assert project_frame.clientIdEdit.text() == "id"
    assert project_frame.genderInput.currentText() == "Male"
    assert project_frame.ageInput.currentText() == "19 - 29"

def test_tooltips_have_shortcuts(project_frame):
    play_button : QPushButton = project_frame.playPauseButton
    assert play_button.shortcut().toString() in play_button.toolTip()

def test_delete_removes_rows(project_frame: OpenedProjectFrame):
    model: AnnotationListModel = project_frame.annotationList.model()
    start = model.rowCount()
    selected = len(project_frame.get_selected_annotations())
    project_frame.delete_selected()
    assert model.rowCount() == start - selected

def test_delete_removes_files(project_frame: OpenedProjectFrame):
    selected: Annotation = project_frame.get_selected_annotations()[0]
    project_frame.delete_selected()
    assert not os.path.isfile(selected.path)