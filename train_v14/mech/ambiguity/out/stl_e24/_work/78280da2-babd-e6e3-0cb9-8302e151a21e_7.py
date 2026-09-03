from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
notch_width = 10.0
notch_depth = 5.0
slot_width = 8.0
slot_length = 20.0
slot_offset = 12.0
boss_diameter = 10.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_depth = 2.0
hole_spacing = 18.0
hole_count = 3
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
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
solid_body = solid_body - Pos(-jaw_length/2 + slot_offset, -jaw_width/2 + jaw_thickness/2, jaw_thickness/2) * Box(slot_width, jaw_thickness, slot_length)
solid_body = solid_body + Pos(0, 0, jaw_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for i in range(hole_count):
    x = -jaw_length/2 + hole_spacing + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 1)
    solid_body = solid_body - Pos(x, 0, jaw_thickness - countersink_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, countersink_depth)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "jaw_with_notch_slot_boss_holes"
export_step(part, "output.step")