from build123d import *

base_radius = 30.0
base_height = 15.0
step_radius = 20.0
step_height = 15.0
boss_radius = 12.0
boss_height = 20.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset = 20.0
slot_width = 6.0
slot_length = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (step_radius, base_height))
            l4 = Line(l3@1, (step_radius, base_height + step_height))
            l5 = Line(l4@1, (boss_radius, base_height + step_height))
            l6 = Line(l5@1, (boss_radius, base_height + step_height + boss_height))
            l7 = Line(l6@1, (0, base_height + step_height + boss_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

# Chamfer edges at step transitions
chamfer_edges = []
for e in solid_body.edges():
    z = e.center().Z
    if abs(z - base_height) < 0.5 or abs(z - (base_height + step_height)) < 0.5:
        chamfer_edges.append(e)
solid_body = chamfer(chamfer_edges, chamfer_size)

# Mounting holes through base
for x, y in [(0, hole_offset), (0, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

# Slot cut through step
slot_box = Pos(step_radius, 0, base_height + step_height/2) * Box(slot_width, slot_length, step_height)
solid_body = solid_body - slot_box

part = solid_body
part.name = "stepped_cylinder_with_holes_and_slot"
export_step(part, "output.step")