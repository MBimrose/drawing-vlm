from build123d import *

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
pocket_depth = 3.0
pocket_margin = 5.0
slot_width = 30.0
slot_height = 20.0
slot_chamfer = 1.0
hole_diameter = 3.0
hole_radius = hole_diameter / 2.0
hole_depth = wall_thickness - 0.5

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
inner_height = outer_height - wall_thickness

result = Box(outer_width, outer_depth, outer_height)
result = result - Pos(0, 0, -wall_thickness/2) * Box(inner_width, inner_depth, inner_height)

pocket_w = outer_width - 2 * pocket_margin
pocket_d = outer_depth - 2 * pocket_margin
result = result - Pos(0, 0, outer_height/2 - pocket_depth/2) * Box(pocket_w, pocket_d, pocket_depth)

slot = Box(wall_thickness, slot_width, slot_height)
slot = chamfer(slot.edges().filter_by(Axis.Z), slot_chamfer)
result = result - Pos(-outer_width/2 + wall_thickness/2, 0, 0) * slot

import math
for i in range(4):
    angle = math.radians(i * 360.0 / 4)
    px = (outer_width/2 - wall_thickness - hole_radius) * math.cos(angle)
    py = (outer_width/2 - wall_thickness - hole_radius) * math.sin(angle)
    result = result - Pos(px, py, outer_height/2 - hole_depth/2) * Cylinder(hole_radius, hole_depth)

part = result
part.name = "hollow_box_with_pocket_slot_holes"
export_step(part, "output.step")