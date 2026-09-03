from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 5.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 2.0
rib_spacing = 20.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_distance = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket_length = plate_length - 2 * wall_thickness
pocket_width = plate_width - 2 * wall_thickness
pocket_depth = plate_thickness - wall_thickness
pocket = Pos(0, 0, -plate_thickness/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib_count = int((plate_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -plate_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, -plate_thickness/2 + wall_thickness + rib_height/2) * Box(rib_thickness, pocket_width, rib_height)
    solid_body = solid_body + rib

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_ribs_holes"
export_step(part, "output.step")