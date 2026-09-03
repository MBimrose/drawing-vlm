from build123d import *

stem_width = 10.0
stem_height = 30.0
flange_width = 50.0
flange_thickness = 12.0
length = 80.0
pocket_width = 20.0
pocket_depth = 10.0
chamfer_size = 1.0

stem = Pos(0, stem_height/2, length/2) * Box(stem_width, stem_height, length)
flange = Pos(0, stem_height + flange_thickness/2, length/2) * Box(flange_width, flange_thickness, length)
solid_body = stem + flange

pocket = Pos(0, stem_height + flange_thickness - pocket_depth/2, length/2) * Box(pocket_width, pocket_depth, length)
solid_body = solid_body - pocket

z_edges = solid_body.edges().filter_by(Axis.Z)
flange_edges = [e for e in z_edges if e.center().Y > stem_height]
solid_body = chamfer(flange_edges, chamfer_size)

part = solid_body
part.name = "T_profile_with_pocket"
export_step(part, "output.step")