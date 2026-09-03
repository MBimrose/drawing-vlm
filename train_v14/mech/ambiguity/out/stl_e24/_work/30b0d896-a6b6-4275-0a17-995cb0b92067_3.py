from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 8.0
central_hole_diameter = 12.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 10.0
keyway_width = 4.0
keyway_length = 40.0
keyway_offset_y = -20.0
pocket_margin = 10.0
pocket_depth = 3.0
boss_diameter = 15.0
boss_height = 5.0
chamfer_size = 1.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 1)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, mount_hole_offset_y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

solid_body = solid_body - Pos(0, keyway_offset_y, plate_thickness/2) * Box(keyway_length, keyway_width, plate_thickness + 1)

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Box(plate_width - 2*pocket_margin, plate_height - 2*pocket_margin, pocket_depth)

solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")