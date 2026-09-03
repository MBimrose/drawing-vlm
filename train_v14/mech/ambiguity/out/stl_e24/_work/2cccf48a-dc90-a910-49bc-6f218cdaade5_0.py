from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
tab_width = 20.0
tab_height = 10.0
slot_width = 30.0
slot_height = 12.0
hole_diameter = 5.5
hole_pattern_radius = 20.0
chamfer_size = 0.8

base = Box(plate_width, plate_height, plate_thickness)
tab = Pos(0, -(plate_height/2 + tab_height/2), 0) * Box(tab_width, tab_height, plate_thickness)
solid_body = base + tab

solid_body = solid_body - Box(slot_width, slot_height, plate_thickness)

for i in range(5):
    angle = math.radians(i * 360.0 / 5)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")