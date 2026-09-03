from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
taper_length = 20.0
taper_width_end = 10.0
slot_width = 2.0
slot_length = arm_length * 0.8
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset = 15.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (arm_length, 0), (arm_length, taper_width_end),
                     (arm_length - taper_length, arm_width), (0, arm_width), close=True)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

slot = Pos(arm_length/2, arm_width/2, arm_thickness * 3/4) * Box(slot_length, slot_width, arm_thickness/2)
solid_body = solid_body - slot

for i in range(3):
    hx = hole_offset + i * hole_spacing
    hy = arm_width / 2
    hole = Pos(hx, hy, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)
    solid_body = solid_body - hole

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x = max(e.center().X for e in z_edges)
chamfer_edges = [e for e in z_edges if abs(e.center().X - max_x) < 0.01]
solid_body = chamfer(chamfer_edges, chamfer_distance)

part = solid_body
part.name = "tapered_arm_with_slot_and_holes"
export_step(part, "output.step")