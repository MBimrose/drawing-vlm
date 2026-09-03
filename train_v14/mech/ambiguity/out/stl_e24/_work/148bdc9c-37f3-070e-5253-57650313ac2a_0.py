from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
width = 20.0
tab_width = 20.0
tab_height = 10.0
pocket_width = 40.0
pocket_length = 30.0
pocket_depth = 5.0
mount_hole_diameter = 8.0
mount_hole_spacing = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=width)

solid_body = p.part

tab = Pos(0, outer_radius, width / 2) * Box(tab_width, tab_height, width)
solid_body = solid_body + tab

solid_body = solid_body - Pos(0, 0, width / 2) * Cylinder(inner_radius, width)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, width / 2) * Cylinder(mount_hole_diameter / 2, width)

pocket = Pos(0, 0, width - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "ring_with_tab"
export_step(part, "output.step")