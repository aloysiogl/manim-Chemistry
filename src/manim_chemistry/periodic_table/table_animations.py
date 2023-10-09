from manim import *
from ..element import Element
from .table_objects import MElementObject

from pathlib import Path

script_path = Path(__file__).absolute().parent
files_path = script_path / "manim-Chemistry/examples/element_files"


class PositionTransformer:
    def __init__(self, phrases, csv_path):
        assignment_finder = AssignmentFinder(csv_path)
        self.offset_rows = (len(phrases)-1)/2
        max_phrase_length = max(
            [len(assignment_finder.best_assignment_for_phrase(phrase)) for phrase in phrases])
        self.offset_cols = (max_phrase_length-1)/2

        base_element = MElementObject()
        self.mult_array = np.array(
            [base_element.get_width(), -base_element.get_height(), 0])*1.4*0.25

    def get_transformed_position(self, position):
        base_position = np.array(
            [position[1]-self.offset_cols, position[0]-self.offset_rows, 0])
        return np.multiply(self.mult_array, base_position)


class PositionFinder:
    def __init__(self, csv_path):
        self.assingment_finder = AssignmentFinder(csv_path)

    def get_assigments(self, phrases):
        element_positions = {}
        letter_positions = {}
        for i in range(len(phrases)):
            phrase = phrases[i]
            assignment = self.assingment_finder. \
                best_assignment_for_phrase(phrase)
            for j in range(len(assignment)):
                if isinstance(assignment[j], Element):
                    atomic_number = assignment[j].atomic_number
                    if atomic_number not in element_positions:
                        element_positions[atomic_number] = []
                    element_positions[atomic_number].append((i, j))
                else:
                    if assignment[j] not in letter_positions:
                        letter_positions[assignment[j]] = []
                    letter_positions[assignment[j]].append((i, j))
        return element_positions, letter_positions


class AssignmentFinder:
    def __init__(self, csv_path):
        available_atomic_numbers = list(range(1, 119))
        available_elements = [Element.from_csv_file(csv_path / "Elementos.csv", i)
                              for i in available_atomic_numbers]
        self.symbol_to_element = {element.symbol.lower(
        ): element for element in available_elements}
        self.memoised_assignments = {}

    def best_assignment_for_phrase(self, phrase):
        if phrase in self.memoised_assignments:
            return self.memoised_assignments[phrase]
        if len(phrase) == 0:
            return []
        phrase_without_first_letter = phrase[1:]
        first_letter = phrase[0].lower()
        if len(phrase) == 1:
            if first_letter in self.symbol_to_element:
                return [self.symbol_to_element[first_letter]]
            return [first_letter]
        phrase_without_two_first_letters = phrase[2:]
        two_first_letters = phrase[:2].lower()

        first_assingment = self.best_assignment_for_phrase(
            phrase_without_first_letter)
        two_first_assingment = self.best_assignment_for_phrase(
            phrase_without_two_first_letters)
        tot_first = self.count_non_element(first_assingment)
        tot_two_first = self.count_non_element(two_first_assingment)

        if first_letter not in self.symbol_to_element:
            tot_first += 1
            first_assingment = [first_letter] + first_assingment
        else:
            first_assingment = [
                self.symbol_to_element[first_letter]] + first_assingment

        if two_first_letters not in self.symbol_to_element:
            tot_two_first += 2
            two_first_assingment = [two_first_letters] + two_first_assingment
        else:
            two_first_assingment = [
                self.symbol_to_element[two_first_letters]] + two_first_assingment

        final_assingment = two_first_assingment
        if tot_first <= tot_two_first:
            final_assingment = first_assingment
        self.memoised_assignments[phrase] = final_assingment
        return final_assingment

    def count_non_element(self, assingment):
        tot_letters = 0
        for element in assingment:
            if isinstance(element, Element):
                continue
            tot_letters += 1
        return tot_letters


class ReplicatedElement:
    def __init__(self, element):
        self.element = element
        self.y_offset = 0
        self.x_offset = 0
        self.x_scale = 1
        self.y_scale = 1
        self.elements = [self.element]

    def move_to_assignments_animation(self, assignment, position_transformer):
        atomic_number = self.element.atomic_number
        if atomic_number not in assignment:
            return FadeOut(self.element)
        total_positions = len(assignment[atomic_number])
        for i in range(1, total_positions):
            new_element = self.element.copy()
            self.elements.append(new_element)
        animations = []
        for i in range(len(assignment[atomic_number])):
            position = assignment[atomic_number][i]
            animations.append(self.elements[i].animate.move_to(
                position_transformer.get_transformed_position(position)))
        return AnimationGroup(*animations)

    def transform_to_letter_animation(self, assignment):
        animations = []
        atomic_number = self.element.atomic_number
        if atomic_number not in assignment:
            return Wait()
        for element in self.elements:
            letter = Text(element.element_symbol).scale(
                1).move_to(element.get_center())
            animations.append(Transform(element, letter))
        return AnimationGroup(*animations)


class PeriodicTable(VGroup):
    # TODO Change to english database
    def __init__(self, data_file, *vmobjects, **kwargs):
        VGroup.__init__(self, *vmobjects, **kwargs)
        self.data_file = data_file

    def get_elements(self):
        positions = self.elements_position_dict()
        base_element = MElementObject()
        mult_array = np.array(
            [base_element.get_width(), -base_element.get_height(), 0])

        table = VGroup()
        elements = {}
        for element, position in positions.items():
            new_position = np.multiply(mult_array, np.array(position))
            new_element = MElementObject.from_csv_file_data(
                self.data_file, element
            ).move_to(new_position)
            elements[element] = new_element

            table.add(new_element)

        table.move_to(ORIGIN).scale(0.25)
        self.add(table)
        return table, elements

    def elements_position_dict(self):
        # TODO: Think of a better way of doing this. However, it works and looks good
        positions = {
            3: [0, 1, 0],
            4: [1, 1, 0],
            5: [12, 1, 0],
            6: [13, 1, 0],
            7: [14, 1, 0],
            8: [15, 1, 0],
            9: [16, 1, 0],
            10: [17, 1, 0],
            11: [0, 2, 0],
            12: [1, 2, 0],
            13: [12, 2, 0],
            14: [13, 2, 0],
            15: [14, 2, 0],
            16: [15, 2, 0],
            17: [16, 2, 0],
            18: [17, 2, 0],
            19: [0, 3, 0],
            20: [1, 3, 0],
            21: [2, 3, 0],
            22: [3, 3, 0],
            23: [4, 3, 0],
            24: [5, 3, 0],
            25: [6, 3, 0],
            26: [7, 3, 0],
            27: [8, 3, 0],
            28: [9, 3, 0],
            29: [10, 3, 0],
            30: [11, 3, 0],
            31: [12, 3, 0],
            32: [13, 3, 0],
            33: [14, 3, 0],
            34: [15, 3, 0],
            35: [16, 3, 0],
            36: [17, 3, 0],
            37: [0, 4, 0],
            38: [1, 4, 0],
            39: [2, 4, 0],
            40: [3, 4, 0],
            41: [4, 4, 0],
            42: [5, 4, 0],
            43: [6, 4, 0],
            44: [7, 4, 0],
            45: [8, 4, 0],
            46: [9, 4, 0],
            47: [10, 4, 0],
            48: [11, 4, 0],
            49: [12, 4, 0],
            50: [13, 4, 0],
            51: [14, 4, 0],
            52: [15, 4, 0],
            53: [16, 4, 0],
            54: [17, 4, 0],
            55: [0, 5, 0],
            56: [1, 5, 0],
            57: [2, 7.5, 0],
            58: [3, 7.5, 0],
            59: [4, 7.5, 0],
            60: [5, 7.5, 0],
            61: [6, 7.5, 0],
            62: [7, 7.5, 0],
            63: [8, 7.5, 0],
            64: [9, 7.5, 0],
            65: [10, 7.5, 0],
            66: [11, 7.5, 0],
            67: [12, 7.5, 0],
            68: [13, 7.5, 0],
            69: [14, 7.5, 0],
            70: [15, 7.5, 0],
            71: [2, 5, 0],
            72: [3, 5, 0],
            73: [4, 5, 0],
            74: [5, 5, 0],
            75: [6, 5, 0],
            76: [7, 5, 0],
            77: [8, 5, 0],
            78: [9, 5, 0],
            79: [10, 5, 0],
            80: [11, 5, 0],
            81: [12, 5, 0],
            82: [13, 5, 0],
            83: [14, 5, 0],
            84: [15, 5, 0],
            85: [16, 5, 0],
            86: [17, 5, 0],
            87: [0, 6, 0],
            88: [1, 6, 0],
            89: [2, 8.5, 0],
            90: [3, 8.5, 0],
            91: [4, 8.5, 0],
            92: [5, 8.5, 0],
            93: [6, 8.5, 0],
            94: [7, 8.5, 0],
            95: [8, 8.5, 0],
            96: [9, 8.5, 0],
            97: [10, 8.5, 0],
            98: [11, 8.5, 0],
            99: [12, 8.5, 0],
            100: [13, 8.5, 0],
            101: [14, 8.5, 0],
            102: [15, 8.5, 0],
            103: [2, 6, 0],
            104: [3, 6, 0],
            105: [4, 6, 0],
            106: [5, 6, 0],
            107: [6, 6, 0],
            108: [7, 6, 0],
            109: [8, 6, 0],
            110: [9, 6, 0],
            111: [10, 6, 0],
            112: [11, 6, 0],
            113: [12, 6, 0],
            114: [13, 6, 0],
            115: [14, 6, 0],
            116: [15, 6, 0],
            117: [16, 6, 0],
            118: [17, 6, 0],
        }
        return positions
