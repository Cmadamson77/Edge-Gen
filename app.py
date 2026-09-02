# ============================================================
# AI EDGE ART GENERATOR V3.3
# app.py
# ============================================================

import io
import random

import streamlit as st

from ai_edge_generator import (
    DEFAULT_COLOR_WEIGHTS,
    DEFAULT_SHAPE_WEIGHTS,
)

from ai_edge_custom import (
    DEFAULT_BACKGROUND,
    DEFAULT_CUSTOM_COLORS,
    create_custom_ai_edge_blueprint,
    normalize_hex,
    render_custom_png,
    render_custom_vector,
    valid_hex,
)


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="AI Edge Art Generator",
    page_icon="◼",
    layout="centered",
)

st.title(
    "AI Edge Art Generator"
)

st.write(
    "Create an AI Edge pattern from a stable baseline, "
    "then art-direct its density, color balance, and shape dominance."
)


# ============================================================
# SESSION STATE
# ============================================================

if "baseline_seed" not in st.session_state:

    st.session_state[
        "baseline_seed"
    ] = (
        random.SystemRandom()
        .randint(
            0,
            999_999_999,
        )
    )


if "generated_result" not in st.session_state:

    st.session_state[
        "generated_result"
    ] = None


# ============================================================
# PATTERN BASELINE
# ============================================================

st.subheader(
    "Pattern Baseline"
)

st.caption(
    "Keep the same seed to preserve the same overall footprint "
    "while changing negative space, color, or shape balance."
)


seed_col, seed_button_col = st.columns(
    [
        3,
        1,
    ]
)


with seed_col:

    baseline_seed = st.number_input(
        "Baseline seed",
        min_value=0,
        max_value=999_999_999,
        value=int(
            st.session_state[
                "baseline_seed"
            ]
        ),
        step=1,
    )


with seed_button_col:

    st.write("")
    st.write("")

    if st.button(
        "New Seed",
        use_container_width=True,
    ):

        st.session_state[
            "baseline_seed"
        ] = (
            random.SystemRandom()
            .randint(
                0,
                999_999_999,
            )
        )

        st.session_state[
            "generated_result"
        ] = None

        st.rerun()


st.session_state[
    "baseline_seed"
] = int(
    baseline_seed
)


# ============================================================
# DIMENSIONS
# ============================================================

st.subheader(
    "Dimensions"
)

st.caption(
    "Patterns are constructed on a 25 × 25 px grid. "
    "Artwork may bleed beyond the requested dimensions "
    "and is cropped to the final canvas."
)


dimension_col_1, dimension_col_2 = st.columns(
    2
)


with dimension_col_1:

    width = st.number_input(
        "Width (px)",
        min_value=100,
        max_value=10000,
        value=1200,
        step=1,
    )


with dimension_col_2:

    height = st.number_input(
        "Height (px)",
        min_value=100,
        max_value=10000,
        value=1600,
        step=1,
    )


# ============================================================
# NEGATIVE SPACE
# ============================================================

st.subheader(
    "Negative Space"
)

negative_space = st.slider(
    "Pattern openness",
    min_value=0,
    max_value=60,
    value=15,
    step=1,
    help=(
        "15% is the default dense composition. "
        "Higher values progressively create more open areas "
        "while preserving the baseline footprint."
    ),
)


# ============================================================
# COLOR BALANCE
# ============================================================

st.subheader(
    "Color Balance"
)

st.caption(
    "Edit any hex value to change the palette. "
    "Use the slider to control how dominant that color is."
)


color_order = [
    "Brown",
    "Pink",
    "Red",
    "Yellow",
    "Blue",
    "Gray",
    "Ice Blue",
]


custom_colors = {}

color_weights = {}


# ============================================================
# COLUMN LABELS
# ============================================================

header_number, header_hex, header_swatch, header_slider = (
    st.columns(
        [
            0.35,
            1.6,
            0.65,
            4.4,
        ]
    )
)


with header_number:

    st.caption("")


with header_hex:

    st.caption(
        "HEX"
    )


with header_swatch:

    st.caption(
        "COLOR"
    )


with header_slider:

    st.caption(
        "BALANCE"
    )


# ============================================================
# COLOR ROWS
# ============================================================

for index, color_name in enumerate(
    color_order,
    start=1,
):

    number_col, hex_col, swatch_col, slider_col = (
        st.columns(
            [
                0.35,
                1.6,
                0.65,
                4.4,
            ],
            vertical_alignment="center",
        )
    )


    # --------------------------------------------------------
    # NUMBER
    # --------------------------------------------------------

    with number_col:

        st.markdown(
            f"### {index}"
        )


    # --------------------------------------------------------
    # HEX INPUT
    # --------------------------------------------------------

    with hex_col:

        entered_hex = st.text_input(
            label=(
                f"{color_name} hex"
            ),

            value=(
                DEFAULT_CUSTOM_COLORS[
                    color_name
                ]
            ),

            key=(
                f"hex_{color_name}"
            ),

            label_visibility="collapsed",
        )


    normalized = normalize_hex(
        entered_hex
    )


    custom_colors[
        color_name
    ] = normalized


    # --------------------------------------------------------
    # SWATCH
    # --------------------------------------------------------

    with swatch_col:

        if valid_hex(
            normalized
        ):

            swatch_color = (
                normalized
            )

        else:

            swatch_color = (
                "#FFFFFF"
            )


        st.markdown(
            (
                '<div style="'
                'width:42px;'
                'height:42px;'
                'border-radius:3px;'
                'border:1px solid rgba(0,0,0,.18);'
                f'background:{swatch_color};'
                'margin:auto;'
                '"></div>'
            ),
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # BALANCE SLIDER
    # --------------------------------------------------------

    with slider_col:

        color_weights[
            color_name
        ] = st.slider(
            label=(
                f"{color_name} balance"
            ),

            min_value=0,
            max_value=40,

            value=int(
                DEFAULT_COLOR_WEIGHTS[
                    color_name
                ]
            ),

            step=1,

            key=(
                f"weight_{color_name}"
            ),

            label_visibility="collapsed",
        )


# ============================================================
# BACKGROUND
# ============================================================

st.write("")

st.markdown(
    "**Background**"
)


bg_label_col, bg_hex_col, bg_swatch_col, bg_space_col = (
    st.columns(
        [
            0.35,
            1.6,
            0.65,
            4.4,
        ],
        vertical_alignment="center",
    )
)


with bg_label_col:

    st.markdown(
        "### B"
    )


with bg_hex_col:

    background = st.text_input(
        "Background hex",
        value=DEFAULT_BACKGROUND,
        key="background_hex",
        label_visibility="collapsed",
    )


background = normalize_hex(
    background
)


with bg_swatch_col:

    if valid_hex(
        background
    ):

        background_preview = (
            background
        )

    else:

        background_preview = (
            "#FFFFFF"
        )


    st.markdown(
        (
            '<div style="'
            'width:42px;'
            'height:42px;'
            'border-radius:3px;'
            'border:1px solid rgba(0,0,0,.18);'
            f'background:{background_preview};'
            'margin:auto;'
            '"></div>'
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# SHAPE DOMINANCE
# ============================================================

st.subheader(
    "Shape Dominance"
)

st.caption(
    "Increase a motif to make it more prominent. "
    "No motif disappears completely."
)


shape_weights = {}


shape_col_1, shape_col_2 = st.columns(
    2
)


with shape_col_1:

    shape_weights[
        "Checkerboard"
    ] = st.slider(
        "Checkerboard",
        1,
        10,
        int(
            DEFAULT_SHAPE_WEIGHTS[
                "Checkerboard"
            ]
        ),
    )


    shape_weights[
        "Stair Step"
    ] = st.slider(
        "Stair Step",
        1,
        10,
        int(
            DEFAULT_SHAPE_WEIGHTS[
                "Stair Step"
            ]
        ),
    )


with shape_col_2:

    shape_weights[
        "Lattice"
    ] = st.slider(
        "Lattice",
        1,
        10,
        int(
            DEFAULT_SHAPE_WEIGHTS[
                "Lattice"
            ]
        ),
    )


    shape_weights[
        "Pills"
    ] = st.slider(
        "Pills",
        1,
        10,
        int(
            DEFAULT_SHAPE_WEIGHTS[
                "Pills"
            ]
        ),
    )


# ============================================================
# SPLICE
# ============================================================

st.subheader(
    "Splice"
)

splice_enabled = st.checkbox(
    "Enable diagonal splice",
    value=True,
)


# ============================================================
# VALIDATION
# ============================================================

invalid_colors = [
    (
        index,
        name,
        value,
    )
    for index, (
        name,
        value,
    )
    in enumerate(
        custom_colors.items(),
        start=1,
    )
    if not valid_hex(
        value
    )
]


background_invalid = (
    not valid_hex(
        background
    )
)


# ============================================================
# GENERATE
# ============================================================

st.write("")


if st.button(
    "Generate Pattern",
    type="primary",
    use_container_width=True,
):

    if invalid_colors:

        invalid_text = ", ".join(
            (
                f"Color {index}"
            )
            for index, name, value
            in invalid_colors
        )

        st.error(
            f"Please enter a valid 6-digit hex value for: "
            f"{invalid_text}."
        )


    elif background_invalid:

        st.error(
            "Please enter a valid 6-digit hex value "
            "for the background."
        )


    elif sum(
        color_weights.values()
    ) <= 0:

        st.error(
            "At least one color must have a balance above zero."
        )


    else:

        with st.spinner(
            "Generating AI Edge pattern..."
        ):

            try:

                # ====================================================
                # ONE BLUEPRINT
                # ====================================================

                blueprint = (
                    create_custom_ai_edge_blueprint(
                        width=int(
                            width
                        ),

                        height=int(
                            height
                        ),

                        seed=int(
                            st.session_state[
                                "baseline_seed"
                            ]
                        ),

                        negative_space=(
                            negative_space
                        ),

                        colors=(
                            custom_colors
                        ),

                        background=(
                            background
                        ),

                        color_weights=(
                            color_weights
                        ),

                        shape_weights=(
                            shape_weights
                        ),

                        splice_enabled=(
                            splice_enabled
                        ),
                    )
                )


                # ====================================================
                # BOTH OUTPUTS FROM SAME BLUEPRINT
                # ====================================================

                image = render_custom_png(
                    blueprint
                )


                production_vector = (
                    render_custom_vector(
                        blueprint
                    )
                )


                st.session_state[
                    "generated_result"
                ] = {
                    "image":
                        image,

                    "production_vector":
                        production_vector,

                    "metadata": {
                        "seed":
                            blueprint.seed,

                        "width":
                            blueprint.width,

                        "height":
                            blueprint.height,
                    },
                }


            except Exception as error:

                st.exception(
                    error
                )


# ============================================================
# RESULT
# ============================================================

result = st.session_state.get(
    "generated_result"
)


if result is not None:

    image = result[
        "image"
    ]

    production_vector = result[
        "production_vector"
    ]

    metadata = result[
        "metadata"
    ]


    st.divider()


    # ========================================================
    # PREVIEW
    # ========================================================

    st.image(
        image,
        caption=(
            "AI Edge — "
            f"Baseline {metadata['seed']}"
        ),
        use_container_width=True,
    )


    # ========================================================
    # PNG BUFFER
    # ========================================================

    png_buffer = io.BytesIO()


    image.save(
        png_buffer,
        format="PNG",
    )


    filename_base = (
        f"ai_edge_"
        f"{metadata['seed']}_"
        f"{metadata['width']}x"
        f"{metadata['height']}"
    )


    # ========================================================
    # DOWNLOADS
    # ========================================================

    download_col_1, download_col_2 = st.columns(
        2
    )


    with download_col_1:

        st.download_button(
            label="Download PNG",

            data=png_buffer.getvalue(),

            file_name=(
                filename_base
                +
                ".png"
            ),

            mime="image/png",

            use_container_width=True,
        )


    with download_col_2:

        st.download_button(
            label="Download Production Vector",

            data=production_vector,

            file_name=(
                filename_base
                +
                "_production.svg"
            ),

            mime="image/svg+xml",

            use_container_width=True,
        )


    st.info(
        "Baseline seed: "
        f"{metadata['seed']}. "
        "Keep this seed to preserve the same footprint while "
        "changing negative space, palette, color balance, "
        "and shape dominance."
    )