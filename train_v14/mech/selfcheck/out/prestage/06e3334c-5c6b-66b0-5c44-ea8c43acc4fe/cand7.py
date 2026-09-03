from build123d import *
import math

plate_side = 80.0
plate_thickness = 10.0
rib_height = 3.0
rib_thickness = 5.0
central_hole_diameter = 12.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(plate_side / math.sqrt(3), 3)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, plate_thickness * 2)

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as rs:
        RegularPolygon((plate_side + 2 * rib_thickness) / math.sqrt(3), 3)
    extrude(amount=rib_height)

solid_body = solid_body + rib_p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")