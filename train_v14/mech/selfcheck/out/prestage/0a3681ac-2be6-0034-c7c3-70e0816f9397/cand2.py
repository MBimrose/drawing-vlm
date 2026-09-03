from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_base = 10.0
rib_offset_from_center = 5.0
hole_diameter = 8.0
hole_offset_from_end = 15.0
fillet_radius = 1.0
notch_width = 20.0
notch_depth = 6.0
notch_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

notch_box = Pos(0, bracket_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, bracket_thickness)
solid_body = solid_body - notch_box

with BuildPart() as rib_p:
    with BuildSketch(Plane.XZ) as rib_sk:
        with BuildLine() as rib_line:
            Polyline((-rib_base/2, 0), (rib_base/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

rib_solid = Pos(0, bracket_width/2, 0) * rib_p.part
solid_body = solid_body + rib_solid

hole_cyl = Pos(bracket_length/2 - hole_offset_from_end, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)
solid_body = solid_body - hole_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")