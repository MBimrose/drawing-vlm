from build123d import *
import math

outer_diameter = 80.0
disc_thickness = 5.0
inner_diameter = 30.0
blind_hole_diameter = 4.0
blind_hole_depth = 3.0
blind_hole_count = 12
blind_hole_radius = 30.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=disc_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_distance)

for i in range(blind_hole_count):
    angle = math.radians(i * 360.0 / blind_hole_count)
    px = blind_hole_radius * math.cos(angle)
    py = blind_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, disc_thickness - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)

part = solid_body
part.name = "washer_with_blind_holes"
export_step(part, "output.step")