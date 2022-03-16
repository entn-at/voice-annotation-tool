from io import StringIO
import os, csv
from pathlib import Path
import json
from typing import Iterable, List, TextIO

from .annotation import Annotation


class Project:
    """Representation of a project file

    Handles loading and saving projects as well as loading the
    samples from the audio folder.
    Provides methods for importing and exporting json, text and csv
    files.
    """

    def __init__(self):
        self.tsv_file: Path | None = None
        self.audio_folder: Path | None = None
        self.annotations_by_path: dict[str, Annotation] = {}
        self.annotations: List[Annotation] = []
        self.modified_annotations: List[str] = []

    def load_json(self, file: TextIO, location: Path = Path()) -> bool:
        """Loads a project from a json file.

        Paths to the audio folder and to the tsv file are loaded relative
        to the given location. This does not load the tsv file or the audio
        folder.
        """
        data = json.load(file)
        if not all(
            ["modified_annotations" in data, "audio_folder" in data, "tsv_file" in data]
        ):
            return False
        self.modified_annotations = data["modified_annotations"]
        self.audio_folder = location.joinpath(data.get("audio_folder"))
        self.tsv_file = location.joinpath(data.get("tsv_file"))
        return True

    def load_audio_files(self, folder: Path):
        """
        Loads the samples from the audio folder of this project into files.
        """
        self.audio_folder = folder
        if not self.audio_folder.is_dir():
            return
        for audio_file in os.listdir(self.audio_folder):
            path = Path(audio_file)
            if path.suffix in [".mp3", ".ogg", ".mp4", ".webm", ".avi", ".mkv", ".wav"]:
                if not audio_file in self.annotations_by_path:
                    annotation = Annotation()
                    annotation.path = self.audio_folder.joinpath(path)
                    self.add_annotation(annotation)

    def annotate(self, annotation: Annotation, text: str) -> None:
        """Changes the text of the given annotation."""
        if not annotation.modified:
            self.modified_annotations.append(annotation.path.name)
        annotation.modified = True
        annotation.sentence = text

    def mark_unchanged(self, annotation: Annotation) -> None:
        """Remove the modified mark of the given annotation."""
        annotation.modified = False
        if annotation.path in self.modified_annotations:
            self.modified_annotations.remove(annotation.path)

    def save(self, file: TextIO, location: Path = Path()):
        """Saves this project to the given buffer. Paths to the audio
        folder and to the tsv file are saved relative to the project file.
        """
        data = {
            "tsv_file": "",
            "audio_folder": "",
            "modified_annotations": self.modified_annotations,
        }
        if self.tsv_file:
            data["tsv_file"] = str(os.path.relpath(self.tsv_file, location))
        if self.audio_folder:
            data["audio_folder"] = str(os.path.relpath(self.audio_folder, location))
        json.dump(data, file)

    def save_annotations(self, file: TextIO):
        """
        Exports the project's annotations to a tab separated value (tsv) file.
        """
        writer = csv.DictWriter(file, Annotation.TSV_HEADER_MEMBERS, delimiter="\t")
        writer.writeheader()
        for annotation in self.annotations:
            writer.writerow(annotation.to_dict())

    def load_tsv_file(self, file: Iterable[str]):
        """
        Loads the annotations from the `tsv_file` into the annotations array.
        """
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            annotation = Annotation(row)
            if annotation.path.name in self.modified_annotations:
                annotation.modified = True
            self.add_annotation(annotation)
        print("loaded csv")

    def delete_tsv(self):
        """Delete the TSV file."""
        if self.tsv_file and self.tsv_file.is_file():
            self.tsv_file.unlink()

    def delete_annotation(self, annotation: Annotation):
        """Delete a stored annotation and the audio file on disk."""
        annotation.path.unlink(missing_ok=True)
        self.annotations_by_path.pop(annotation.path.name)
        self.annotations.remove(annotation)

    def add_annotation(self, annotation: Annotation):
        if self.audio_folder:
            annotation.path = self.audio_folder.joinpath(annotation.path)
        self.annotations_by_path[annotation.path.name] = annotation
        self.annotations.append(annotation)

    def importCSV(self, infile: StringIO):
        reader = csv.reader(infile, delimiter=";")
        for row in reader:
            path = row[0]
            if not path in self.annotations_by_path:
                return
            self.annotate(self.annotations_by_path[path], row[1])

    def exportCSV(self, outfile: StringIO):
        writer = csv.writer(outfile, delimiter=";")
        for annotation in self.annotations:
            writer.writerow([annotation.path.name, annotation.sentence])

    def importJson(self, infile: StringIO):
        data = json.load(infile)
        for row in data:
            for filename in row:
                if not filename in self.annotations_by_path:
                    continue
                self.annotate(self.annotations_by_path[filename], row[filename])

    def exportJson(self, outfile: StringIO):
        data = []
        for annotation in self.annotations:
            data.append({annotation.path.name: annotation.sentence})
        json.dump(data, outfile)

    def __hash__(self):
        return hash(frozenset(map(hash, self.annotations)))
