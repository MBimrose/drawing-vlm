from build123d import *

outer_diameter = 30.0
wall_thickness = 2.0
inner_diameter = outer_diameter - 2 * wall_thickness
stem_length = 80.0
branch_length = 50.0
rib_thickness = 2.8
rib_height = 20.0
rib_start = 30.0
rib_end = rib_start + rib_height
pocket_width = 20.0
pocket_depth = 15.0
pocket_height = 5.0
hole_diameter = 5.0
hole_spacing = branch_length / 2.0

outer_stem = Cylinder(outer_diameter / 2.0, stem_length)
outer_branch = Pos(0, 0, stem_length / 2.0) * Rot(0, 90, 0) * Cylinder(outer_diameter / 2.0, branch_length)
outer_tee = outer_stem + outer_branch

inner_stem = Cylinder(inner_diameter / 2.0, stem_length)
inner_branch = Pos(0, 0, stem_length / 2.0) * Rot(0, 90, 0) * Cylinder(inner_diameter / 2.0, branch_length)
inner_tee = inner_stem + inner_branch

tee_hollow = outer_tee - inner_tee

rib = Pos(0, 0, rib_start - stem_length / 2.0) * Cylinder((outer_diameter / 2.0) + rib_thickness, rib_height)
tee_with_rib = tee_hollow + rib

pocket = Pos(0, 0, stem_length / 2.0 + outer_diameter / 2.0 - pocket_height / 2.0) * Box(pocket_width, pocket_depth, pocket_height)
tee_pocketed = tee_with_rib - pocket

hole1 = Pos(-hole_spacing / 2.0, 0, stem_length / 2.0 + outer_diameter / 2.0) * Cylinder(hole_diameter / 2.0, 100)
hole2 = Pos(hole_spacing / 2.0, 0, stem_length / 2.0 + outer_diameter / 2.0) * Cylinder(hole_diameter / 2.0, 100)
part = tee_pocketed - hole1 - hole2

part.name = "Tee_Fitting"
export_step(part, "output.step")