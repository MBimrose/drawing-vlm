from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
outer_fillet_radius = 1.0
notch_width = 20.0
notch_depth = 6.0
notch_corner_radius = 1.0
hole_diameter = 8.0
hole_offset_x = 15.0
rib_width = 10.0
rib_height = 6.0
rib_offset_from_center = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), outer_fillet_radius)

notch_cut = Pos(0, bracket_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, bracket_thickness)
solid_body = solid_body - notch_cut

notch_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(notch_edges, notch_corner_radius)

hole = Pos(hole_offset_x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)
solid_body = solid_body - hole

with BuildPart() as rib_p:
    with BuildSketch(Plane.XZ.offset(-bracket_width/2)) as sk:
        Polygon((0, -bracket_thickness/2), (rib_width, -bracket_thickness/2), (rib_width/2, -bracket_thickness/2 + rib_height))
    extrude(amount=-bracket_thickness)

solid_body = solid_body + rib_p.part

part = solid_body
part.name = "bracket_with_notch_rib"
export_step(part, OUTPUT_PATH)