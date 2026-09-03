from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
edge_chamfer = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 12.0
pocket_wall_thickness = 2.0
hole_diameter = 2.0
hole_spacing_x = 6.0
hole_spacing_y = 6.0
hole_margin = 8.0
rib_thickness = 4.0
rib_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, corner_fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

rib = Pos(0, 0, block_height - rib_height/2) * Box(rib_thickness, block_width - 2*hole_margin, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

x_start = -block_length/2 + hole_margin
x_end = block_length/2 - hole_margin
y_start = -block_width/2 + hole_margin
y_end = block_width/2 - hole_margin

x_vals = []
cur = x_start
while cur <= x_end:
    x_vals.append(cur)
    cur += hole_spacing_x

y_vals = []
cur = y_start
while cur <= y_end:
    y_vals.append(cur)
    cur += hole_spacing_y

for x in x_vals:
    for y in y_vals:
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_pocket_and_holes"
export_step(part, "output.step")