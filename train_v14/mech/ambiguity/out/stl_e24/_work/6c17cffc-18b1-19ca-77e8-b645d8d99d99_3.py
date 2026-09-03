from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_width = 10.0
rib_height = 4.0
rib_thickness = 2.0
recess_diameter = 30.0
recess_depth = 2.0
hole_diameter = 5.5
hole_pattern_radius = 25.0
hole_count = 6
fillet_radius = 1.0
cross_groove_width = 6.0
cross_groove_length = 20.0
cross_groove_depth = 1.5

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, 0, plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

recess = Pos(0, 0, -plate_thickness/2 + recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)
solid_body = solid_body - recess

groove1 = Pos(0, 0, -plate_thickness/2 + cross_groove_depth/2) * Box(cross_groove_length, cross_groove_width, cross_groove_depth)
solid_body = solid_body - groove1

groove2 = Pos(0, 0, -plate_thickness/2 + cross_groove_depth/2) * Box(cross_groove_width, cross_groove_length, cross_groove_depth)
solid_body = solid_body - groove2

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_rib_recess_grooves_holes"
export_step(part, "output.step")