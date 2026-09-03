from build123d import *

outer_diameter = 40.0
wall_thickness = 3.0
tube_length = 100.0
slot_width = 8.0
slot_length = 30.0
slot_spacing = 20.0
chamfer_distance = 1.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, tube_length * 2)
solid_body = solid_body - Cylinder(inner_radius, tube_length * 2)

slot_center_x = outer_radius - wall_thickness / 2.0
slot_box = Box(slot_width, wall_thickness, slot_length)

for i in range(4):
    z_pos = slot_spacing * i
    solid_body = solid_body - Pos(slot_center_x, 0, z_pos) * slot_box

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "tube_with_slots"
export_step(part, "output.step")