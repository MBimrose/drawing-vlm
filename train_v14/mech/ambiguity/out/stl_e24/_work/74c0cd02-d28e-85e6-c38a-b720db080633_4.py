from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - wall_thickness*2 - 6.0
rib_spacing = 20.0
vent_slot_width = 5.0
vent_slot_height = outer_height - wall_thickness*2

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib_count = int((outer_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    base = base + rib

vent = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2 - wall_thickness - vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
base = base - vent

part = base
part.name = "vented_box_with_ribs"
export_step(part, "output.step")