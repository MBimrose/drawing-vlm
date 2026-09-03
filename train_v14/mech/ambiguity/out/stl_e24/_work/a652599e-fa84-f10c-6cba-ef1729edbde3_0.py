from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_fillet_radius = 5.0
central_hole_diameter = 12.0
clearance_hole_diameter = 4.2
clearance_hole_offset = 15.0
chamfer_distance = 1.0
boss_diameter = 20.0
boss_height = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Y)
solid_body = fillet(vertical_edges, corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, block_height/2) * Cylinder(central_hole_diameter/2, block_height)

for x, y in [(clearance_hole_offset, clearance_hole_offset),
             (-clearance_hole_offset, clearance_hole_offset),
             (-clearance_hole_offset, -clearance_hole_offset),
             (clearance_hole_offset, -clearance_hole_offset)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(clearance_hole_diameter/2, block_height)

boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

top_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "block_with_holes_and_boss"
export_step(part, "output.step")