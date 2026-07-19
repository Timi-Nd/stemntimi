"""STEM'N'TIMI EM0.01 - 8-second trigonometry cutaway.

Render with Manim Community Edition 0.20.1:

    manim -pqh em001_trig_projection.py TrigProjectionInsert

The scene intentionally uses Text instead of MathTex, so a LaTeX installation
is not required. Total scene duration is exactly 8 seconds:
1-second fade-in + 6-second rotation + 1-second hold.
"""

from manim import *
import numpy as np
import re
import sys


# Refined STEM'N'TIMI Dark Palette.
BACKGROUND = BLACK
PRIMARY = WHITE
X_COLOR = BLUE
Y_COLOR = GREEN
DIM = GREY_B

config.background_color = BACKGROUND


def make_robot(angle: float, centre: np.ndarray) -> VGroup:
    """Create a sleek top-down robot pointing along +x."""
    # Scaled down slightly to ensure labels never overlap the body
    body = RoundedRectangle(
        width=0.75,
        height=0.45,
        corner_radius=0.08,
        color=PRIMARY,
        stroke_width=2,
        fill_color=BACKGROUND,
        fill_opacity=1,
    )

    wheel_config = {
        "width": 0.22,
        "height": 0.08,
        "corner_radius": 0.02,
        "color": PRIMARY,
        "fill_color": PRIMARY,
        "fill_opacity": 1,
        "stroke_width": 0,
    }

    upper_wheel = RoundedRectangle(**wheel_config).move_to(UP * 0.26)
    lower_wheel = RoundedRectangle(**wheel_config).move_to(DOWN * 0.26)

    heading_mark = Triangle(
        color=PRIMARY,
        fill_color=PRIMARY,
        fill_opacity=1,
        stroke_width=0,
    ).scale(0.08).rotate(-PI / 2).move_to(RIGHT * 0.28)

    centre_dot = Dot(ORIGIN, radius=0.03, color=PRIMARY)
    robot = VGroup(body, upper_wheel, lower_wheel, heading_mark, centre_dot)
    robot.rotate(angle, about_point=ORIGIN)
    robot.move_to(centre)
    return robot


class TrigProjectionInsert(Scene):
    """Rotate a robot while its velocity components update continuously."""

    def construct(self):
        # Default Parameters
        V_START = 0.0
        V_END = 0.0
        OMEGA_DEG = 0.0  # degrees per second
        THETA_START = 0.0
        REF_DURATION = 6.0
        DURATION = REF_DURATION
        target_pos = None
        display_selection = []
        show_grid = False
        show_triangle = False
        show_radar = False
        show_subtitles = False

        # Interactive Console Input
        if sys.stdin and sys.stdin.isatty():
            print("\n--- Robot Motion Configuration ---")
            print("Press Enter to keep the default value.")

            def get_nums(prompt, default_vals):
                while True:
                    try:
                        s = input(prompt).strip()
                        if not s:
                            return default_vals
                        # Split by common separators (space, comma, semicolon)
                        parts = re.split(r'[,\s;]+', s)
                        nums = []
                        for p in parts:
                            p = p.strip("()[]")
                            if not p: continue
                            # Handle dash as a range separator (if not just a leading negative sign)
                            dash_idx = p.find("-", 1)
                            if dash_idx != -1:
                                nums.append(float(p[:dash_idx]))
                                nums.append(float(p[dash_idx+1:]))
                            else:
                                nums.append(float(p))
                        if nums:
                            return nums
                        print("No valid numbers found. Please try again.")
                    except (ValueError, IndexError):
                        print("Invalid format. Please enter numbers or a range (e.g. 0.5-1.5).")
                    except EOFError:
                        return default_vals

            # Linear Velocity
            v_nums = get_nums(f"Linear Velocity (v) or range (e.g. 0.5-1.5) [default {V_START}]: ", [V_START, V_END])
            V_START, V_END = v_nums[0], (v_nums[1] if len(v_nums) > 1 else v_nums[0])

            # Angle (θ)
            t_nums = get_nums(f"Angle (θ) in degrees or range (e.g. 10-80) [default {THETA_START / DEGREES}]: ", [THETA_START / DEGREES])
            if len(t_nums) >= 2:
                THETA_START = t_nums[0] * DEGREES
                OMEGA_DEG = (t_nums[1] - t_nums[0]) / REF_DURATION
            else:
                THETA_START = t_nums[0] * DEGREES

            # Angular Velocity (ω)
            w_nums = get_nums(f"Angular Velocity (ω) in deg/s or range (e.g. 10-80) [default {OMEGA_DEG:.2f}]: ", [OMEGA_DEG])
            if len(w_nums) >= 2:
                # Interpret range as an angle sweep
                THETA_START = w_nums[0] * DEGREES
                OMEGA_DEG = (w_nums[1] - w_nums[0]) / REF_DURATION
            else:
                OMEGA_DEG = w_nums[0]

            # Target Coordinate
            while True:
                target_nums = get_nums("Target Coordinate x,y (e.g. 2,2) [none]: ", None)
                if not target_nums:
                    break
                if len(target_nums) >= 2:
                    target_pos = np.array([target_nums[0], target_nums[1]])
                    break
                print("Please enter both X and Y coordinates (e.g. 2, 2).")

            # Info Selection
            try:
                show_in = input("Display Info (v, omega, x, y, theta, vx, vy) [all]: ").strip().lower()
                if show_in:
                    # Robust parsing to handle parentheses, commas, spaces, etc.
                    display_selection = re.findall(r"\w+", show_in)

                # Beginner Aids Keywords
                if "grid" in display_selection: show_grid = True
                if "triangle" in display_selection: show_triangle = True
                if "radar" in display_selection: show_radar = True
                if "subtitles" in display_selection: show_subtitles = True

                # Beginner Aids Master Toggle
                try:
                    ba_in = input("Enable beginner visual aids (grid, triangle, radar, subtitles)? [y/n] [default n]: ").strip().lower()
                    if ba_in.startswith('y'):
                        show_grid = show_triangle = show_radar = show_subtitles = True
                except EOFError:
                    pass
            except EOFError:
                pass

        OMEGA_VAL = OMEGA_DEG * DEGREES
        A_VAL = (V_END - V_START) / REF_DURATION

        def get_integrated_pos(t):
            """Calculate (x, y) coordinates based on integrated motion (v=v0+at, theta=th0+wt)."""
            if abs(OMEGA_VAL) < 1e-8:
                # Linear motion: dist = integral (v0 + at) dt = v0*t + 0.5*a*t^2
                dist = V_START * t + 0.5 * A_VAL * (t**2)
                return dist * np.cos(THETA_START), dist * np.sin(THETA_START)
            else:
                curr_th = THETA_START + OMEGA_VAL * t
                # x(t) = (v0/w)*(sin(th_t)-sin(th0)) + (a/w)*t*sin(th_t) + (a/w^2)*(cos(th_t)-cos(th0))
                x_coord = (V_START / OMEGA_VAL) * (np.sin(curr_th) - np.sin(THETA_START)) + \
                          (A_VAL / OMEGA_VAL) * t * np.sin(curr_th) + \
                          (A_VAL / (OMEGA_VAL**2)) * (np.cos(curr_th) - np.cos(THETA_START))
                # y(t) = -(v0/w)*(cos(th_t)-cos(th0)) - (a/w)*t*cos(th_t) + (a/w^2)*(sin(th_t)-sin(th0))
                y_coord = -(V_START / OMEGA_VAL) * (np.cos(curr_th) - np.cos(THETA_START)) - \
                          (A_VAL / OMEGA_VAL) * t * np.cos(curr_th) + \
                          (A_VAL / (OMEGA_VAL**2)) * (np.sin(curr_th) - np.sin(THETA_START))
                return x_coord, y_coord

        def get_curr_v():
            t = time_tracker.get_value()
            return V_START + A_VAL * t

        # Stopping logic: find time t in [0, REF_DURATION] that minimizes distance to target_pos
        if target_pos is not None:
            best_t = 0
            min_dist = float('inf')
            # Sample dense points to find the closest approach
            for t_sample in np.linspace(0, REF_DURATION, 601):
                px, py = get_integrated_pos(t_sample)
                dist = np.linalg.norm(np.array([px, py]) - target_pos)
                if dist < min_dist:
                    min_dist = dist
                    best_t = t_sample
            
            DURATION = max(0.01, best_t)

        V_SCALE = 4.0  # Visual scaling for velocity vectors

        time_tracker = ValueTracker(0)

        def get_curr_theta():
            return THETA_START + OMEGA_VAL * time_tracker.get_value()

        # Create axes for decomposition
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 4, 1],
            x_length=6.0,
            y_length=4.8,
            tips=True,
            axis_config={
                "color": DIM,
                "stroke_width": 1.5,
                "include_ticks": False,
            },
        ).shift(RIGHT * 2.2)

        def get_pos():
            """Calculate (x, y) coordinates based on current time (integrated motion)."""
            t = time_tracker.get_value()
            return get_integrated_pos(t)

        def get_robot_center():
            x_c, y_c = get_pos()
            return axes.c2p(x_c, y_c)

        x_label = Text("x", font_size=28, color=DIM).next_to(
            axes.x_axis.get_end(), DOWN, buff=0.2
        )
        y_label = Text("y", font_size=28, color=DIM).next_to(
            axes.y_axis.get_end(), LEFT, buff=0.2
        )

        # Beginner Aids: Grid
        grid = VGroup()
        if show_grid:
            grid = NumberPlane(
                x_range=[0, 5, 1],
                y_range=[0, 4, 1],
                x_length=6.0,
                y_length=4.8,
                axis_config={"stroke_opacity": 0},
                background_line_style={
                    "stroke_color": DIM,
                    "stroke_width": 1,
                    "stroke_opacity": 0.2,
                }
            ).shift(RIGHT * 2.2)

        robot = always_redraw(lambda: make_robot(get_curr_theta(), get_robot_center()))

        # Velocity vector and components (attached to robot)
        velocity = always_redraw(
            lambda: Arrow(
                get_robot_center(),
                get_robot_center()
                + V_SCALE * get_curr_v()
                * np.array([np.cos(get_curr_theta()), np.sin(get_curr_theta()), 0]),
                buff=0,
                color=PRIMARY,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.12,
            )
        )

        x_component = always_redraw(
            lambda: Arrow(
                get_robot_center(),
                get_robot_center() + RIGHT * V_SCALE * get_curr_v() * np.cos(get_curr_theta()),
                buff=0,
                color=X_COLOR,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.14,
            )
        )

        y_component = always_redraw(
            lambda: Arrow(
                get_robot_center() + RIGHT * V_SCALE * get_curr_v() * np.cos(get_curr_theta()),
                get_robot_center()
                + V_SCALE * get_curr_v()
                * np.array([np.cos(get_curr_theta()), np.sin(get_curr_theta()), 0]),
                buff=0,
                color=Y_COLOR,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.14,
            )
        )

        # Projection lines (Redundant removed, x_path and y_path kept)
        x_path_line = always_redraw(
            lambda: DashedLine(
                get_robot_center(),
                axes.c2p(get_pos()[0], 0),
                color=DIM,
                stroke_width=1,
            )
        )
        y_path_line = always_redraw(
            lambda: DashedLine(
                get_robot_center(),
                axes.c2p(0, get_pos()[1]),
                color=DIM,
                stroke_width=1,
            )
        )

        # Beginner Aids: Shaded Triangle
        shaded_triangle = VGroup()
        if show_triangle:
            shaded_triangle = always_redraw(
                lambda: Polygon(
                    get_robot_center(),
                    get_robot_center() + RIGHT * V_SCALE * get_curr_v() * np.cos(get_curr_theta()),
                    get_robot_center() + V_SCALE * get_curr_v() * np.array([np.cos(get_curr_theta()), np.sin(get_curr_theta()), 0]),
                    fill_color=DIM,
                    fill_opacity=0.15,
                    stroke_width=0,
                )
            )

        # Beginner Aids: Radar Circle
        radar_circle = VGroup()
        if show_radar:
            radar_circle = always_redraw(
                lambda: DashedVMobject(
                    Circle(
                        radius=max(0.01, V_SCALE * get_curr_v()),
                        color=DIM,
                        stroke_width=1,
                    ).move_to(get_robot_center()),
                    num_dashes=30,
                    dashed_ratio=0.5,
                ).set_opacity(0.3)
            )

        angle_arc = always_redraw(
            lambda: Arc(
                radius=0.7,
                start_angle=0,
                angle=get_curr_theta(),
                arc_center=get_robot_center(),
                color=DIM,
                stroke_width=2,
            )
        )

        theta_label = always_redraw(
            lambda: Text("θ", font_size=28, color=DIM).move_to(
                get_robot_center()
                + 1.1
                * np.array(
                    [
                        np.cos(get_curr_theta() / 2),
                        np.sin(get_curr_theta() / 2),
                        0,
                    ]
                )
            )
        )

        vx_label = always_redraw(
            lambda: Text("vₓ", font_size=28, color=X_COLOR).move_to(
                get_robot_center() 
                + RIGHT * (V_SCALE * get_curr_v() * np.cos(get_curr_theta()) / 2)
                + (UP if get_curr_v() * np.sin(get_curr_theta()) < -1e-4 else DOWN) * 0.35
            )
        )

        vy_label = always_redraw(
            lambda: Text("vᵧ", font_size=28, color=Y_COLOR).move_to(
                get_robot_center()
                + RIGHT * (V_SCALE * get_curr_v() * np.cos(get_curr_theta()))
                + UP * (V_SCALE * get_curr_v() * np.sin(get_curr_theta()) / 2)
                + (RIGHT if get_curr_v() * np.cos(get_curr_theta()) >= -1e-4 else LEFT) * 0.4
            )
        )

        velocity_label = always_redraw(
            lambda: Text("v", font_size=30, color=PRIMARY).move_to(
                get_robot_center()
                + (V_SCALE * get_curr_v() + 0.4)
                * np.array(
                    [
                        np.cos(get_curr_theta()),
                        np.sin(get_curr_theta()),
                        0,
                    ]
                )
            )
        )

        # Side Panel - Grouped Data Readout
        show_all = not display_selection or "all" in display_selection
        def is_sel(kw): return show_all or kw in display_selection

        # Base value trackers (DecimalNumbers with updaters)
        v_val_m = DecimalNumber(V_START, num_decimal_places=2, font_size=24, mob_class=Text)
        if abs(V_END - V_START) > 1e-6:
            v_val_m.add_updater(lambda d: d.set_value(get_curr_v()))
            
        omega_val_m = DecimalNumber(OMEGA_DEG, num_decimal_places=2, font_size=24, mob_class=Text)
        # Note: OMEGA_DEG is constant in current logic
        
        x_val_m = DecimalNumber(0.00, num_decimal_places=2, font_size=24, mob_class=Text)
        x_val_m.add_updater(lambda d: d.set_value(get_pos()[0]))
        
        y_val_m = DecimalNumber(0.00, num_decimal_places=2, font_size=24, mob_class=Text)
        y_val_m.add_updater(lambda d: d.set_value(get_pos()[1]))
        
        theta_val_m = DecimalNumber(get_curr_theta() / DEGREES, num_decimal_places=1, font_size=24, mob_class=Text)
        theta_val_m.add_updater(lambda d: d.set_value(get_curr_theta() / DEGREES))
        
        vx_val_m = DecimalNumber(get_curr_v() * np.cos(get_curr_theta()), num_decimal_places=2, font_size=24, color=X_COLOR, mob_class=Text)
        vx_val_m.add_updater(lambda d: d.set_value(get_curr_v() * np.cos(get_curr_theta())))
        
        vy_val_m = DecimalNumber(get_curr_v() * np.sin(get_curr_theta()), num_decimal_places=2, font_size=24, color=Y_COLOR, mob_class=Text)
        vy_val_m.add_updater(lambda d: d.set_value(get_curr_v() * np.sin(get_curr_theta())))

        def get_panel_group():
            items = []
            
            # v
            if is_sel("v"):
                items.append(VGroup(Text("v =", font_size=24), v_val_m).arrange(RIGHT, buff=0.15))
            
            # omega
            if is_sel("omega") or is_sel("ω") or is_sel("w"):
                items.append(VGroup(Text("ω =", font_size=24), omega_val_m, Text("°/s", font_size=24)).arrange(RIGHT, buff=0.1))
                
            # x
            if is_sel("x"):
                items.append(VGroup(Text("x =", font_size=24), x_val_m).arrange(RIGHT, buff=0.15))
                
            # y
            if is_sel("y"):
                items.append(VGroup(Text("y =", font_size=24), y_val_m).arrange(RIGHT, buff=0.15))
                
            # theta
            if is_sel("theta") or is_sel("θ") or is_sel("t"):
                th_main = VGroup(Text("θ =", font_size=24), theta_val_m, Text("°", font_size=24)).arrange(RIGHT, buff=0.1)
                if show_subtitles:
                    items.append(VGroup(th_main, Text("(Facing Direction)", font_size=16, color=DIM)).arrange(DOWN, aligned_edge=LEFT, buff=0.1))
                else:
                    items.append(th_main)
                    
            # vx
            if is_sel("vx"):
                vx_main = VGroup(Text("vₓ =", font_size=24, color=X_COLOR), vx_val_m).arrange(RIGHT, buff=0.15)
                if show_subtitles:
                    sub_text = "(Speed pushing Right)" if get_curr_v() * np.cos(get_curr_theta()) >= -1e-4 else "(Speed pushing Left)"
                    items.append(VGroup(vx_main, Text(sub_text, font_size=16, color=DIM)).arrange(DOWN, aligned_edge=LEFT, buff=0.1))
                else:
                    items.append(vx_main)
                    
            # vy
            if is_sel("vy"):
                vy_main = VGroup(Text("vᵧ =", font_size=24, color=Y_COLOR), vy_val_m).arrange(RIGHT, buff=0.15)
                if show_subtitles:
                    sub_text = "(Speed pushing Forward)" if get_curr_v() * np.sin(get_curr_theta()) >= -1e-4 else "(Speed pushing Backward)"
                    items.append(VGroup(vy_main, Text(sub_text, font_size=16, color=DIM)).arrange(DOWN, aligned_edge=LEFT, buff=0.1))
                else:
                    items.append(vy_main)

            if not items:
                return VGroup()
            return VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=0.35).to_edge(LEFT, buff=0.8)

        panel = always_redraw(get_panel_group)


        dynamic_objects = VGroup(
            shaded_triangle,
            radar_circle,
            x_path_line,
            y_path_line,
            x_component,
            y_component,
            velocity,
            robot,
            angle_arc,
            theta_label,
            vx_label,
            vy_label,
            velocity_label,
            panel,
        )

        # 1 second reveal + 6 second rotation + 1 second hold = 8 seconds.
        self.play(
            Create(grid) if show_grid else Wait(0),
            Create(axes),
            Write(x_label),
            Write(y_label),
            FadeIn(dynamic_objects),
            run_time=1,
        )
        self.play(
            time_tracker.animate.set_value(DURATION),
            run_time=DURATION,
            rate_func=linear,
        )
        self.wait(1)

