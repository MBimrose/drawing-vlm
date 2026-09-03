from build123d import *
import math

outer_diameter = 80.0
height = 60.0
wall_thickness = 5.0
fillet_radius = 2.0
pocket_radius = 20.0
pocket_depth = 10.0
hole_diameter = 5.0
hole_pattern_radius = 30.0
hole_count = 6
rib_thickness = 4.0
rib_width = 6.0
rib_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2) * Cylinder(hole_diameter/2, height * 2)

rib = Pos(inner_radius - rib_thickness/2.0, 0, 0) * Box(rib_thickness, rib_width, height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")