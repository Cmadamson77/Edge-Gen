# ============================================================
# AI EDGE CUSTOM PALETTE LAYER
# ai_edge_custom.py
# ============================================================
#
# Allows the Streamlit app to temporarily supply:
#
# - seven custom artwork colors
# - a custom background color
#
# WITHOUT changing the approved AI Edge pattern engine.
#
# ============================================================

from contextlib import contextmanager

import ai_edge_generator as generator
import ai_edge_vector as vector


# ============================================================
# DEFAULT APPROVED PALETTE
# ============================================================

DEFAULT_CUSTOM_COLORS = {
    "Brown": "#4B190F",
    "Pink": "#F9BFF9",
    "Red": "#FF0015",
    "Yellow": "#FFFF8F",
    "Blue": "#416CA4",
    "Gray": "#A6B5C2",
    "Ice Blue": "#CBFEFF",
}

DEFAULT_BACKGROUND = "#EAE7D9"


# ============================================================
# HEX HELPERS
# ============================================================

def normalize_hex(
    value,
):

    value = str(
        value
    ).strip().upper()

    if not value.startswith(
        "#"
    ):
        value = (
            "#"
            +
            value
        )

    return value


def valid_hex(
    value,
):

    value = normalize_hex(
        value
    )

    if len(
        value
    ) != 7:
        return False

    try:

        int(
            value[1:],
            16,
        )

    except ValueError:

        return False

    return True


def validated_hex(
    value,
):

    value = normalize_hex(
        value
    )

    if not valid_hex(
        value
    ):

        raise ValueError(
            f"{value} is not a valid 6-digit hex color."
        )

    return value


# ============================================================
# TEMPORARY PALETTE ENVIRONMENT
# ============================================================

@contextmanager
def custom_palette_environment(
    colors,
    background,
):

    clean_colors = {
        name: validated_hex(
            value
        )
        for name, value
        in colors.items()
    }

    clean_background = validated_hex(
        background
    )

    original_generator_colors = (
        generator.COLORS
    )

    original_generator_background = (
        generator.BACKGROUND
    )

    original_vector_background = (
        vector.BACKGROUND
    )

    try:

        generator.COLORS = dict(
            clean_colors
        )

        generator.BACKGROUND = (
            clean_background
        )

        # The existing Production Vector renderer imports its
        # background value at module load, so keep it synchronized.

        vector.BACKGROUND = (
            clean_background
        )

        yield

    finally:

        generator.COLORS = (
            original_generator_colors
        )

        generator.BACKGROUND = (
            original_generator_background
        )

        vector.BACKGROUND = (
            original_vector_background
        )


# ============================================================
# PUBLIC BLUEPRINT GENERATOR
# ============================================================

def create_custom_ai_edge_blueprint(
    width,
    height,
    seed,
    negative_space,
    colors,
    background,
    color_weights,
    shape_weights,
    splice_enabled=True,
):

    with custom_palette_environment(
        colors=colors,
        background=background,
    ):

        blueprint = (
            generator.create_ai_edge_blueprint(
                width=width,
                height=height,
                seed=seed,
                negative_space=negative_space,
                color_weights=color_weights,
                shape_weights=shape_weights,
                splice_enabled=splice_enabled,
            )
        )

        # Preserve the custom background directly in the
        # completed blueprint so the PNG renderer remains correct
        # after the temporary environment is restored.

        blueprint.background = (
            validated_hex(
                background
            )
        )

        return blueprint


# ============================================================
# PNG
# ============================================================

def render_custom_png(
    blueprint,
):

    return generator.render_blueprint_png(
        blueprint
    )


# ============================================================
# PRODUCTION VECTOR
# ============================================================

def render_custom_vector(
    blueprint,
):

    # The existing vector renderer reads a module-level
    # BACKGROUND value. Temporarily synchronize it to the
    # blueprint before rendering.

    original_vector_background = (
        vector.BACKGROUND
    )

    try:

        vector.BACKGROUND = (
            blueprint.background
        )

        return (
            vector.generate_vector_from_blueprint(
                blueprint
            )
        )

    finally:

        vector.BACKGROUND = (
            original_vector_background
        )