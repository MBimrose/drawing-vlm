from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
fillet_radius = 2.0
set_screw_diameter = 4.0
set_screw_offset = 5.0
slot_width = 6.0
slot_length = 15.0
slot_depth = 4.0
rib_count = 6
rib_width = 4.0
rib_height = 8.0
rib_thickness = 2.0
boss_radius = 5.0
boss_height = 3.0
tab_width = 8.0
tab_height = 10.0
tab_thickness = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, height))
            l3 = Line(l2@1, (inner_radius, height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

slot_box = Pos(outer_radius - slot_depth/2, 0, height/2) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

screw_cyl = Pos(outer_radius - set_screw_offset, 0, height/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, outer_radius * 2)
solid_body = solid_body - screw_cyl

boss = Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

tab = Pos(outer_radius - tab_thickness/2, 0, tab_thickness/2) * Box(tab_width, tab_height, tab_thickness)
solid_body = solid_body + tab

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_width, height)
    solid_body = solid_body + rib

part = solid_body
part.name = "collar_with_ribs"
export_step(part, "output.step")