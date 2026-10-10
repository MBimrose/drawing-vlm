from build123d import *

base_side = 80.0
base_thickness = 10.0
rib_height = 3.0
rib_offset = 3.0
hole_diameter = 12.0
fillet_radius = 2.0

inner_side = base_side - 2 * rib_offset

with BuildPart() as p:
    with BuildSketch() as s1:
        RegularPolygon(base_side / 2, 3)
    extrude(amount=base_thickness)
    with BuildSketch(Plane.XY.offset(base_thickness)) as s2:
        RegularPolygon(inner_side / 2, 3)
    extrude(amount=rib_height)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter / 2, base_thickness + rib_height + 10)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "triangular_base_with_rib"
export_step(part, "output.step")