from build123d import *
import math

jaw_length = 80
jaw_width = 30
jaw_thickness = 10
notch_width = 12
notch_depth = 5
slot_width = 8
slot_length = 40
slot_offset = 15
boss_diameter = 10
boss_height = 4
hole_diameter = 4
countersink_diameter = 6
countersink_angle = 82
hole_spacing = 18
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

solid = p.part

slot_center_x = -jaw_length/2 + slot_offset
slot = Pos(slot_center_x, -jaw_width/2 + jaw_thickness/2, jaw_thickness/2) * Box(slot_width, jaw_thickness, slot_length)
solid = solid - slot

boss = Pos(0, 0, jaw_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid = solid + boss

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
for i in range(hole_count):
    x = (i - (hole_count-1)/2) * hole_spacing
    shaft = Pos(x, 0, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 1)
    solid = solid - shaft
    csk = Pos(x, 0, jaw_thickness - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)
    solid = solid - csk

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "jaw_with_notch_slot_boss_holes"
export_step(part, "output.step")