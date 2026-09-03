from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
fillet_radius = 1.0
vent_width = 30.0
vent_height = 10.0
vent_offset_from_bottom = 5.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0
rib_width = 5.0
rib_height = 8.0
rib_spacing = 15.0

solid_body = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

vent_center_z = enclosure_height/2 + vent_offset_from_bottom + vent_height/2
vent_cut = Pos(0, enclosure_width/2 - wall_thickness/2, vent_center_z) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent_cut

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, dy, enclosure_height - wall_thickness/2) * Cylinder(mount_hole_diameter/2, wall_thickness)
        solid_body = solid_body - hole

rib_count = int((enclosure_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -enclosure_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_width, enclosure_width - 2*wall_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "enclosure_with_vents_and_ribs"
export_step(part, "output.step")