from build123d import *

base_side = 80.0
base_thickness = 10.0
rib_height = 3.0
rib_thickness = 2.0
hole_diameter = 12.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(base_side, 3)
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(base_thickness)) as rs:
        RegularPolygon(base_side + 2 * rib_thickness, 3)
    extrude(amount=rib_height)

solid_body = solid_body + rib_p.part

total_height = base_thickness + rib_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 1)

part = solid_body
part.name = "triangular_base_with_rib"
export_step(part, "output.step")