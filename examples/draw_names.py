from manim import Scene, Text, FadeOut, Transform, Create, ORIGIN, RIGHT, UP, DOWN, LEFT
from manim_chemistry.periodic_table import PositionFinder, PeriodicTable, PositionTransformer, ReplicatedElement, MElementWithPositions, MElementObject, MElementGroup
from  manim_chemistry.chemical_text import MChemicalText

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
        text = MChemicalText(
            ["o", "iii", "ii"], element_file_path)
        text2 = MChemicalText(
            ["a", "i", "i"], element_file_path)
        text = MChemicalText(
            ["agradeciment especial", "do", "quimico"], element_file_path)
        text2 = MChemicalText(
            ["made by aloysio", "do", "quimico"], element_file_path)
        text.move_to(ORIGIN).scale(0.2)
        text2.move_to(ORIGIN).scale(0.3)
        self.add(text)
        elements_transform = text.get_element_group().transform_into_group(text2.get_element_group())
        text_transform = Transform(text.get_letter_group(), text2.get_letter_group())
        self.play(elements_transform, text_transform)
        table = PeriodicTable(element_file_path)
        table.scale(0.25)
        table.move_to(ORIGIN)
        self.play(FadeOut(text.get_letter_group()))
        self.play(text.get_element_group().transform_into_group(table))


class Main1(Scene):
    def construct(self):
        element_file_path = files_path / "Elementos.csv"
        pos1 = [ORIGIN]
        pos2 = [2*UP*MElementObject().get_height(), 2*DOWN *
                MElementObject().get_height()]
        pos3 = [2*LEFT*MElementObject().get_height()]
        pos4 = [2*RIGHT*MElementObject().get_height()]
        el1 = MElementWithPositions(
            atomic_number=1, positions=pos1, data_file_path=element_file_path)
        el2 = MElementWithPositions(
            atomic_number=2, positions=pos2, data_file_path=element_file_path)
        el3 = MElementWithPositions(
            atomic_number=1, positions=pos3, data_file_path=element_file_path)
        el4 = MElementWithPositions(
            atomic_number=3, positions=pos4, data_file_path=element_file_path)
        gr1 = MElementGroup([el1, el2])
        gr1.move_to(ORIGIN).scale(0.5)
        gr2 = MElementGroup([el3, el4])
        gr2.move_to(ORIGIN).scale(0.5)
        self.add(gr1)
        self.play(gr1.transform_into_group(gr2))
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
