from build123d import *

plate_length = 60.0
plate_width = 40.0
plate_thickness = 8.0
boss_diameter = 20.0
boss_height = 4.0
hole_diameter = 6.0
hole_offset = 15.0
pocket_depth = 2.0
pocket_margin = 5.0
fillet_radius = 2.0
chamfer_distance = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 20)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_boss_holes_pocket"
export_step(part, "output.step")