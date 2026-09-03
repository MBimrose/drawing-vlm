from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
fillet_radius = 2.0
chamfer_size = 0.5
pocket_width = 30.0
pocket_depth = 20.0
pocket_recess_depth = 2.5
slot_length = 40.0
slot_width = 6.0
slot_offset_y = 20.0
hole_diameter = 4.0
hole_head_diameter = 7.0
hole_head_angle = 90.0
hole_offset_x = -20.0
hole_offset_y = 20.0

solid = Box(plate_width, plate_depth, plate_thickness)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = fillet(top_face.edges(), fillet_radius)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_recess_depth/2) * Box(pocket_width, pocket_depth, pocket_recess_depth)
solid = solid - pocket

slot1 = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
solid = solid - slot1 - slot2

hole1 = Pos(hole_offset_x, hole_offset_y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, hole_head_diameter/2, plate_thickness, hole_head_angle)
hole2 = Pos(hole_offset_x, -hole_offset_y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, hole_head_diameter/2, plate_thickness, hole_head_angle)
solid = solid - hole1 - hole2

part = solid
part.name = "plate_with_pockets_slots_holes"
export_step(part, "output.step")