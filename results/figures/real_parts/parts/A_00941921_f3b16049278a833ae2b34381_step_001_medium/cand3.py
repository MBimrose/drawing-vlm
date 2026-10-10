from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 40.0
plate_thickness = 5.0
tab_width = 10.0
tab_length = 20.0
mount_hole_diameter = 5.0
clearance = 0.2
chamfer_angle_deg = 20.0
chamfer_distance = plate_thickness * math.tan(math.radians(chamfer_angle_deg))

base = Cylinder(outer_diameter / 2, plate_thickness)
tab = Pos(outer_diameter / 2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
tabs = tab
for i in range(1, 4):
    tabs = tabs + Rot(0, 0, i * 90) * tab

result = base + tabs
result = result - Cylinder((inner_diameter + clearance) / 2, plate_thickness)

hole_radius = (mount_hole_diameter + clearance) / 2
hole_positions = [
    (outer_diameter / 2 + tab_length / 2, 0),
    (-(outer_diameter / 2 + tab_length / 2), 0),
    (0, outer_diameter / 2 + tab_length / 2),
    (0, -(outer_diameter / 2 + tab_length / 2))
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_radius, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_plate_with_tabs"
export_step(part, "output.step")