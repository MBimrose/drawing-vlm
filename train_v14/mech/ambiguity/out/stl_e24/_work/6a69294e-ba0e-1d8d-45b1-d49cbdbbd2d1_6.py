from build123d import *

lever_length = 80
lever_width = 20
lever_thickness = 10
taper_length = 20
taper_width = 10
hole_diameter = 4
hole_spacing = 12
hole_offset = 15
chamfer_distance = 1
slot_width = 2
slot_length = lever_width - 4
slot_spacing = 10
slot_count = int((lever_length - 2 * hole_offset) / slot_spacing)

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (lever_length, 0), (lever_length, lever_width - taper_width),
                     (lever_length - taper_length, lever_width), (0, lever_width), close=True)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, lever_width / 2, lever_thickness / 2) * Cylinder(hole_diameter / 2, lever_thickness)

for i in range(slot_count):
    x = hole_offset + i * slot_spacing
    solid_body = solid_body - Pos(x, lever_width / 2, lever_thickness * 3 / 4) * Box(slot_length, slot_width, lever_thickness / 2)

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = chamfer(chamfer_edges, chamfer_distance)

part = solid_body
part.name = "lever"
export_step(part, "output.step")