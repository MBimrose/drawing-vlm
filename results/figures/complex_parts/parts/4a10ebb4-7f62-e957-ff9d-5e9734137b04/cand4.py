from build123d import *

housing_length = 80.0
housing_width = 50.0
housing_height = 30.0
wall_thickness = 2.0
vent_slot_width = 30.0
vent_slot_height = 10.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0
chamfer_distance = 0.5
rib_thickness = 2.0
rib_height = 5.0

solid_body = Pos(0, 0, housing_height/2) * Box(housing_length, housing_width, housing_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vent_cut = Pos(0, 0, housing_height - wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)
solid_body = solid_body - vent_cut

hole_r = mount_hole_diameter / 2
for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        solid_body = solid_body - Pos(dx, dy, housing_height/2) * Cylinder(hole_r, housing_height)

rib = Pos(0, 0, -rib_height/2) * Box(housing_length - 2*wall_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "housing_with_vents_and_ribs"
export_step(part, "output.step")