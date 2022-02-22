from PySide6.QtWidgets import QDialogButtonBox, QPushButton
from PySide6.QtTest import QTest
from _pytest.fixtures import FixtureFunction
from voice_annotation_tool.create_project_dialog import CreateProjectDialog


def test_ok_disabled():
    dialog = CreateProjectDialog()
    ok_button: QPushButton = dialog.buttonBox.button(QDialogButtonBox.Ok)
    assert not ok_button.isEnabled()


def test_ok_enabled_after_fields_filled():
    dialog = CreateProjectDialog()
    dialog.audioPathEdit.insert("path")
    dialog.projectPathEdit.insert("path")
    dialog.tsvPathEdit.insert("path")
    ok_button: QPushButton = dialog.buttonBox.button(QDialogButtonBox.Ok)
    assert ok_button.isEnabled()


def test_create_project():
    dialog = CreateProjectDialog()
    dialog.audioPathEdit.insert("/tmp")
    dialog.projectPathEdit.insert("/tmp/path.json")
    dialog.tsvPathEdit.insert("/tmp/path.tsv")
    dialog.accept()
    assert True
