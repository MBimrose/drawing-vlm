from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
wall_thickness = 5.0
rib_width = 20.0
rib_height = 30.0
rib_offset = 10.0
hole_diameter = 8.0
chamfer_size = 1.0

base = Box(outer_width, outer_height, length)
rib = Pos(outer_width/2 - rib_offset - rib_width/2, 0, 0) * Box(rib_width, rib_height, length)
solid_body = base + rib

hole = Cylinder(hole_diameter/2, length)
solid_body = solid_body - hole

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "ribbed_block_with_hole"
export_step(part, "output.step")