from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
recess_radius = 15.0
recess_depth = 4.0
hole_diameter = 5.5
hole_circle_radius = 25.0
hole_count = 6
fillet_radius = 1.0
rib_width = 8.0
rib_length = 30.0
rib_depth = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)

solid_body = solid_body - Pos(0, 0, -plate_thickness/2 + recess_depth/2) * Cylinder(recess_radius, recess_depth)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(0, 0, -plate_thickness/2 + rib_depth/2) * Box(rib_width, rib_length, rib_depth)
solid_body = solid_body - Pos(0, 0, -plate_thickness/2 + rib_depth/2) * Box(rib_length, rib_width, rib_depth)

part = solid_body
part.name = "plate_with_recess_holes_and_ribs"
export_step(part, "output.step")