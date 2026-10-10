from build123d import *
import math

hub_radius = 15.0
hub_thickness = 8.0
arm_length = 40.0
arm_width = 12.0
arm_tip_radius = 10.0
shell_thickness = 0.7
fillet_radius = 1.0
central_hole_diameter = 20.0
arm_hole_diameter = 6.0
pocket_width = 12.0
pocket_depth = 4.0

hub = Cylinder(hub_radius, hub_thickness)

arm_center_dist = hub_radius + arm_length / 2
arm = Pos(arm_center_dist, 0, 0) * Box(arm_length, arm_width, hub_thickness)
arm_tip = Pos(hub_radius + arm_length, 0, 0) * Cylinder(arm_tip_radius, hub_thickness)
arm = arm + arm_tip

arms = arm
for i in range(1, 3):
    arms = arms + Rot(0, 0, i * 120) * arm

result = hub + arms

result = offset(result, amount=-shell_thickness)
result = fillet(result.edges(), fillet_radius)

result = result - Cylinder(central_hole_diameter / 2, hub_thickness * 2)

for i in range(3):
    angle = math.radians(i * 120)
    px = arm_center_dist * math.cos(angle)
    py = arm_center_dist * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(arm_hole_diameter / 2, hub_thickness * 2)

result = result - Pos(0, 0, hub_thickness - pocket_depth / 2) * Box(pocket_width, pocket_width, pocket_depth)

part = result
part.name = "hub_with_arms"
export_step(part, "output.step")