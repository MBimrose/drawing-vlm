from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 12.0
corner_radius = 5.0
slot_length = 40.0
slot_width = 8.0
slot_spacing = 20.0
central_hole_diameter = 10.0
chamfer_size = 1.0
rib_width = 20.0
rib_height = 10.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
        Circle(central_hole_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=plate_thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
top_right_edge = max(vertical_edges, key=lambda e: (e.center().X, e.center().Y))
solid_body = fillet([top_right_edge], corner_radius)

for y_offset in [-slot_spacing / 2, slot_spacing / 2]:
    slot = Pos(0, y_offset, plate_thickness / 2) * Box(slot_length, slot_width, plate_thickness)
    solid_body = solid_body - slot

rib = Pos(0, 0, plate_thickness - rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slots_and_rib"
export_step(part, "output.step")