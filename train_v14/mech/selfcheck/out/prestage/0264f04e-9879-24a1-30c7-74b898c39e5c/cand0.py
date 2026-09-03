from build123d import *

base_radius = 30.0
base_height = 15.0
shoulder_radius = 20.0
shoulder_height = 15.0
boss_radius = 12.0
boss_height = 20.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
slot_width = 8.0
slot_length = 30.0
rib_thickness = 4.0
rib_height = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (shoulder_radius, base_height))
            l4 = Line(l3@1, (shoulder_radius, base_height + shoulder_height))
            l5 = Line(l4@1, (boss_radius, base_height + shoulder_height))
            l6 = Line(l5@1, (boss_radius, base_height + shoulder_height + boss_height))
            l7 = Line(l6@1, (0, base_height + shoulder_height + boss_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

fillet_sphere = Pos(0, 0, base_height + shoulder_height) * Sphere(fillet_radius)
solid_body = solid_body - fillet_sphere

total_height = base_height + shoulder_height + boss_height
for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)

slot_box = Pos(base_radius - slot_width/2, 0, total_height/2) * Box(slot_width, slot_length, total_height)
solid_body = solid_body - slot_box

rib_box = Pos(boss_radius + rib_thickness/2, 0, base_height + shoulder_height/2) * Box(rib_thickness, rib_height, shoulder_height)
solid_body = solid_body + rib_box

part = solid_body
part.name = "stepped_cylinder_with_features"
export_step(part, "output.step")