from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
chamfer_size = 2.0
hole_diameter = 6.0
hole_offset = 10.0
slot_length = 10.0
slot_width = 4.0
slot_offset = 5.0
recess_radius = 8.0
recess_depth = 4.0
center_hole_diameter = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)

for x, y in [(-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
             (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
             (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
             (-plate_length/2 + hole_offset, plate_width/2 - hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = solid_body - Pos(-plate_length/2 + slot_offset, 0, 0) * Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - Pos(plate_length/2 - slot_offset, 0, 0) * Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - Pos(0, -plate_width/2 + slot_offset, 0) * Box(slot_width, slot_length, plate_thickness * 2)
solid_body = solid_body - Pos(0, plate_width/2 - slot_offset, 0) * Box(slot_width, slot_length, plate_thickness * 2)

solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(center_hole_diameter/2, boss_height + plate_thickness + 10)

part = solid_body
part.name = "plate_with_boss"
export_step(part, "output.step")