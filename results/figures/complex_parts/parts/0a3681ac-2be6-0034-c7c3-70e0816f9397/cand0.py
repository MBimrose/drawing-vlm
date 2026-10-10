from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
gusset_height = 6.0
gusset_base = 12.0
hole_diameter = 8.0
hole_offset = 15.0
slot_length = 20.0
slot_width = 6.0
slot_offset = 10.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-gusset_base/2, 0), (gusset_base/2, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

gusset_body = Pos(0, bracket_width/2, 0) * g.part
solid_body = solid_body + gusset_body

solid_body = solid_body - Pos(hole_offset, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 2)
solid_body = solid_body - Pos(0, slot_offset, bracket_thickness/2) * Box(slot_length, slot_width, bracket_thickness + 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket_with_gusset"
export_step(part, "output.step")