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
hole_circle_radius = 20.0
chamfer_distance = 0.8

base_plate = Box(plate_width, plate_height, plate_thickness)
tab = Pos(0, -(plate_height/2 + tab_height/2), 0) * Box(tab_width, tab_height, plate_thickness)
result = base_plate + tab

slot = Box(slot_width, slot_height, plate_thickness + 0.01)
result = result - slot

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness + 0.01)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")