from build123d import *

outer_width = 50.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
slot_width = 20.0
slot_height = 15.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 10.0
chamfer_size = 1.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

slot = Pos(0, -outer_depth/2 + wall_thickness/2, 0) * Box(slot_width, wall_thickness, slot_height)
base = base - slot

pocket = Pos(0, 0, outer_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
base = base - pocket

bottom_front_edges = base.edges().filter_by(Axis.X).sort_by(Axis.Z)[:1].sort_by(Axis.Y)[:1]
base = chamfer(bottom_front_edges, chamfer_size)

part = base
part.name = "shelled_box_with_slot_pocket"
export_step(part, "output.step")