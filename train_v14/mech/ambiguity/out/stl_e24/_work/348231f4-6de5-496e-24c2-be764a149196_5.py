from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 3.0
rib_height = 2.0
rib_width = 5.0
rib_length = 60.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 1.5
pocket_offset_x = -plate_length/2 + pocket_length/2 + 5.0
pocket_offset_y = 0.0
hole_diameter = 2.0
cbore_diameter = 4.0
cbore_depth = 2.0
chamfer_size = 0.3

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = base + rib

pocket = Pos(pocket_offset_x, pocket_offset_y, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

shaft_hole = Cylinder(hole_diameter/2, plate_thickness + 10)
cbore_hole = Pos(0, 0, plate_thickness/2 - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
result = result - shaft_hole - cbore_hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_rib_pocket_and_hole"
export_step(part, "output.step")