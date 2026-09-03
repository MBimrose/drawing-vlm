from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
taper_length = 20.0
taper_width = 10.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset = 15.0
chamfer_distance = 1.0
slot_width = 2.0
slot_length = 10.0
slot_spacing = 12.0
slot_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (arm_length, 0), (arm_length, taper_width),
                     (arm_length - taper_length, arm_width), (0, arm_width), close=True)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

for i in range(5):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, arm_width / 2, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness)

for i in range(5):
    x = slot_offset + i * slot_spacing
    solid_body = solid_body - Pos(x, arm_width / 2, arm_thickness * 3 / 4) * Box(slot_length, slot_width, arm_thickness / 2)

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1:]
solid_body = chamfer(chamfer_edges, chamfer_distance)

part = solid_body
part.name = "tapered_arm_with_holes_slots"
export_step(part, "output.step")