import numpy as np
from typing import List
from manim import VGroup, Text
from ..element import Element
from ..periodic_table import MElementWithPositions, MElementGroup, MElementObject


class MChemicalText(VGroup):
    def __init__(self, phrases: List[str], elements_path, letter_scale=1.2, *vmobjects, **kwargs):
        VGroup.__init__(self, *vmobjects, **kwargs)
        position_finder = PositionFinder(elements_path)
        self.elements_path = elements_path
        self.element_assignments, self.letter_assignments = position_finder.get_assigments(
            phrases)
        self.element_group = None
        self.letter_group = None
        self.letter_scale = letter_scale
        self.add_letter_and_element_groups()

    def add_letter_and_element_groups(self):
        els = []
        for atomic_number, positions in self.element_assignments.items():
            els.append(MElementWithPositions(
                atomic_number, positions, self.elements_path))
        self.element_group = MElementGroup(els)
        self.letter_group = VGroup()
        for letter, positions in self.letter_assignments.items():
            for position in positions:
                text = Text(letter.upper()).scale(1).move_to(position)
                text.scale(MElementObject().width * self.letter_scale)
                self.letter_group.add(text)
        self.add(self.element_group)
        self.add(self.letter_group)

    def get_element_group(self):
        return self.element_group

    def get_letter_group(self):
        return self.letter_group


class PositionFinder:
    def __init__(self, elements_path, horizontal_scale=1, vertical_scale=1):
        self.assingment_finder = AssignmentFinder(elements_path)
        el_obj = MElementObject()
        self.scale_factor = np.array(
            [1*el_obj.get_width()*horizontal_scale, -1*el_obj.get_height()*vertical_scale, 1])

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
                    element_positions[atomic_number].append(
                        np.array([j, i, 0]*self.scale_factor))
                else:
                    if assignment[j] not in letter_positions:
                        letter_positions[assignment[j]] = []
                    letter_positions[assignment[j]].append(
                        np.array([j, i, 0]*self.scale_factor))
        return element_positions, letter_positions


class AssignmentFinder:
    def __init__(self, elements_path):
        available_atomic_numbers = list(range(1, 119))
        available_elements = [Element.from_csv_file(elements_path, i)
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
