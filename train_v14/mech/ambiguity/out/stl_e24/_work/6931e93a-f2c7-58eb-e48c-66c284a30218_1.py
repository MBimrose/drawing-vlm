from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
corner_fillet_radius = 5.0
chamfer_distance = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_margin = 8.0
rib_thickness = 4.0
rib_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
target_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([target_edge], corner_fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(0, 0, rib_height/2) * Box(block_length - 2*hole_margin, rib_thickness, rib_height)
solid_body = solid_body + rib

x_start = -block_length/2 + hole_margin
x_end = block_length/2 - hole_margin
y_start = -block_width/2 + hole_margin
y_end = block_width/2 - hole_margin

x = x_start
while x <= x_end:
    y = y_start
    while y <= y_end:
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
        solid_body = solid_body - hole
        y += hole_spacing
    x += hole_spacing

part = solid_body
part.name = "block_with_pocket_rib_and_holes"
export_step(part, "output.step")