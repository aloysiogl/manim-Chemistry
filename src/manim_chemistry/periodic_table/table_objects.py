from typing import List
from manim import (
    AnimationGroup,
    FadeIn,
    FadeOut,
    MoveToTarget,
    VGroup,
    WHITE,
    BLACK,
    BLUE,
    Rectangle,
    color_gradient,
    Text,
    Tex,
    RIGHT,
    ORIGIN,
    DOWN,
)
import pandas as pd
import numpy as np

from ..element import Element
from ..utils import AssignmentFinder


class MElementObject(VGroup):
    def __init__(
        self,
        atomic_number=1,
        atomic_mass=1,
        element_name="Hydrogen",
        element_symbol="H",
        coloring=BLACK,
        fill_colors=(WHITE, BLUE),
        gradient=10,
        opacity=0.8,
        text_color=WHITE,
        **kwargs,
    ):
        VGroup.__init__(self, **kwargs)
        self.atomic_number = atomic_number
        self.atomic_mass = atomic_mass
        self.element_name = element_name
        self.element_symbol = element_symbol
        self.coloring = coloring
        self.fill_colors = fill_colors
        self.gradient = 0
        self.opacity = 0.8
        self.text_color = text_color

        element_frame = self.create_frame_with_text()

        self.add(element_frame)

    def frame_name_width_ratio(self, frame, name_text):
        return frame.get_width() / (1.25 * name_text.get_width())

    def max_height_ratio(self, name_text):
        text_height = name_text.get_height()
        if text_height > 0.3:
            ratio = 0.3 / text_height
            name_text.scale(ratio)

        return name_text

    def create_frame_base(self):
        frame_rectangle = (
            Rectangle(
                height=2.8,
                width=2.8,
                color=self.coloring,
                stroke_width=0.2,
                fill_opacity=self.opacity,
            )
            .scale(0.8)
            .set_fill(color_gradient(self.fill_colors, self.gradient))
        )

        return frame_rectangle

    def create_frame_with_text(self):
        frame_rectangle = self.create_frame_base()
        symbol_text = (
            Text(self.element_symbol, color=self.text_color)
            .scale(2.4)
            .move_to(frame_rectangle.get_center())
        )
        name_text = (
            Text(self.element_name, color=self.text_color)
            .scale(0.2)
            .next_to(frame_rectangle, DOWN, buff=-0.4)
        )
        atomic_number_text = (
            Tex(str(self.atomic_number), color=self.text_color)
            .scale(0.65)
            .next_to(frame_rectangle, -DOWN, buff=-0.4)
        )
        atomic_mass_text = (
            Tex(str(self.atomic_mass), color=self.text_color)
            .scale(0.65)
            .next_to(frame_rectangle, DOWN, buff=-0.4)
        )

        ratio = self.frame_name_width_ratio(
            frame=frame_rectangle, name_text=name_text)
        name_text.scale(ratio)
        name_text = self.max_height_ratio(name_text)

        shifting_ammount = 0
        if 10 <= self.atomic_number:
            shifting_ammount += 0.15

        if self.atomic_number > 100:
            shifting_ammount += 0.15

        # atomic_number_text.shift(shifting_ammount * RIGHT)
        # atomic_mass_text.shift(-shifting_ammount * RIGHT)

        return VGroup(frame_rectangle, symbol_text, atomic_number_text, atomic_mass_text)

    def from_csv_file_data(filename, atomic_number, **kwargs):
        # TODO: Add option to set manually colors.
        # TODO: Create a table that adds this data in a prettier way.
        df = pd.read_csv(filename)
        element = df.loc[df["AtomicNumber"] ==
                         atomic_number].squeeze().to_dict()

        return MElementObject(
            atomic_number=atomic_number,
            atomic_mass=element.get("AtomicMass"),
            element_name=element.get("Name"),
            element_symbol=element.get("Symbol"),
            fill_colors=[element.get("Color"), WHITE],
        )


class MElementWithPositions(VGroup):
    def __init__(self, atomic_number, positions, data_file_path, *vmobjects, **kwargs):
        VGroup.__init__(self, *vmobjects, **kwargs)
        self.atomic_number = atomic_number
        self.positions = positions
        self.melements: MElementObject = {}
        self.data_file_path = data_file_path
        self.add_element_in_positions()

    def add_element_in_positions(self):
        for i in range(len(self.positions)):
            position = self.positions[i]
            melement = MElementObject.from_csv_file_data(
                self.data_file_path, self.atomic_number
            )
            melement.move_to(position)
            self.melements[i] = melement
            self.add(melement)

    def get_atomic_number(self):
        return self.atomic_number

    def get_nearest_element(self, excluding, melement: MElementObject) -> MElementObject:
        nearest_element = None
        nearest_distance = None
        index = None
        for ind, element in self.melements.items():
            if ind in excluding:
                continue
            distance = np.linalg.norm(
                element.get_center() - melement.get_center())
            nearest_element = element if nearest_element is None or distance < nearest_distance else nearest_element
            index = ind if index is None or distance < nearest_distance else index
            nearest_distance = distance if nearest_distance is None or distance < nearest_distance else nearest_distance

        return nearest_element, index

    def remove_element_from_index(self, index):
        new_melements = {}
        for i in range(len(self.melements)):
            if i == index:
                continue
            if i > index:
                i -= 1
            new_melements[i] = self.melements[i]
        new_positions = []
        for el in new_melements.values():
            new_positions.append(el.get_center())
        self.melements = new_melements
        self.positions = new_positions

    def add_element_in_position(self, position):
        melement = MElementObject.from_csv_file_data(
            self.data_file_path, self.atomic_number
        )
        self.melements[len(self.melements)] = melement
        self.positions.append(position)
        self.add(melement)
        return melement

    def transform_into_element_with_positions(self, els: 'MElementWithPositions'):
        animations = []
        if self.atomic_number != els.get_atomic_number():
            raise Exception(
                "You can't move to an element with different atomic number")
        indexes_to_remove = []
        indexes_already_used = []
        for i in range(len(self.melements)):
            curr_element = self.melements[i]
            if i < len(els.melements):
                assigned_element, ind = els.get_nearest_element(
                    indexes_already_used, curr_element)
                width = assigned_element.get_width()
                # TODO: Get opacity directly from the target somehow
                opacity = MElementObject().opacity
                should_remove = False
            else:
                assigned_element, ind = els.get_nearest_element(
                    [], curr_element)
                opacity = 0
                should_remove = True
                indexes_to_remove.append(i)
            ag = AnimationGroup(curr_element.animate.move_to(
                assigned_element).scale_to_fit_width(width).set_fill(opacity=opacity), remover=should_remove)
            animations.append(ag)
            indexes_already_used.append(ind)

        indexes_left_to_use = list(range(len(els.melements)))
        indexes_left_to_use = [
            i for i in indexes_left_to_use if i not in indexes_already_used]
        if len(els) > len(self.melements):
            for i in indexes_left_to_use:
                target_element = els.melements[i]
                closest_element, _ = self.get_nearest_element(
                    [], target_element)
                curr_element = self.add_element_in_position(
                    closest_element.get_center())
                curr_element.scale_to_fit_width(closest_element.get_width())
                curr_element.set_fill(opacity=0)
                opacity = MElementObject().opacity
                should_remove = False
                width = target_element.get_width()
                ag = AnimationGroup(curr_element.animate.move_to(
                    target_element).scale_to_fit_width(width).set_fill(opacity=opacity), remover=should_remove)
                animations.append(ag)

        for i in indexes_to_remove:
            self.remove_element_from_index(i)

        return AnimationGroup(*animations)


class MElementGroup(VGroup):
    def __init__(self, els: List[MElementWithPositions], *vmobjects, **kwargs):
        VGroup.__init__(self, *vmobjects, **kwargs)
        atomic_numbers = set()
        for el in els:
            if el.get_atomic_number() in atomic_numbers:
                raise Exception(
                    "More than one element with positions with same atomic number")
            atomic_numbers.add(el.get_atomic_number())
        self.els = {}
        for el in els:
            self.add_element(el)

    def add_element(self, el: MElementWithPositions):
        if el.get_atomic_number in self.els:
            raise Exception("Atomic number already in group")
        self.els[el.get_atomic_number()] = el
        self.add(el)

    def get_element_by_atomic_numbers(self):
        return self.els

    def transform_into_group(self, group: 'MElementGroup'):
        els_target = group.get_element_by_atomic_numbers()
        atomic_numbers = set()
        atomic_numbers.update(self.els.keys())
        atomic_numbers.update(els_target.keys())

        animations = []
        for atomic_number in atomic_numbers:
            if atomic_number in els_target and atomic_number in self.els:
                curr_el = self.els[atomic_number]
                target_el = els_target[atomic_number]
                animations.append(
                    curr_el.transform_into_element_with_positions(target_el))
            elif atomic_number in els_target:
                new_el = els_target[atomic_number].copy()
                new_el.set_fill(opacity=0)
                self.add_element(new_el)
                animations.append(new_el.animate.set_fill(
                    opacity=MElementObject().opacity))
            else:
                animations.append(
                    FadeOut(self.els[atomic_number]))
                self.els.pop(atomic_number)
        return AnimationGroup(*animations)


class PeriodicTable(MElementGroup):
    def __init__(self, data_file_path, *vmobjects, **kwargs):
        self.data_file_path = data_file_path
        els = self.get_els()
        MElementGroup.__init__(self, els, *vmobjects, **kwargs)

    def get_els(self):
        positions = self.elements_position_dict()
        base_element = MElementObject()
        mult_array = np.array(
            [base_element.get_width(), -base_element.get_height(), 0])

        els = []
        for element, position in positions.items():
            new_position = np.multiply(mult_array, np.array(position))
            els.append(MElementWithPositions(
                element, [new_position], self.data_file_path))

        return els

    def elements_position_dict(self):
        # TODO: Think of a better way of doing this. However, it works and looks good
        positions = {
            1: [0, 0, 0],
            2: [17, 0, 0],
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
