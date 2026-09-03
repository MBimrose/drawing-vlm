from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
wall_thickness = 5.0
rib_width = 6.0
rib_height = 10.0
rib_spacing = 12.0
hole_diameter = 8.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 20.0
chamfer_size = 1.0

solid_body = Box(outer_width, outer_height, length)

rib_count = int((outer_width - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_offset = -outer_width / 2 + wall_thickness + rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_offset, 0, 0) * Box(rib_width, rib_height, length)
    solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter / 2, length)

pocket = Pos(0, 0, length - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ribbed_block_with_pocket"
export_step(part, "output.step")