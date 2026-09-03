from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = 20.0
slot_width = 5.0
slot_height = 15.0
slot_chamfer = 0.5
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    solid_body = solid_body + rib

slot = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2 - slot_height/2) * Box(slot_width, wall_thickness, slot_height)
slot_edges = slot.edges().filter_by(Axis.Z)
slot = chamfer(slot_edges, slot_chamfer)
solid_body = solid_body - slot

for dx in [-hole_spacing_x/2, hole_spacing_x/2]:
    for dy in [-hole_spacing_y/2, hole_spacing_y/2]:
        hole = Pos(dx, dy, outer_height - wall_thickness/2) * Cylinder(hole_diameter/2, wall_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_ribs_slot_holes"
export_step(part, "output.step")