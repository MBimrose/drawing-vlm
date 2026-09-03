from build123d import *
import math

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
rib_width = 8.0
rib_height = 4.0
recess_radius = 15.0
recess_depth = 2.0
hole_diameter = 5.5
hole_pattern_radius = 25.0
hole_count = 6
edge_fillet = 1.0

solid = Box(plate_width, plate_depth, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), edge_fillet)

rib1 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_depth - 2*rib_width, rib_height)
rib2 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(plate_width - 2*rib_width, rib_width, rib_height)
solid = solid + rib1 + rib2

recess = Pos(0, 0, -plate_thickness/2 + recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid = solid - recess

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)
    solid = solid - hole

part = solid
part.name = "plate_with_ribs_recess_and_holes"
export_step(part, "output.step")