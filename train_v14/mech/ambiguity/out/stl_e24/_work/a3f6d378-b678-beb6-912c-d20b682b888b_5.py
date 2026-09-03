from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
tab_radius = 8.0
slot_width = 6.0
slot_length = plate_length * 0.8
slot_offset_y = -plate_width / 4
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 10.0
num_holes = 7
chamfer_size = 0.8
fillet_radius = 1.0

base_plate = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length / 2 - tab_radius, 0, 0) * Cylinder(tab_radius, plate_thickness)
result = base_plate + tab

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 3, both=True)
slot_solid = Pos(0, slot_offset_y, 0) * slot_bp.part
result = result - slot_solid

for i in range(num_holes):
    x = (i - (num_holes - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, plate_thickness / 2 - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

top_y_face = result.faces().sort_by(Axis.Y)[-1]
chamfer_edges = top_y_face.edges().filter_by(Axis.X)
result = chamfer(chamfer_edges, chamfer_size)

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "plate_with_tab_slot_holes"
export_step(part, "output.step")