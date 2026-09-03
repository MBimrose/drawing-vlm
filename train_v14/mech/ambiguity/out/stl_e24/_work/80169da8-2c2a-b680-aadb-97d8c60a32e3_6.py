from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 30.0
rib_width = 8.0
rib_height = 10.0
rib_thickness = 3.0
pocket_width = 40.0
pocket_length = 30.0
pocket_depth = 5.0
screw_hole_diameter = 3.0
screw_hole_count = 4
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

shell = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

rib = Pos(0, outer_radius + rib_thickness / 2.0, -height / 2.0 + rib_height / 2.0) * Box(outer_diameter, rib_thickness, rib_height)
rib = chamfer(rib.edges(), chamfer_size)

result = shell + rib

pocket = Pos(0, 0, height / 2.0 - pocket_depth / 2.0) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

hole_radius = screw_hole_diameter / 2.0
hole_r = outer_radius - wall_thickness / 2.0
for i in range(screw_hole_count):
    angle_deg = i * 360.0 / screw_hole_count
    angle_rad = math.radians(angle_deg)
    px = hole_r * math.cos(angle_rad)
    py = hole_r * math.sin(angle_rad)
    hole = Pos(px, py, 0) * Rot(0, 90, angle_deg) * Cylinder(hole_radius, wall_thickness + 0.2)
    result = result - hole

part = result
part.name = "cylindrical_shell_with_rib"
export_step(part, "output.step")