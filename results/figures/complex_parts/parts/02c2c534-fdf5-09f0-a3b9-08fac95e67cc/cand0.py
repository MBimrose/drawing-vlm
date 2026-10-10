from build123d import *

arm_length = 70.0
base_radius = 10.0
tip_radius = 5.0
flange_thickness = 10.0
hole_diameter = 4.0
slot_width = 6.0
slot_depth = 8.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, flange_thickness))
            l3 = Line(l2 @ 1, (tip_radius, arm_length))
            l4 = Line(l3 @ 1, (0, arm_length))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

# Through hole along Z axis
solid_body = solid_body - Pos(0, 0, arm_length / 2) * Cylinder(hole_diameter / 2, arm_length + 20)

# Slot cut at tip
slot_box = Pos(0, 0, arm_length - slot_depth / 2) * Box(slot_width, arm_length, slot_depth)
solid_body = solid_body - slot_box

# Chamfer tip edges (edges on the top face)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_arm_with_slot"
export_step(part, "output.step")