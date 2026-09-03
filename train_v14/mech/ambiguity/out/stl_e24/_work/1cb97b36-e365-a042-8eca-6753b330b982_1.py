from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
tslot_stem_width = 6.0
tslot_stem_depth = 20.0
tslot_cross_width = 30.0
tslot_cross_thickness = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 60.0
gusset_length = 12.0
gusset_height = 30.0
gusset_thickness = plate_thickness

base = Box(plate_length, plate_width, plate_thickness)

stem = Box(tslot_stem_width, tslot_stem_depth, plate_thickness)
cross = Pos(0, tslot_stem_depth/2 + tslot_cross_thickness/2, 0) * Box(tslot_cross_width, tslot_cross_thickness, plate_thickness)
tslot = stem + cross
base = base - tslot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    base = base - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

with BuildPart() as gp:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, -gusset_height/2), (gusset_length, 0), (0, gusset_height/2), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = gp.part

gusset_right = Pos(plate_length/2, 0, 0) * gusset
gusset_left = Pos(-plate_length/2, 0, 0) * mirror(gusset, about=Plane.YZ)

part = base + gusset_right + gusset_left
part.name = "plate_with_tslot_and_gussets"
export_step(part, "output.step")