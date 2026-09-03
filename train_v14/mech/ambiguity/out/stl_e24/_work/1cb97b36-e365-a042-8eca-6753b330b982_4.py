from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
slot_stem_width = 6.0
slot_stem_height = 20.0
slot_top_width = 30.0
slot_top_thickness = 6.0
hole_diameter = 4.0
hole_spacing = 30.0
gusset_height = 12.0
gusset_thickness = 6.0

base = Box(bracket_length, bracket_width, bracket_thickness)

stem = Box(slot_stem_width, slot_stem_height, bracket_thickness)
top = Pos(0, slot_stem_height/2 + slot_top_thickness/2, 0) * Box(slot_top_width, slot_top_thickness, bracket_thickness)
slot = stem + top
base = base - slot

hole_positions = [(-bracket_length/2 + hole_spacing/2, 0), (bracket_length/2 - hole_spacing/2, 0)]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

with BuildPart() as gp1:
    with BuildSketch(Plane.XY.offset(-bracket_thickness/2)) as sk1:
        with BuildLine() as bl1:
            Polyline((-bracket_length/2, -bracket_width/2), (-bracket_length/2 - gusset_height, 0), (-bracket_length/2, bracket_width/2), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset1 = gp1.part

with BuildPart() as gp2:
    with BuildSketch(Plane.XY.offset(-bracket_thickness/2)) as sk2:
        with BuildLine() as bl2:
            Polyline((bracket_length/2, -bracket_width/2), (bracket_length/2 + gusset_height, 0), (bracket_length/2, bracket_width/2), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset2 = gp2.part

part = base + gusset1 + gusset2
part.name = "bracket_with_t_slot_and_gussets"
export_step(part, "output.step")