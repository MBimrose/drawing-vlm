from build123d import *

base_width = 80.0
base_depth = 60.0
base_thickness = 5.0
frame_height = 6.0
frame_margin = 5.0
slot_length = 60.0
slot_width = 4.0
slot_spacing = 15.0
hole_diameter = 4.0
hole_offset = 8.0
fillet_vertical = 1.5
fillet_bottom = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_vertical)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = fillet(bottom_face.edges(), fillet_bottom)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width - 2*frame_margin, base_depth - 2*frame_margin, frame_height)
result = base + frame

total_height = base_thickness + frame_height
for y in [-slot_spacing/2, slot_spacing/2]:
    slot = Pos(0, y, total_height/2) * Box(slot_length, slot_width, total_height)
    result = result - slot

hole_positions = [
    (base_width/2 - hole_offset, base_depth/2 - hole_offset),
    (-base_width/2 + hole_offset, base_depth/2 - hole_offset),
    (base_width/2 - hole_offset, -base_depth/2 + hole_offset),
    (-base_width/2 + hole_offset, -base_depth/2 + hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, total_height)
    result = result - hole

part = result
part.name = "base_with_frame_slots_holes"
export_step(part, "output.step")