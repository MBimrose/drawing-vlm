from build123d import *

rod_length = 80.0
rod_diameter = 20.0
rod_radius = rod_diameter / 2.0
wall_thickness = 2.0
inner_radius = rod_radius - wall_thickness
pocket_width = 12.0
pocket_depth = 6.0
pocket_length = 10.0
pocket_center_z = 30.0
chamfer_size = 1.0

solid_body = Cylinder(rod_radius, rod_length)
solid_body = solid_body - Cylinder(inner_radius * 0.8, rod_length)

pocket = Pos(0, rod_radius - pocket_depth / 2, pocket_center_z) * Box(pocket_width, pocket_depth, pocket_length)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "rod_with_pocket"
export_step(part, "output.step")