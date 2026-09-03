from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
t_slot_stem_width = 6.0
t_slot_stem_depth = 20.0
t_slot_top_width = 30.0
t_slot_top_depth = 6.0
gusset_height = 30.0
gusset_width = 12.0
hole_diameter = 4.0
hole_spacing = 60.0

result = Box(bracket_length, bracket_width, bracket_thickness)

stem = Pos(0, 0, 0) * Box(t_slot_stem_width, t_slot_stem_depth, bracket_thickness)
top_bar = Pos(0, t_slot_stem_depth/2 + t_slot_top_depth/2, 0) * Box(t_slot_top_width, t_slot_top_depth, bracket_thickness)
result = result - (stem + top_bar)

with BuildPart() as lg:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((-bracket_length/2, -gusset_height/2), (-bracket_length/2, gusset_height/2), (-bracket_length/2 - gusset_width, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)
result = result + lg.part

with BuildPart() as rg:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((bracket_length/2, -gusset_height/2), (bracket_length/2, gusset_height/2), (bracket_length/2 + gusset_width, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)
result = result + rg.part

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness)

part = result
part.name = "bracket_with_t_slot_and_gussets"
export_step(part, "output.step")