from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
rib_thickness = 4.0
rib_height = 6.0
rib_count = 6
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_radius = (outer_diameter / 2) - wall_thickness - 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)
solid_body = fillet(solid_body.edges(), fillet_radius)

for i in range(4):
    angle = math.radians(i * 90)
    px = hole_offset_radius * math.cos(angle)
    py = hole_offset_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
    solid_body = solid_body + rib

part = solid_body
part.name = "ribbed_housing"
export_step(part, "output.step")