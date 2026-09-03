from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_width = 6.0
slot_depth = 20.0
slot_top_width = 30.0
slot_top_height = 6.0
hole_diameter = 4.0
hole_spacing = 60.0
gusset_width = 12.0
gusset_height = 30.0

result = Box(plate_length, plate_width, plate_thickness)

slot1 = Pos(0, 0, 0) * Box(slot_width, slot_depth, plate_thickness)
slot2 = Pos(0, slot_depth/2 + slot_top_height/2, 0) * Box(slot_top_width, slot_top_height, plate_thickness)
result = result - slot1 - slot2

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, -gusset_height/2), (0, gusset_height/2), (-gusset_width, 0), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = gp.part

result = result + Pos(plate_length/2, 0, 0) * gusset
result = result + Pos(-plate_length/2, 0, 0) * mirror(gusset, about=Plane.YZ)

part = result
part.name = "plate_with_tslot_holes_gussets"
export_step(part, "output.step")