from build123d import *

plate_width = 80.0
plate_depth = 40.0
plate_thickness = 4.0
flange_height = 8.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_depth_cut = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
chamfer_size = 0.5
rib_width = 10.0
rib_height = 6.0
rib_offset = 12.0

base = Box(plate_width, plate_depth, plate_thickness)
flange = Pos(0, plate_depth/2 + flange_height/2, 0) * Box(plate_width, flange_height, plate_thickness)
body = base + flange

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
body = body - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    body = body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)

rib = Pos(0, -plate_depth/2 + rib_offset, 0) * Box(rib_width, rib_height, plate_thickness)
body = body + rib

body = chamfer(body.edges().filter_by(Axis.Z), chamfer_size)

part = body
part.name = "plate_with_flange_pocket_holes_rib"
export_step(part, "output.step")