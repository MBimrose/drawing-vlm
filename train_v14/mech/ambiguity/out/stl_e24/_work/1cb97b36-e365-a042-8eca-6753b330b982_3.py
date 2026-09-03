from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
gusset_height = 30.0
gusset_width = 12.0
slot_stem_width = 6.0
slot_stem_depth = 20.0
slot_top_width = 30.0
slot_top_thickness = 6.0
hole_diameter = 4.0
hole_spacing = 60.0

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.XY.offset(-plate_thickness/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((0, -gusset_height/2), (gusset_width, 0))
            l2 = Line(l1@1, (0, gusset_height/2))
            l3 = Line(l2@1, (0, -gusset_height/2))
        make_face()
    extrude(amount=plate_thickness)
gusset = gp.part

left_gusset = Pos(-plate_length/2, 0, 0) * gusset
right_gusset = Pos(plate_length/2, 0, 0) * gusset

result = base + left_gusset + right_gusset

stem_cut = Pos(0, 0, 0) * Box(slot_stem_width, slot_stem_depth, plate_thickness)
top_cut = Pos(0, slot_stem_depth/2 + slot_top_thickness/2, 0) * Box(slot_top_width, slot_top_thickness, plate_thickness)
result = result - stem_cut - top_cut

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

part = result
part.name = "plate_with_gussets_and_tslot"
export_step(part, "output.step")