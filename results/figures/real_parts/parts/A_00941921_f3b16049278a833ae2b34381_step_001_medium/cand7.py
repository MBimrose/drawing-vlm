from build123d import *
import math

ring_outer_diameter = 60.0
ring_inner_diameter = 40.0
ring_thickness = 5.0
tab_width = 10.0
tab_length = 15.0
hole_diameter = 5.0
hole_clearance = 0.2
chamfer_distance = 1.0
chamfer_angle_deg = 20.0

ring_outer_radius = ring_outer_diameter / 2.0
ring_inner_radius = ring_inner_diameter / 2.0
hole_radius = (hole_diameter + hole_clearance) / 2.0
chamfer_distance2 = chamfer_distance * math.tan(math.radians(chamfer_angle_deg))

ring = Cylinder(ring_outer_radius, ring_thickness) - Cylinder(ring_inner_radius, ring_thickness)

tab = Pos(ring_outer_radius, 0, 0) * Box(tab_length, tab_width, ring_thickness)
tabs = tab
for angle in [90, 180, 270]:
    tabs = tabs + Rot(0, 0, angle) * tab

combined = ring + tabs

hole_center_radius = ring_outer_radius + tab_length / 2.0
hole_positions = [
    (hole_center_radius, 0),
    (0, hole_center_radius),
    (-hole_center_radius, 0),
    (0, -hole_center_radius),
]

for x, y in hole_positions:
    combined = combined - Pos(x, y, 0) * Cylinder(hole_radius, ring_thickness)

combined = chamfer(combined.edges().filter_by(Axis.Z), chamfer_distance, chamfer_distance2)

part = combined
part.name = "ring_with_tabs"
export_step(part, "output.step")