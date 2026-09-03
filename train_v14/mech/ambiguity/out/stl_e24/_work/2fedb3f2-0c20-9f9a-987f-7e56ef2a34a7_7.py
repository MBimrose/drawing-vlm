from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
frame_height = 6.0
frame_margin = 5.0
frame_wall_thickness = 5.0
slot_width = 8.0
slot_length = plate_length - 2 * frame_margin - 10.0
slot_spacing = 15.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 15.0
fillet_radius = 1.5
frame_fillet = 0.8
chamfer_distance = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_distance)

frame = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 2*frame_margin, plate_width - 2*frame_margin, frame_height)
frame = fillet(frame.edges().filter_by(Axis.Z), frame_fillet)

result = base + frame

inner_cut = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 2*frame_margin - 2*frame_wall_thickness, plate_width - 2*frame_margin - 2*frame_wall_thickness, frame_height)
result = result - inner_cut

for y in [-slot_spacing/2, slot_spacing/2]:
    slot = Pos(0, y, plate_thickness + frame_height/2) * Box(slot_length, slot_width, frame_height)
    result = result - slot

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    (plate_length/2 - hole_offset_x, -plate_width/2 + hole_offset_y),
    (-plate_length/2 + hole_offset_x, plate_width/2 - hole_offset_y),
    (plate_length/2 - hole_offset_x, plate_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)
    result = result - hole

part = result
part.name = "plate_with_frame"
export_step(part, "output.step")