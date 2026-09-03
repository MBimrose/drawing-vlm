from build123d import *

bracket_length = 80
bracket_width = 40
sheet_thickness = 5
boss_radius = 12
boss_height = 12
hole_diameter = 8
counterbore_diameter = 14
counterbore_depth = 2.5
mount_hole_diameter = 6
mount_hole_offset = 10
chamfer_size = 0.8
slot_width = 6
slot_length = bracket_length - 20

base = Pos(0, 0, sheet_thickness/2) * Box(bracket_length, bracket_width, sheet_thickness)
boss = Pos(0, bracket_width/2 + boss_radius, sheet_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

cbore = Pos(0, bracket_width/2 + boss_radius, sheet_thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, bracket_width/2 + boss_radius, (sheet_thickness + boss_height)/2) * Cylinder(hole_diameter/2, sheet_thickness + boss_height + 10)
result = result - cbore - shaft

for x in [-bracket_length/2 + mount_hole_offset, bracket_length/2 - mount_hole_offset]:
    result = result - Pos(x, 0, sheet_thickness/2) * Cylinder(mount_hole_diameter/2, sheet_thickness + 10)

slot = Pos(0, 0, sheet_thickness/2) * Box(slot_width, slot_length, sheet_thickness)
result = result - slot

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "bracket"
export_step(part, "output.step")