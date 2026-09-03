from build123d import *

base_length = 70.0
base_width = 40.0
base_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_x = -base_length/2 + 15.0
boss_offset_y = 0.0
blind_hole_diameter = 8.0
blind_hole_depth = 6.0
countersink_diameter = 12.0
countersink_depth = 2.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_offset_y = -base_width/2 + 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(base_length, base_width)
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, base_thickness/2) * Cylinder(mount_hole_diameter/2, base_thickness + 1)

solid_body = solid_body + Pos(boss_offset_x, boss_offset_y, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = solid_body - Pos(boss_offset_x, boss_offset_y, base_thickness + boss_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

solid_body = solid_body - Pos(boss_offset_x, boss_offset_y, base_thickness + boss_height - countersink_depth/2) * Cone(blind_hole_diameter/2, countersink_diameter/2, countersink_depth)

solid_body = solid_body + Pos(0, rib_offset_y, -rib_height/2) * Box(rib_width, base_thickness, rib_height)

part = solid_body
part.name = "base_plate_with_boss"
export_step(part, "output.step")