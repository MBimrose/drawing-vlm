from build123d import *

rod_length = 80.0
rod_diameter = 20.0
rod_radius = rod_diameter / 2.0
hole_diameter = 8.0
pocket_width = 12.0
pocket_height = 10.0
pocket_depth = 6.0
pocket_offset_from_top = 20.0
chamfer_size = 1.0

solid_body = Cylinder(rod_radius, rod_length)
solid_body = solid_body - Cylinder(hole_diameter / 2, rod_length)

pocket_z = rod_length / 2 - pocket_offset_from_top - pocket_height / 2
pocket_box = Pos(0, rod_radius - pocket_depth / 2, pocket_z) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "rod_with_pocket"
export_step(part, "output.step")