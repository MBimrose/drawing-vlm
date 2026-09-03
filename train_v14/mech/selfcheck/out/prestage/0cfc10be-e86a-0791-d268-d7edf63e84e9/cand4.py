from build123d import *

hub_radius = 30.0
hub_length = 20.0
arm_length = 40.0
arm_width = 8.0
arm_height = 25.0
central_hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 8.0
chamfer_size = 1.0

hub = Cylinder(hub_radius, hub_length)
arm = Pos(arm_width/2, arm_height/2, hub_length/2 + arm_length/2) * Box(arm_width, arm_height, arm_length)
result = hub + arm

result = result - Cylinder(central_hole_diameter/2, 100)
result = result - Pos(0, 0, hub_length/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

pocket = Pos(arm_width/2 + arm_length - pocket_depth/2, arm_height/2, hub_length/2 + arm_length/2) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

part = result
part.name = "hub_with_arm"
export_step(part, "output.step")