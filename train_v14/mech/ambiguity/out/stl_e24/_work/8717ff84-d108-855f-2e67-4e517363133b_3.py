from build123d import *

bracket_length = 60.0
bracket_width = 55.0
bracket_thickness = 10.0
gusset_height = 40.0
gusset_extension = 20.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset_from_edge = 10.0
slot_length = 50.0
slot_width = 6.0
slot_offset_from_center = 15.0
fillet_radius = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            l1 = Line((0, -gusset_height/2), (0, gusset_height/2))
            l2 = Line(l1@1, (gusset_extension, 0))
            l3 = Line(l2@1, (0, -gusset_height/2))
        make_face()
    extrude(amount=bracket_thickness)
gusset = Pos(bracket_length/2, 0, -bracket_thickness/2) * gp.part

result = base + gusset

hole_x = -bracket_length/2 + hole_offset_from_edge
for y in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(hole_x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

result = result - Pos(0, slot_offset_from_center, 0) * Box(slot_length, slot_width, bracket_thickness * 2)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_gusset"
export_step(part, "output.step")