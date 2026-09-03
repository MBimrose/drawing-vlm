from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
vent_width = 40.0
vent_height = 12.0
vent_offset_from_top = 5.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
rib_width = 6.0
rib_height = 10.0
rib_thickness = 1.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

outer_box = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = outer_box.faces().sort_by(Axis.Z)[-1]
bottom_face = outer_box.faces().sort_by(Axis.Z)[0]
outer_shell = offset(outer_box, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(inner_length, inner_width, base_thickness)
enclosure = outer_shell + base_plate

vent_center_z = outer_height/2 - vent_offset_from_top - vent_height/2
vent_cut = Pos(0, outer_width/2 - wall_thickness/2, vent_center_z) * Box(vent_width, wall_thickness, vent_height)
enclosure = enclosure - vent_cut

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    enclosure = enclosure - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

rib1 = Pos(-inner_length/2 + rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
rib2 = Pos(inner_length/2 - rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
enclosure = enclosure + rib1 + rib2

part = enclosure
part.name = "ventilated_enclosure"
export_step(part, "output.step")