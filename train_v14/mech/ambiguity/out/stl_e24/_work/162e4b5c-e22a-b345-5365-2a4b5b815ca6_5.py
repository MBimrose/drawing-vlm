from build123d import *

lever_length = 80.0
lever_width = 30.0
lever_thickness = 10.0
split_gap = 0.5
boss_diameter = 20.0
boss_depth = 8.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 20.0
chamfer_distance = 1.0

base = Pos(0, 0, lever_thickness/2) * Box(lever_length, lever_width, lever_thickness)
boss = Pos(lever_length/2 - boss_diameter/2, 0, lever_thickness/2) * Cylinder(boss_diameter/2, lever_thickness)
solid_body = base + boss

hole_positions = [
    (-lever_length/2 + hole_offset, -hole_spacing/2),
    (-lever_length/2 + hole_offset, hole_spacing/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness * 2)

solid_body = solid_body - Pos(lever_length/2 - boss_diameter/2, 0, boss_depth/2) * Cylinder(boss_diameter/2, boss_depth)

solid_body = solid_body - Pos(0, 0, (lever_thickness - split_gap)/2) * Box(split_gap, lever_width, lever_thickness - split_gap)

left_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = chamfer(left_edges, chamfer_distance)

part = solid_body
part.name = "lever"
export_step(part, "output.step")