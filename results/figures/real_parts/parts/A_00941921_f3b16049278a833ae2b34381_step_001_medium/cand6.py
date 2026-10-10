from build123d import *

outer_diameter = 60.0
inner_diameter = 40.0
plate_thickness = 5.0
tab_width = 10.0
tab_length = 15.0
hole_diameter = 5.0
chamfer_distance = 2.0
clearance = 0.2

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

base = Cylinder(outer_radius, plate_thickness)
tab = Pos(outer_radius + tab_length / 2.0, 0, 0) * Box(tab_length, tab_width, plate_thickness)
tabs = tab + Rot(0, 0, 90) * tab + Rot(0, 0, 180) * tab + Rot(0, 0, 270) * tab
result = base + tabs

result = result - Cylinder(inner_radius + clearance, plate_thickness)

hole_positions = [
    (outer_radius + tab_length / 2.0, 0),
    (-(outer_radius + tab_length / 2.0), 0),
    (0, outer_radius + tab_length / 2.0),
    (0, -(outer_radius + tab_length / 2.0)),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2.0 + clearance, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_plate_with_tabs"
export_step(part, "output.step")