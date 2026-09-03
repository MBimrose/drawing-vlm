from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 2.0
hole_diameter = 7.0
hole_spacing = 30.0
hole_offset_y = 10.0
chamfer_size = 0.5
rib_height = 2.0
rib_width = 5.0

solid = Box(plate_length, plate_width, plate_thickness)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

for x, y in [(-hole_spacing, 0), (0, hole_offset_y), (hole_spacing, 0)]:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, plate_width, rib_height)
solid = solid + rib

part = solid
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")