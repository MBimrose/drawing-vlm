from build123d import *

vertical_height = 80.0
horizontal_length = 70.0
thickness = 10.0
bracket_thickness = 8.0
gusset_width = 12.0
gusset_height = 12.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_end = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_height), (thickness, vertical_height),
                     (thickness, thickness), (horizontal_length, thickness),
                     (horizontal_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)
base = p.part

with BuildPart() as g:
    with BuildSketch() as sk2:
        with BuildLine() as bl2:
            Polyline((0,0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
gusset = g.part

result = base + gusset

hole_positions = [
    (hole_offset_from_end, thickness / 2),
    (hole_offset_from_end + hole_spacing, thickness / 2),
    (hole_offset_from_end + 2 * hole_spacing, thickness / 2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, bracket_thickness) * Cylinder(hole_diameter/2, bracket_thickness)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")