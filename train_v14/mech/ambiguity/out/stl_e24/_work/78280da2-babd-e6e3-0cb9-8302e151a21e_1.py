from build123d import *
import math

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
notch_width = 10.0
notch_depth = 6.0
slot_width = 8.0
slot_length = 12.0
slot_offset = 15.0
boss_diameter = 10.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_depth = 2.0
hole_spacing = 18.0
hole_count = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-jaw_length/2, -jaw_width/2),
                (jaw_length/2, -jaw_width/2),
                (jaw_length/2, jaw_width/2 - notch_depth),
                (jaw_length/2 - notch_width, jaw_width/2 - notch_depth),
                (jaw_length/2 - notch_width, jaw_width/2),
                (-jaw_length/2, jaw_width/2),
                close=True
            )
        make_face()
    extrude(amount=jaw_thickness)

solid_body = p.part

slot_center_x = -jaw_length/2 + slot_offset
slot = Pos(slot_center_x, -jaw_width/2 + jaw_thickness/2, jaw_thickness/2) * Box(slot_width, jaw_thickness, slot_length)
solid_body = solid_body - slot

boss = Pos(0, 0, jaw_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    shaft = Pos(x, 0, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 1)
    solid_body = solid_body - shaft
    csink = Pos(x, 0, jaw_thickness - countersink_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, countersink_depth)
    solid_body = solid_body - csink

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "jaw_with_notch_slot_boss_holes"
export_step(part, "output.step")