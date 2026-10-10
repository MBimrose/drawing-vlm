from build123d import *
import math

base_width = 80.0
base_length = 80.0
base_thickness = 15.0
cyl_radius = 25.0
cyl_height = 60.0
fillet_radius = 3.0
hole_diameter = 7.0
hole_count = 8
hole_circle_radius = 35.0
slot_width = 10.0
slot_depth = 20.0
slot_offset = 30.0

base = Box(base_width, base_length, base_thickness)
cyl = Pos(0, 0, base_thickness) * Cylinder(cyl_radius, cyl_height)
solid_body = base + cyl
solid_body = fillet(solid_body.edges(), fillet_radius)

total_height = base_thickness + cyl_height
solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(cyl_radius * 0.6, total_height + 20)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(hole_diameter/2, total_height + 20)

slot = Pos(slot_offset, 0, total_height - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "base_with_cylinder_and_holes"
export_step(part, "output.step")