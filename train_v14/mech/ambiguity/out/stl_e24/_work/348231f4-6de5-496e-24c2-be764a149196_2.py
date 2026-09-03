from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 3.0
rib_height = 2.0
rib_width = 5.0
rib_length = 20.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 1.5
hole_diameter = 2.0
counterbore_diameter = 4.0
counterbore_depth = 2.0
chamfer_size = 0.5

base = Box(leaf_length, leaf_width, leaf_thickness)
rib1 = Box(rib_length, rib_width, rib_height)
rib2 = Box(rib_width, rib_length, rib_height)
result = base + rib1 + rib2

pocket = Pos(0, 0, leaf_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

cbore = Pos(0, 0, leaf_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, 0, 0) * Cylinder(hole_diameter/2, leaf_thickness + 10)
result = result - cbore - shaft

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "leaf_with_ribs_pocket_and_counterbore"
export_step(part, "output.step")