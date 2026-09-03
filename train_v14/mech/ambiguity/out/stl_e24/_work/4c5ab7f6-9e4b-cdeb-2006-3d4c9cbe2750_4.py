from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
slot_width = 8.0
slot_height = 20.0
chamfer_distance = 0.5

base = Box(outer_width, outer_depth, outer_height)
inner = Box(outer_width - 2 * wall_thickness, outer_depth - 2 * wall_thickness, outer_height - wall_thickness)
inner = Pos(0, 0, wall_thickness / 2) * inner
solid_body = base - inner

slot = Box(slot_width, wall_thickness + 0.2, slot_height)
solid_body = solid_body - Pos(outer_width / 2 - wall_thickness / 2, 0, 0) * slot
solid_body = solid_body - Pos(-outer_width / 2 + wall_thickness / 2, 0, 0) * slot
solid_body = solid_body - Pos(0, outer_depth / 2 - wall_thickness / 2, 0) * Rot(0, 0, 90) * slot
solid_body = solid_body - Pos(0, -outer_depth / 2 + wall_thickness / 2, 0) * Rot(0, 0, 90) * slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")