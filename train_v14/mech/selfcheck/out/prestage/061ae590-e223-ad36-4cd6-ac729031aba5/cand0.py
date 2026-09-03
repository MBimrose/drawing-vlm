from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_chamfer = 1.5
hole_diameter = 16.0
hole_offset = 10.0
rib_width = 6.0
rib_thickness = 3.0
rib_height = 12.0
rib_spacing_x = 40.0
rib_spacing_y = 40.0
pocket_diameter = 30.0
pocket_depth = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), corner_chamfer)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

rib_positions = [
    (-rib_spacing_x/2, -rib_spacing_y/2),
    ( rib_spacing_x/2, -rib_spacing_y/2),
    (-rib_spacing_x/2,  rib_spacing_y/2),
    ( rib_spacing_x/2,  rib_spacing_y/2)
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

part = solid_body
part.name = "plate_with_ribs_and_pocket"
export_step(part, "output.step")