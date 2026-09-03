from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 6.0
frame_margin = 5.0
slot_width = 4.0
slot_spacing = 15.0
slot_length = base_length - 2 * frame_margin
hole_diameter = 4.0
hole_offset = 12.0
fillet_radius = 1.5
bottom_fillet = 0.8

solid = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)
solid = fillet(solid.faces().sort_by(Axis.Z)[0].edges(), bottom_fillet)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_margin, base_width - 2*frame_margin, frame_height)
solid = solid + frame

slot1 = Pos(0, slot_spacing/2, base_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
slot2 = Pos(0, -slot_spacing/2, base_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
solid = solid - slot1 - slot2

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
for y in [hole_offset, -hole_offset]:
    solid = solid - Pos(base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid = solid - Pos(-base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = solid
part.name = "base_with_frame_slots_holes"
export_step(part, "output.step")