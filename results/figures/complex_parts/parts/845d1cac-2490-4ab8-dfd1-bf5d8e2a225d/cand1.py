from build123d import *

arm_length = 80.0
arm_width = 12.0
arm_thickness = 6.0
pivot_radius = 6.0
pivot_length = 20.0
relief_length = 30.0
relief_depth = 4.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset = 15.0
notch_width = 10.0
notch_depth = 3.0

base = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
pivot = Pos(arm_length, 0, 0) * Rot(0, 90, 0) * Cylinder(pivot_radius, pivot_length)
result = base + pivot

with BuildPart() as relief_bp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, -arm_width/2), (0, arm_width/2))
            l2 = Line(l1@1, (relief_length, arm_width/2 - relief_depth))
            l3 = Line(l2@1, (relief_length, -arm_width/2 + relief_depth))
            l4 = Line(l3@1, (0, -arm_width/2))
        make_face()
    extrude(amount=arm_thickness)
relief_cut = Pos(arm_length - relief_length, 0, 0) * relief_bp.part
result = result - relief_cut

notch_cut = Pos(arm_length/2, arm_width/2 - notch_depth/2, arm_thickness/2) * Box(notch_width, notch_depth, arm_thickness)
result = result - notch_cut

for i in range(2):
    hx = arm_length/2 + hole_offset + i * hole_spacing
    hole_cut = Pos(hx, 0, 0) * Cylinder(hole_diameter/2, arm_thickness)
    result = result - hole_cut

part = result
part.name = "arm_with_pivot"
export_step(part, "output.step")