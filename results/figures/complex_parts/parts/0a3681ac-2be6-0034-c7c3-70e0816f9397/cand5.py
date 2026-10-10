from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
hole_diameter = 8.0
hole_offset_x = 15.0
hole_offset_y = 0.0
slot_length = 20.0
slot_width = 6.0
slot_offset_x = 0.0
slot_offset_y = 10.0
gusset_base = 12.0
gusset_height = 6.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

# Hole through top face
solid_body = solid_body - Pos(hole_offset_x, hole_offset_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

# Slot cut through
solid_body = solid_body - Pos(slot_offset_x, slot_offset_y, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness)

# Gusset on >Y face
with BuildPart() as g:
    with BuildSketch(Plane.XZ.offset(bracket_width/2)) as sk:
        with BuildLine() as bl:
            Polyline((-gusset_base/2, 0), (gusset_base/2, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = solid_body + g.part

# Fillet all vertical edges
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")