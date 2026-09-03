from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 5.0
hole_diameter = 4.5
hole_head_diameter = 8.6
hole_head_angle = 90.0
hole_spacing = 50.0
chamfer_size = 0.8
rib_height = 2.0
rib_width = 10.0
rib_length = 60.0

solid_body = Box(base_length, base_width, base_thickness)
solid_body = solid_body - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, base_thickness)

hole = CounterSinkHole(hole_diameter/2, hole_head_diameter/2, base_thickness, hole_head_angle)
solid_body = solid_body - Pos(-hole_spacing/2, 0, -base_thickness/2) * hole
solid_body = solid_body - Pos(hole_spacing/2, 0, -base_thickness/2) * hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, -base_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "base_plate_with_slot_holes_and_rib"
export_step(part, "output.step")