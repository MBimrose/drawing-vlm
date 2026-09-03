from build123d import *
import math

outer_diameter = 80.0
plate_thickness = 10.0
pocket_diameter = 40.0
pocket_depth = 5.0
hole_diameter = 6.0
hole_depth = 6.0
hole_circle_radius = 30.0
fillet_radius = 2.0

solid_body = Cylinder(outer_diameter/2, plate_thickness)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

for i in range(6):
    angle = math.radians(i * 360.0 / 6)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "washer_with_pocket_and_holes"
export_step(part, "output.step")