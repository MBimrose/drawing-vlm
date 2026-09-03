from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
notch_width = 10.0
notch_depth = 5.0
slot_width = 8.0
slot_depth = 6.0
boss_diameter = 10.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
hole_spacing = 18.0
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

slot_cut = Pos(-jaw_length/2 + slot_width/2 + 5, -jaw_width/2 + slot_depth/2, jaw_thickness/2) * Box(slot_width, slot_depth, jaw_thickness)
solid_body = solid_body - slot_cut

boss = Pos(0, 0, jaw_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(3):
    x = (i - 1) * hole_spacing
    csk = Pos(x, 0, jaw_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, jaw_thickness, countersink_angle)
    solid_body = solid_body - csk

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "jaw_with_notch_slot_boss"
export_step(part, "output.step")