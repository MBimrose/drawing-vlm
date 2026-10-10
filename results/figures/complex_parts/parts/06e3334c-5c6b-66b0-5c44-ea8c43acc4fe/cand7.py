from build123d import *
import math

plate_side_length = 80.0
plate_thickness = 10.0
rib_width = 5.0
rib_height = 3.0
central_hole_diameter = 12.0
mount_hole_diameter = 5.0

outer_side_length = plate_side_length + 2 * rib_width
inner_radius = plate_side_length / math.sqrt(3)
outer_radius = outer_side_length / math.sqrt(3)

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(inner_radius, 3)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness * 2)

with BuildPart() as rib_p:
    with BuildSketch() as rs:
        RegularPolygon(outer_radius, 3)
    extrude(amount=rib_height)

rib_solid = rib_p.part
rib_solid = rib_solid - Cylinder(inner_radius, rib_height * 2)
rib_solid = Pos(0, 0, plate_thickness) * rib_solid

solid_body = solid_body + rib_solid

for i in range(3):
    angle = math.radians(i * 120)
    px = inner_radius * math.cos(angle)
    py = inner_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

part = solid_body
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")