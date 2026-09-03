from build123d import *

plate_width = 80.0
plate_height = 40.0
plate_thickness = 8.0
tab_width = 30.0
tab_height = 12.0
slot_width = 6.0
slot_height = 30.0
slot_spacing = 15.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Box(plate_width, plate_height, plate_thickness)
tab = Pos(0, plate_height/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
solid_body = base + tab

slot1 = Pos(-slot_spacing/2, 0, 0) * Box(slot_width, slot_height, plate_thickness)
slot2 = Pos(slot_spacing/2, 0, 0) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot1 - slot2

hole1 = Pos(-hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 100)
hole2 = Pos(hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 100)
solid_body = solid_body - hole1 - hole2

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_tab_slots_holes"
export_step(part, "output.step")