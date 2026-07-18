"""STEM'N'TIMI EM0.01 - 8-second trigonometry cutaway.

Render with Manim Community Edition 0.20.1:

    manim -pqh em001_trig_projection.py TrigProjectionInsert

The scene intentionally uses Text instead of MathTex, so a LaTeX installation
is not required. Total scene duration is exactly 8 seconds:
1 second fade-in + 6 seconds rotation + 1 second hold.
"""

from manim import *
import numpy as np


# Monochrome STEM'N'TIMI palette.
BACKGROUND = ManimColor("#F5F3EE")
INK = ManimColor("#111111")
GRAPHITE = ManimColor("#555555")
MID_GREY = ManimColor("#888888")
LIGHT_GREY = ManimColor("#D9D9D9")

config.background_color = BACKGROUND


def make_robot(angle: float, centre: np.ndarray) -> VGroup:
    """Create a simple top-down two-wheeled robot pointing along +x."""
    body = RoundedRectangle(
        width=1.35,
        height=0.72,
        corner_radius=0.12,
        color=INK,
        stroke_width=3,
        fill_color=BACKGROUND,
        fill_opacity=1,
    )

    upper_wheel = RoundedRectangle(
        width=0.45,
        height=0.13,
        corner_radius=0.04,
        color=INK,
        stroke_width=3,
        fill_color=INK,
        fill_opacity=1,
    ).move_to(UP * 0.46)

    lower_wheel = upper_wheel.copy().move_to(DOWN * 0.46)

    heading_mark = Triangle(
        color=INK,
        fill_color=INK,
        fill_opacity=1,
        stroke_width=0,
    ).scale(0.13).rotate(-PI / 2).move_to(RIGHT * 0.49)

    centre_dot = Dot(ORIGIN, radius=0.045, color=INK)
    robot = VGroup(body, upper_wheel, lower_wheel, heading_mark, centre_dot)
    robot.rotate(angle, about_point=ORIGIN)
    robot.move_to(centre)
    return robot


class TrigProjectionInsert(Scene):
    """Rotate a robot while its velocity components update continuously."""

    def construct(self):
        # Avoid zero-length component arrows by beginning and ending slightly
        # away from 0 and 90 degrees.
        theta = ValueTracker(10 * DEGREES)
        speed = 1.0
        display_length = 2.55

        axes = Axes(
            x_range=[-3.5, 3.6, 1],
            y_range=[-2.7, 2.8, 1],
            x_length=6.4,
            y_length=5.0,
            tips=True,
            axis_config={
                "color": MID_GREY,
                "stroke_width": 2,
                "include_ticks": False,
            },
        ).shift(LEFT * 2.2)

        origin = axes.c2p(0, 0)

        x_label = Text("x", font_size=28, color=GRAPHITE).next_to(
            axes.x_axis.get_end(), DOWN, buff=0.12
        )
        y_label = Text("y", font_size=28, color=GRAPHITE).next_to(
            axes.y_axis.get_end(), LEFT, buff=0.12
        )

        robot = always_redraw(lambda: make_robot(theta.get_value(), origin))

        velocity = always_redraw(
            lambda: Arrow(
                origin,
                axes.c2p(
                    display_length * np.cos(theta.get_value()),
                    display_length * np.sin(theta.get_value()),
                ),
                buff=0,
                color=INK,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.14,
            )
        )

        x_component = always_redraw(
            lambda: Arrow(
                origin,
                axes.c2p(display_length * np.cos(theta.get_value()), 0),
                buff=0,
                color=GRAPHITE,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.16,
            )
        )

        y_component = always_redraw(
            lambda: Arrow(
                axes.c2p(display_length * np.cos(theta.get_value()), 0),
                axes.c2p(
                    display_length * np.cos(theta.get_value()),
                    display_length * np.sin(theta.get_value()),
                ),
                buff=0,
                color=MID_GREY,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.16,
            )
        )

        projection_line = always_redraw(
            lambda: DashedLine(
                axes.c2p(
                    display_length * np.cos(theta.get_value()),
                    display_length * np.sin(theta.get_value()),
                ),
                axes.c2p(0, display_length * np.sin(theta.get_value())),
                dash_length=0.11,
                color=LIGHT_GREY,
                stroke_width=3,
            )
        )

        angle_arc = always_redraw(
            lambda: Arc(
                radius=0.75,
                start_angle=0,
                angle=theta.get_value(),
                arc_center=origin,
                color=GRAPHITE,
                stroke_width=3,
            )
        )

        theta_label = always_redraw(
            lambda: Text("θ", font_size=27, color=GRAPHITE).move_to(
                origin
                + 0.95
                * np.array(
                    [
                        np.cos(theta.get_value() / 2),
                        np.sin(theta.get_value() / 2),
                        0,
                    ]
                )
            )
        )

        vx_label = always_redraw(
            lambda: Text("vₓ", font_size=25, color=GRAPHITE).next_to(
                x_component, DOWN, buff=0.12
            )
        )

        vy_label = always_redraw(
            lambda: Text("vᵧ", font_size=25, color=MID_GREY).next_to(
                y_component, RIGHT, buff=0.12
            )
        )

        velocity_label = always_redraw(
            lambda: Text("v", font_size=27, color=INK).next_to(
                velocity.get_end(),
                np.array(
                    [
                        np.cos(theta.get_value()),
                        np.sin(theta.get_value()),
                        0,
                    ]
                ),
                buff=0.1,
            )
        )

        # Right-side explanation panel. DecimalNumber values update every frame.
        panel_title = Text(
            "Forward velocity on map axes",
            font_size=30,
            weight=BOLD,
            color=INK,
        )
        equation_x = Text("vₓ = v cos(θ)", font_size=31, color=GRAPHITE)
        equation_y = Text("vᵧ = v sin(θ)", font_size=31, color=MID_GREY)

        angle_name = Text("θ =", font_size=27, color=GRAPHITE)
        angle_value = DecimalNumber(
            theta.get_value() / DEGREES,
            num_decimal_places=0,
            unit="°",
            font_size=27,
            color=INK,
        )
        angle_value.add_updater(
            lambda number: number.set_value(theta.get_value() / DEGREES)
        )
        angle_row = VGroup(angle_name, angle_value).arrange(RIGHT, buff=0.12)

        vx_name = Text("vₓ =", font_size=27, color=GRAPHITE)
        vx_value = DecimalNumber(
            speed * np.cos(theta.get_value()),
            num_decimal_places=2,
            font_size=27,
            color=INK,
        )
        vx_value.add_updater(
            lambda number: number.set_value(speed * np.cos(theta.get_value()))
        )
        vx_row = VGroup(vx_name, vx_value).arrange(RIGHT, buff=0.12)

        vy_name = Text("vᵧ =", font_size=27, color=MID_GREY)
        vy_value = DecimalNumber(
            speed * np.sin(theta.get_value()),
            num_decimal_places=2,
            font_size=27,
            color=INK,
        )
        vy_value.add_updater(
            lambda number: number.set_value(speed * np.sin(theta.get_value()))
        )
        vy_row = VGroup(vy_name, vy_value).arrange(RIGHT, buff=0.12)

        readout = VGroup(angle_row, vx_row, vy_row).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22
        )

        panel = VGroup(panel_title, equation_x, equation_y, readout).arrange(
            DOWN, aligned_edge=LEFT, buff=0.35
        ).to_edge(RIGHT, buff=0.55)

        panel_rule = Line(
            panel.get_left() + LEFT * 0.18 + UP * 1.55,
            panel.get_left() + LEFT * 0.18 + DOWN * 1.55,
            color=LIGHT_GREY,
            stroke_width=4,
        )

        dynamic_objects = VGroup(
            projection_line,
            x_component,
            y_component,
            velocity,
            robot,
            angle_arc,
            theta_label,
            vx_label,
            vy_label,
            velocity_label,
        )

        # 1 second reveal + 6 second rotation + 1 second hold = 8 seconds.
        self.play(
            FadeIn(axes),
            FadeIn(x_label),
            FadeIn(y_label),
            FadeIn(dynamic_objects),
            FadeIn(panel),
            FadeIn(panel_rule),
            run_time=1,
        )
        self.play(
            theta.animate.set_value(80 * DEGREES),
            run_time=6,
            rate_func=smooth,
        )
        self.wait(1)

