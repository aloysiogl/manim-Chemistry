from manim import Scene, Text, Create
from manim_chemistry.periodic_table import PositionFinder, PeriodicTable, PositionTransformer, ReplicatedElement

from pathlib import Path

script_path = Path(__file__).absolute().parent
files_path = script_path / "element_files"


class Main(Scene):
    def construct(self):
        finder = PositionFinder(files_path)
        element_assignment, letter_assigment = finder.get_assigments(
            ["alunos de", "", "quimica"])
        periodic_table = PeriodicTable(files_path / "Elementos.csv")
        table, elements = periodic_table.get_elements()

        # add table elemets to scene
        replicated_elements = []
        for atomic_number, element in elements.items():
            self.add(element)
            replicated_elements.append(ReplicatedElement(element))
        animations = []
        position_transformer = PositionTransformer(["dia", "do", "quimico"])
        for element in replicated_elements:
            animations.append(element.move_to_assignments_animation(
                element_assignment, position_transformer))

        self.play(*animations, run_time=5)
        animations = []
        for letter, positions in letter_assigment.items():
            for position in positions:
                position = position_transformer.get_transformed_position(
                    position)
                text = Text(letter.upper()).scale(1).move_to(position)
                animations.append(Create(text))
        self.play(*animations, run_time=1)
        animations = []
        for element in replicated_elements:
            animations.append(
                element.transform_to_letter_animation(element_assignment))
        self.wait()
