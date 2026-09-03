from build123d import *

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_x = -bracket_length/2 + 15.0
boss_offset_y = 0.0
through_hole_diameter = 8.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_offset_y = -bracket_width/4

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, bracket_thickness/2) * Cylinder(mount_hole_diameter/2, bracket_thickness + 2)

rib = Pos(0, rib_offset_y, -rib_height/2) * Box(rib_width, bracket_thickness, rib_height)
solid_body = solid_body + rib

boss = Pos(boss_offset_x, boss_offset_y, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

cbore = Pos(boss_offset_x, boss_offset_y, bracket_thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(boss_offset_x, boss_offset_y, (bracket_thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, bracket_thickness + boss_height + 2)
solid_body = solid_body - thru

part = solid_body
part.name = "bracket"
export_step(part, "output.step")