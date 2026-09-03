from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 30.0
rib_thickness = plate_thickness
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 2.5
hole_diameter = 4.0
hole_offset_x = 15.0
hole_offset_y = 12.0
chamfer_size = 1.0

base = Box(plate_width, plate_height, plate_thickness)
rib_left = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
rib_right = Pos(plate_width/2 - rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
result = base + rib_left + rib_right

pocket = Pos(0, plate_height/4, plate_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

hole1 = Pos(-plate_width/2 + hole_offset_x, -plate_height/2 + hole_offset_y, 0) * Cylinder(hole_diameter/2, plate_thickness)
hole2 = Pos(plate_width/2 - hole_offset_x, -plate_height/2 + hole_offset_y, 0) * Cylinder(hole_diameter/2, plate_thickness)
result = result - hole1 - hole2

bottom_face = result.faces().sort_by(Axis.Y)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "plate_with_ribs_pocket_holes"
export_step(part, "output.step")