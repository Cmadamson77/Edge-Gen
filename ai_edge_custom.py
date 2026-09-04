# ============================================================
# AI EDGE CUSTOM PALETTE LAYER
# ai_edge_custom.py
# ============================================================
#
# V3.7
#
# UNIVERSAL DYNAMIC PALETTE FIX
#
# Supports:
#
# - 1–20 artwork colors
# - completely arbitrary hex values
# - completely arbitrary slot names
# - custom background
# - no dependency on legacy names like:
#       Brown
#       Pink
#       Red
#       Yellow
#       Blue
#       Gray
#       Ice Blue
#
# This file deliberately patches the generator's color-choice
# function during blueprint creation so legacy palette names
# can NEVER leak into a dynamic palette.
#
# ============================================================


from contextlib import contextmanager
import random

import ai_edge_generator as generator
import ai_edge_vector as vector


# ============================================================
# NEW APPROVED DEFAULT PALETTE
# ============================================================

DEFAULT_PALETTE = [
    {
        "hex": "#FF515B",
        "weight": 10,
    },
    {
        "hex": "#D6A9E7",
        "weight": 16,
    },
    {
        "hex": "#8C1018",
        "weight": 8,
    },
    {
        "hex": "#FF6410",
        "weight": 10,
    },
    {
        "hex": "#F7D3D3",
        "weight": 10,
    },
    {
        "hex": "#A72AFF",
        "weight": 8,
    },
    {
        "hex": "#E8C7EF",
        "weight": 4,
    },
    {
        "hex": "#3D2C63",
        "weight": 4,
    },
    {
        "hex": "#123FC4",
        "weight": 10,
    },
    {
        "hex": "#7DA1EB",
        "weight": 8,
    },
    {
        "hex": "#D7E1F4",
        "weight": 4,
    },
    {
        "hex": "#7D3E10",
        "weight": 8,
    },
    {
        "hex": "#FFB56A",
        "weight": 4,
    },
    {
        "hex": "#FF8136",
        "weight": 4,
    },
    {
        "hex": "#FF1721",
        "weight": 10,
    },
]


DEFAULT_BACKGROUND = "#EAE7D9"

MIN_COLORS = 1
MAX_COLORS = 20


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
# WEIGHTED CHOICE
# ============================================================

def dynamic_weighted_choice(
    rng,
    weights,
):

    names = list(
        weights.keys()
    )

    values = [
        max(
            0.0,
            float(
                weights[name]
            ),
        )
        for name
        in names
    ]

    if not names:

        raise ValueError(
            "No artwork colors are available."
        )

    if sum(
        values
    ) <= 0:

        values = [
            1.0
            for _
            in names
        ]

    return rng.choices(
        names,
        weights=values,
        k=1,
    )[0]


# ============================================================
# BUILD DYNAMIC COLOR SYSTEM
# ============================================================

def build_color_system(
    palette_slots,
):

    colors = {}
    weights = {}


    for index, slot in enumerate(
        palette_slots,
        start=1,
    ):

        slot_name = (
            f"Color {index}"
        )


        colors[
            slot_name
        ] = validated_hex(
            slot[
                "hex"
            ]
        )


        weights[
            slot_name
        ] = max(
            0.0,
            float(
                slot[
                    "weight"
                ]
            ),
        )


    if not colors:

        raise ValueError(
            "At least one artwork color is required."
        )


    if sum(
        weights.values()
    ) <= 0:

        raise ValueError(
            "At least one artwork color must have "
            "a balance above zero."
        )


    return (
        colors,
        weights,
    )


# ============================================================
# UNIVERSAL COLOR CHOICE
# ============================================================
#
# This completely replaces the old generator behavior:
#
#     COLORS["Brown"]
#     COLORS["Red"]
#     etc.
#
# It uses ONLY the current dynamic palette.
#
# ============================================================

def make_dynamic_color_chooser(
    colors,
    weights,
):

    def choose_region_colors(
        region,
        ignored_color_weights=None,
    ):

        rng = random.Random(
            region.color_seed
        )


        # ----------------------------------------------------
        # PRIMARY
        # ----------------------------------------------------

        primary_name = (
            dynamic_weighted_choice(
                rng,
                weights,
            )
        )


        # ----------------------------------------------------
        # SECONDARY
        # ----------------------------------------------------

        secondary_weights = {
            name: weight
            for name, weight
            in weights.items()
            if (
                name
                !=
                primary_name
                and
                weight
                >
                0
            )
        }


        if not secondary_weights:

            secondary_weights = {
                name: 1.0
                for name
                in colors.keys()
                if name
                !=
                primary_name
            }


        if secondary_weights:

            secondary_name = (
                dynamic_weighted_choice(
                    rng,
                    secondary_weights,
                )
            )

        else:

            secondary_name = (
                primary_name
            )


        # ----------------------------------------------------
        # SPLICE
        # ----------------------------------------------------

        splice_weights = {
            name: weight
            for name, weight
            in weights.items()
            if (
                name
                !=
                primary_name
                and
                weight
                >
                0
            )
        }


        if splice_weights:

            splice_name = (
                dynamic_weighted_choice(
                    rng,
                    splice_weights,
                )
            )

        else:

            splice_name = (
                secondary_name
            )


        return (
            colors[
                primary_name
            ],

            colors[
                secondary_name
            ],

            colors[
                splice_name
            ],
        )


    return choose_region_colors


# ============================================================
# TEMPORARY GENERATOR ENVIRONMENT
# ============================================================

@contextmanager
def custom_palette_environment(
    colors,
    color_weights,
    background,
):

    clean_colors = {
        name: validated_hex(
            value
        )
        for name, value
        in colors.items()
    }


    clean_weights = {
        name: max(
            0.0,
            float(
                color_weights[
                    name
                ]
            ),
        )
        for name
        in clean_colors.keys()
    }


    clean_background = (
        validated_hex(
            background
        )
    )


    # --------------------------------------------------------
    # SAVE ALL ORIGINAL GENERATOR STATE
    # --------------------------------------------------------

    original_colors = (
        generator.COLORS
    )

    original_weights = (
        generator.DEFAULT_COLOR_WEIGHTS
    )

    original_background = (
        generator.BACKGROUND
    )

    original_choose_region_colors = (
        generator.choose_region_colors
    )

    original_vector_background = (
        vector.BACKGROUND
    )


    try:

        # ----------------------------------------------------
        # INSTALL DYNAMIC PALETTE
        # ----------------------------------------------------

        generator.COLORS = dict(
            clean_colors
        )


        generator.DEFAULT_COLOR_WEIGHTS = dict(
            clean_weights
        )


        generator.BACKGROUND = (
            clean_background
        )


        # ----------------------------------------------------
        # CRITICAL UNIVERSAL FIX
        # ----------------------------------------------------
        #
        # No matter what the old generator thinks the colors
        # are called, all region color selection now goes
        # through this palette-aware chooser.
        #
        # ----------------------------------------------------

        generator.choose_region_colors = (
            make_dynamic_color_chooser(
                clean_colors,
                clean_weights,
            )
        )


        vector.BACKGROUND = (
            clean_background
        )


        yield


    finally:

        # ----------------------------------------------------
        # RESTORE ORIGINAL GENERATOR
        # ----------------------------------------------------

        generator.COLORS = (
            original_colors
        )


        generator.DEFAULT_COLOR_WEIGHTS = (
            original_weights
        )


        generator.BACKGROUND = (
            original_background
        )


        generator.choose_region_colors = (
            original_choose_region_colors
        )


        vector.BACKGROUND = (
            original_vector_background
        )


# ============================================================
# CREATE BLUEPRINT
# ============================================================

def create_custom_ai_edge_blueprint(
    width,
    height,
    seed,
    negative_space,
    palette_slots,
    background,
    shape_weights,
    splice_enabled=True,
):

    (
        colors,
        color_weights,
    ) = build_color_system(
        palette_slots
    )


    with custom_palette_environment(
        colors=colors,
        color_weights=color_weights,
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