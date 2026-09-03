from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
slot_width = 10.0
slot_height = 20.0
slot_offset = 40.0
boss_radius = 10.0
boss_height = 12.0
boss_offset = 15.0
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - wall_thickness/2, 0, slot_offset - length/2) * Box(wall_thickness*2, slot_width, slot_height)
solid_body = solid_body - slot_box

boss = Pos(outer_radius + boss_height/2, 0, boss_offset - length/2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(mount_hole_dia/2, length)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slot_boss"
export_step(part, "output.step")