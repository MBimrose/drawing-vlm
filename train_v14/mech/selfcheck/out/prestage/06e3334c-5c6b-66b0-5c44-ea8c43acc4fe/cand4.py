from build123d import *

triangle_side = 80.0
plate_thickness = 10.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 12.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(triangle_side/2, 3)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter/2, plate_thickness * 2)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

with BuildPart() as p2:
    with BuildSketch() as s2:
        RegularPolygon((triangle_side + 2*rib_width)/2, 3)
    extrude(amount=rib_height)

rib_body = p2.part
rib_body = Pos(0, 0, plate_thickness) * rib_body
rib_vertical_edges = rib_body.edges().filter_by(Axis.Z)
rib_body = chamfer(rib_vertical_edges, chamfer_distance)

part = solid_body + rib_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")