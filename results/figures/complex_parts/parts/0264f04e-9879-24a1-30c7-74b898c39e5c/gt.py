from build123d import *

outer_radius = 30.0
base_height = 10.0
step1_radius = 20.0
step1_height = 15.0
step2_radius = 12.0
step2_height = 20.0
fillet_radius = 2.0
flange_diameter = 60.0
flange_height = 5.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

total_height = base_height + step1_height + step2_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0,0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, base_height))
            l3 = Line(l2@1, (step1_radius, base_height))
            a1 = ThreePointArc(l3@1, (step1_radius - fillet_radius, base_height + fillet_radius), (step1_radius, base_height + fillet_radius))
            l4 = Line(a1@1, (step1_radius, base_height + step1_height))
            l5 = Line(l4@1, (step2_radius, base_height + step1_height))
            a2 = ThreePointArc(l5@1, (step2_radius - fillet_radius, base_height + step1_height + fillet_radius), (step2_radius, base_height + step1_height + fillet_radius))
            l6 = Line(a2@1, (step2_radius, total_height))
            l7 = Line(l6@1, (0, total_height))
            l8 = Line(l7@1, l1@0)
        make_face()
    revolve(axis=Axis.Z)

socket_body = p.part
flange = Pos(0, 0, -flange_height/2) * Cylinder(flange_diameter/2, flange_height)
result = socket_body + flange

mid_z = base_height + step1_height/2
hole_r = mount_hole_diameter / 2
hole_h = total_height + flange_height + 10
for y in [mount_hole_spacing/2, -mount_hole_spacing/2]:
    result = result - Pos(0, y, mid_z) * Cylinder(hole_r, hole_h)

part = result
part.name = "stepped_socket_with_flange"
export_step(part, OUTPUT_PATH)