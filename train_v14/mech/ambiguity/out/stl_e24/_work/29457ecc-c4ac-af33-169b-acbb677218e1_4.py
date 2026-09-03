from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
wall_thickness = 2.0
pocket_depth = block_thickness - wall_thickness
boss_diameter = 20.0
boss_height = 8.0
hole_diameter = 4.0
hole_offset = 20.0
fillet_radius = 1.5
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_thickness)

pocket = Pos(0, 0, block_thickness/2 - pocket_depth/2) * Box(block_length - 2*wall_thickness, block_width - 2*wall_thickness, pocket_depth)
solid_body = solid_body - pocket

boss = Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (hole_offset, -hole_offset), (-hole_offset, -hole_offset)]:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness + boss_height + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "block_with_pocket_boss_holes"
export_step(part, "output.step")