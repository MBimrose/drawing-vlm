from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
slot_width = 20.0
slot_depth = 6.0
hole_diameter = 8.0
hole_offset_x = 15.0
hole_offset_y = 0.0
gusset_height = 12.0
gusset_base = 15.0
fillet_radius = 1.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

slot_box = Pos(0, bracket_width/2 - slot_depth/2, -bracket_thickness/2) * Box(slot_width, slot_depth, bracket_thickness)
solid_body = solid_body - slot_box

hole_cyl = Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)
solid_body = solid_body - hole_cyl

with BuildPart() as g:
    with BuildSketch(Plane.XZ.offset(-bracket_width/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-gusset_base/2, 0), (gusset_base/2, 0))
            l2 = Line(l1@1, (0, gusset_height))
            l3 = Line(l2@1, (-gusset_base/2, 0))
        make_face()
    extrude(amount=bracket_thickness)
gusset_body = g.part

solid_body = solid_body + gusset_body

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")