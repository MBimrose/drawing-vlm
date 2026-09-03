from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
hole_diameter = 4.0
hole_offset = 10.0
fillet_radius = 1.5
chamfer_distance = 1.0

solid_body = Box(block_length, block_width, block_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

boss = Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

hole_positions = [
    (-block_length/2 + hole_offset, -block_width/2 + hole_offset),
    ( block_length/2 - hole_offset, -block_width/2 + hole_offset),
    (-block_length/2 + hole_offset,  block_width/2 - hole_offset),
    ( block_length/2 - hole_offset,  block_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness + boss_height + 20)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "shelled_block_with_boss"
export_step(part, "output.step")