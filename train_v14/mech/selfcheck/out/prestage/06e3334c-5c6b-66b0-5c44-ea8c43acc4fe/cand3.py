from build123d import *
import math

side_length = 60.0
plate_thickness = 10.0
rib_height = 3.0
rib_offset = 5.0
central_hole_diameter = 12.0
chamfer_distance = 1.0
fillet_radius = 2.0

tri_height = side_length * math.sqrt(3) / 2.0
scale_factor = (tri_height + rib_offset) / tri_height
outer_side = side_length * scale_factor
outer_height = tri_height + rib_offset

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(outer_side, 3)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

with BuildPart() as rib_p:
    with BuildSketch() as rs:
        RegularPolygon(side_length, 3)
    extrude(amount=rib_height)

rib_body = Pos(0, 0, plate_thickness) * rib_p.part
rib_body = fillet(rib_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body + rib_body
solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness + rib_height + 10)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")