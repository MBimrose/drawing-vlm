from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 6.0
frame_margin = 5.0
slot_length = 50.0
slot_width = 8.0
slot_spacing = 15.0
hole_diameter = 4.0
hole_offset_y = 12.0
chamfer_size = 0.5
fillet_vertical = 1.5
fillet_top = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_size)
base = fillet(base.edges().filter_by(Axis.Z), fillet_vertical)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_margin, base_width - 2*frame_margin, frame_height)
base = base + frame
base = fillet(base.edges().filter_by(Axis.Z), fillet_top)

slot1 = Pos(0, -slot_spacing/2, base_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
slot2 = Pos(0, slot_spacing/2, base_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
base = base - slot1 - slot2

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
for y in [-hole_offset_y/2, hole_offset_y/2]:
    base = base - Pos(base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    base = base - Pos(-base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = base
part.name = "base_with_frame_slots_holes"
export_step(part, "output.step")