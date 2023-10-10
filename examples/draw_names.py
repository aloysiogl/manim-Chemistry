from manim import Scene, Text, Create, ORIGIN, RIGHT, UP, DOWN
from manim_chemistry.periodic_table import PositionFinder, PeriodicTable, PositionTransformer, ReplicatedElement, MElementWithPositions, MElementObject

from pathlib import Path

script_path = Path(__file__).absolute().parent
files_path = script_path / "element_files"


"""
Comandos para compilar a animacao, utilize a opção -pqh para alta qualidade:
manim -pql draw_names.py Main
manim -pqh draw_names.py Main
"""


class Main(Scene):
    def construct(self):
        element_file_path = files_path / "Elementos.csv"
        positions = [ORIGIN]
        positions2 = [2*UP*MElementObject().get_height(), 2*DOWN *
                      MElementObject().get_height()]
        element_with_positions = MElementWithPositions(
            atomic_number=1, positions=positions, data_file_path=element_file_path)
        element_with_positions.scale(0.5).move_to(ORIGIN)

        element_with_positions2 = MElementWithPositions(
            atomic_number=1, positions=positions2, data_file_path=element_file_path)
        self.add(element_with_positions)
        element_with_positions2.scale(1).move_to(ORIGIN)
        anim = element_with_positions.move_to_element_with_positions(
            element_with_positions2)
        self.play(anim, run_time=1)
        self.wait()


class Main2(Scene):
    def construct(self):
        phrases = ["agradeciment especial", "do", "quimico"]
        horizontal_scale = 1
        vertical_scale = 1
        finder = PositionFinder(files_path)
        element_assignment, letter_assigment = finder.get_assigments(
            phrases)
        periodic_table = PeriodicTable(files_path / "Elementos.csv")
        table, elements = periodic_table.get_elements()

        # add table elemets to scene
        replicated_elements = []
        for atomic_number, element in elements.items():
            self.add(element)
            replicated_elements.append(ReplicatedElement(element))
        animations = []
        position_transformer = PositionTransformer(
            phrases, files_path, horizontal_scale, vertical_scale)
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
