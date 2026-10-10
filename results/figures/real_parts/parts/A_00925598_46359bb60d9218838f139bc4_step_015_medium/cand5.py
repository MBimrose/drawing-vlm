from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 10.0
corner_hole_diameter = 8.0
corner_hole_offset = 12.0
boss_radius = 15.0
boss_height = 60.0
groove_width = 5.0
groove_depth = 2.0
chamfer_distance = 5.0
bottom_chamfer = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

corner_positions = [
    (plate_width/2 - corner_hole_offset, plate_height/2 - corner_hole_offset),
    (-plate_width/2 + corner_hole_offset, plate_height/2 - corner_hole_offset),
    (-plate_width/2 + corner_hole_offset, -plate_height/2 + corner_hole_offset),
    (plate_width/2 - corner_hole_offset, -plate_height/2 + corner_hole_offset),
]
for x, y in corner_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(corner_hole_diameter/2, plate_thickness)

solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius + groove_width, boss_height)
solid_body = solid_body - Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)

groove_radius = boss_radius + groove_width/2
groove_z = plate_thickness + boss_height - groove_depth/2
solid_body = solid_body - Pos(0, 0, groove_z) * Cylinder(groove_radius, groove_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), bottom_chamfer)

part = solid_body
part.name = "plate_with_boss_and_groove"
export_step(part, "output.step")