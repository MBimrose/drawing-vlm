from build123d import *

side_length = 60.0
thickness = 10.0
rib_height = 3.0
rib_offset = 4.0
central_hole_diameter = 12.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(side_length, 3)
    extrude(amount=thickness)

solid_body = p.part

hole = Cylinder(central_hole_diameter / 2, thickness * 2)
solid_body = solid_body - hole

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(thickness)) as rs:
        RegularPolygon(side_length + 2 * rib_offset, 3)
    extrude(amount=rib_height)

rib_solid = rib_p.part
rib_edges = rib_solid.edges().filter_by(Axis.Z)
rib_solid = fillet(rib_edges, fillet_radius)

solid_body = solid_body + rib_solid

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")