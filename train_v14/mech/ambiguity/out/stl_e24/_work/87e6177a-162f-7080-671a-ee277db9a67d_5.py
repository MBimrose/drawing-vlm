from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
thread_pitch = 4.0
thread_depth = 1.5
thread_length = height - 5.0
keyway_width = 12.0
keyway_depth = 2.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_count = 4
slot_width = 2.0
slot_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
thread_minor_diameter = (inner_radius - thread_depth) * 2.0

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

thread_cutter = Pos(0, 0, thread_length/2) * Cylinder(thread_minor_diameter / 2.0, thread_length)
solid_body = solid_body - thread_cutter

keyway_cutter = Pos(outer_radius - keyway_depth/2.0, 0, keyway_depth/2.0) * Box(keyway_width, height, keyway_depth)
solid_body = solid_body - keyway_cutter

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = (outer_radius - wall_thickness/2.0) * math.cos(angle)
    py = (outer_radius - wall_thickness/2.0) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2) * Cylinder(mount_hole_diameter/2, height)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = (outer_radius - wall_thickness/2.0) * math.cos(angle)
    py = (outer_radius - wall_thickness/2.0) * math.sin(angle)
    slot_cutter = Pos(px, py, wall_thickness/2.0) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, wall_thickness, wall_thickness)
    solid_body = solid_body - slot_cutter

part = solid_body
part.name = "threaded_cylinder_with_keyway"
export_step(part, "output.step")