from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 4.0
fillet_radius = 0.5
chamfer_distance = 0.8
mount_hole_dia = 2.0
mount_hole_spacing = 30.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner = offset(base, amount=-wall_thickness)
result = base - inner

slot = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(slot_width, wall_thickness, slot_height)
result = result - slot

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-outer_length/2 + wall_thickness/2, y, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, wall_thickness)
    result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

result = fillet(result.edges(), fillet_radius)

part = result
part.name = "shelled_box_with_slot_and_holes"
export_step(part, "output.step")