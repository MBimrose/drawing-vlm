from build123d import *
import math

outer_radius = 30
inner_radius = 12
collar_height = 20
slot_width = 6
slot_depth = 4
fillet_radius = 2
rib_thickness = 2
rib_height = 8
rib_count = 6
relief_hole_diameter = 8
relief_depth = 2
boss_radius = 5
boss_height = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (inner_radius, collar_height), (outer_radius, collar_height), (outer_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

collar = p.part

slot = Pos(outer_radius - slot_depth/2, 0, collar_height * 1.2 / 2) * Box(slot_depth, slot_width, collar_height * 1.2)
collar = collar - slot

top_face = collar.faces().sort_by(Axis.Z)[-1]
collar = fillet(top_face.edges(), fillet_radius)
bottom_face = collar.faces().sort_by(Axis.Z)[0]
collar = fillet(bottom_face.edges(), fillet_radius)

relief = Pos(inner_radius, 0, -relief_depth/2) * Cylinder(relief_hole_diameter/2, relief_depth)
collar = collar - relief

boss = Pos(outer_radius - boss_height/2, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
collar = collar + boss

for i in range(rib_count):
    angle = math.radians(360 / rib_count * i)
    rib = Box(rib_thickness, rib_height, collar_height)
    rib = Rot(0, 0, math.degrees(angle)) * rib
    rib = Pos((inner_radius + rib_thickness/2)*math.cos(angle), (inner_radius + rib_thickness/2)*math.sin(angle), 0) * rib
    collar = collar + rib

part = collar
part.name = "collar_with_ribs"
export_step(part, OUTPUT_PATH)