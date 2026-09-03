from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
cover_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 20.0
vent_spacing = 8.0
vent_count = 7
mount_hole_diameter = 3.0
mount_hole_spacing_x = 20.0
mount_hole_spacing_y = 20.0
chamfer_distance = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, inner_height/2) * Box(inner_length, inner_width, inner_height)
base = base - cavity

cover = Pos(0, 0, outer_height - cover_thickness/2) * Box(outer_length, outer_width, cover_thickness)

for i in range(vent_count):
    x = (i - (vent_count - 1) / 2) * vent_spacing
    slot = Pos(x, -outer_width/2 + cover_thickness/2, outer_height - cover_thickness/2) * Box(vent_slot_width, cover_thickness, vent_slot_height)
    cover = cover - slot

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, dy, outer_height - cover_thickness/2) * Cylinder(mount_hole_diameter/2, cover_thickness)
        cover = cover - hole

result = base + cover

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_distance)

part = result
part.name = "ventilated_enclosure"
export_step(part, "output.step")