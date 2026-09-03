from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
frame_height = 6.0
frame_margin = 5.0
inner_fillet_radius = 1.5
outer_fillet_radius = 0.8
chamfer_distance = 0.5
hole_diameter = 4.0
hole_spacing = 30.0
slot_width = 4.0
slot_spacing = 15.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), inner_fillet_radius)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_distance)

frame_outer = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 2*frame_margin, plate_width - 2*frame_margin, frame_height)
frame_inner = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 4*frame_margin, plate_width - 4*frame_margin, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), outer_fillet_radius)

result = base + frame

slot_length = plate_length - 4*frame_margin
slot1 = Pos(0, -slot_spacing/2, plate_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
slot2 = Pos(0, slot_spacing/2, plate_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
result = result - slot1 - slot2

hole_r = hole_diameter / 2
hole_h = plate_thickness + frame_height + 10
for y in [-plate_width/2 + frame_margin + hole_spacing/2, plate_width/2 - frame_margin - hole_spacing/2]:
    result = result - Pos(plate_length/2, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    result = result - Pos(-plate_length/2, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = result
part.name = "plate_with_frame"
export_step(part, "output.step")