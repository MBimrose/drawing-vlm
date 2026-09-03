from build123d import *

arm_length = 80
arm_width = 30
arm_thickness = 10
rib_length = 20
rib_width = 10
rib_height = 5
pocket_diameter = 20
pocket_depth = 8
pocket_offset = 10
hole_diameter = 4
hole_spacing = 15
hole_offset = 20
chamfer_size = 1
slot_width = 2
slot_depth = 6
slot_offset = 40

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
rib = Pos(0, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)
result = base + rib

pocket_center_x = arm_length/2 - pocket_offset
pocket = Pos(pocket_center_x, 0, pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
result = result - pocket

hole_center_x = -arm_length/2 + hole_offset
for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(hole_center_x, y, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness + 1)
    result = result - hole

slot_center_x = -arm_length/2 + slot_offset
slot = Pos(slot_center_x, 0, slot_depth/2) * Box(slot_width, arm_width, slot_depth)
result = result - slot

z_edges = result.edges().filter_by(Axis.Z)
min_x_edges = z_edges.sort_by(Axis.X)[:2]
result = chamfer(min_x_edges, chamfer_size)

part = result
part.name = "arm_with_rib_pocket_holes_slot"
export_step(part, "output.step")