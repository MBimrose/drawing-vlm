from build123d import *
import math

plate_side = 100.0
plate_thickness = 10.0
rib_offset = 5.0
rib_height = 3.0
central_hole_diameter = 12.0
through_hole_diameter = 5.0
through_hole_offset = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(plate_side / math.sqrt(3), 3)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as rs:
        RegularPolygon((plate_side - 2 * rib_offset) / math.sqrt(3), 3)
    extrude(amount=rib_height)

solid_body = solid_body + rib_p.part

solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness + rib_height + 10)

for i in range(3):
    angle = math.radians(i * 120)
    px = through_hole_offset * math.cos(angle)
    py = through_hole_offset * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(through_hole_diameter / 2, plate_thickness + rib_height + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")