from build123d import *

base_diameter = 20.0
base_thickness = 10.0
arm_length = 60.0
arm_width_max = 30.0
arm_width_min = 10.0
hole_diameter = 4.0
hole_offset = 5.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_diameter/2, 0))
            l2 = Line(l1@1, (base_diameter/2, base_thickness))
            l3 = Line(l2@1, (arm_width_max/2, base_thickness + arm_length*0.2))
            l4 = Line(l3@1, (arm_width_min/2, base_thickness + arm_length))
            l5 = Line(l4@1, (0, base_thickness + arm_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(hole_offset, 0, 0) * Cylinder(hole_diameter/2, 200)
solid_body = solid_body - Pos(slot_offset, 0, base_thickness + arm_length/2) * Box(slot_length, slot_width, 200)
solid_body = solid_body - Pos(-500, 0, 0) * Box(1000, 1000, 1000)

part = solid_body
part.name = "split_arm"
export_step(part, "output.step")