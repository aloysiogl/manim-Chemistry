from manim import Transform, AnimationGroup


def convert_chemical_texts(source, target):
    elements_transform = source.get_element_group(
    ).transform_into_group(target.get_element_group())
    text_transform = Transform(
        source.get_letter_group(), target.get_letter_group())
    return AnimationGroup(elements_transform, text_transform)
