# Reference model of test_part.pdf (Pilot Metals 12-001795-00), hand-built from the 3 sheets, in mm.
# Thickness is not dimensioned: measured from the side view (87.5 px at 87.5 px/in) = 1.00 in.
from build123d import *
IN = 25.4
side = 8.780 * IN            # 223.01
thick = 1.000 * IN           # 25.4
corner_r = 0.10 * IN         # R.10 break edge (plan corners)
clear_d, clear_sq = 0.257 * IN, 7.000 * IN     # 4x through, on 177.8 square
tap_d, tap_sq = 6.8, 93.35                     # 4x M8x1.25 tap thru (tap drill 6.8), on 93.35 square
dowel_d, dowel_depth, dowel_dx, dowel_y = 8.5, 6.0, 120.0, 101.5 - side / 2   # 2x, 101.5 up from bottom edge
with BuildPart() as p:
    with BuildSketch():
        RectangleRounded(side, side, corner_r)
    extrude(amount=thick)
    with Locations((0, 0, thick)):
        with GridLocations(clear_sq, clear_sq, 2, 2):
            Hole(clear_d / 2)
        with GridLocations(tap_sq, tap_sq, 2, 2):
            Hole(tap_d / 2)
        with Locations((-dowel_dx / 2, dowel_y), (dowel_dx / 2, dowel_y)):
            Hole(dowel_d / 2, depth=dowel_depth)
part = p.part
export_step(part, "output.step")
