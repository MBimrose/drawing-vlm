from build123d import *

length = 80.0
width = 40.0
height = 20.0
wall_thickness = 2.0
top_fillet_radius = 3.0
pocket_length = 30.0
pocket_width = 15.0
pocket_depth = 10.0
vent_diameter = 4.0
vent_spacing = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-length/2, -width/2), (length/2, -width/2))
            l2 = Line(l1@1, (length/2, width/2))
            arc = ThreePointArc(l2@1, (0, width/2 + 5), (-length/2, width/2))
            l3 = Line(arc@1, (-length/2, -width/2))
        make_face()
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), top_fillet_radius)

pocket = Pos(-length/2 + pocket_length/2, -width/2 + pocket_width/2, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

nx = int(length / vent_spacing)
ny = int(width / vent_spacing)
for i in range(nx):
    for j in range(ny):
        x = (i - (nx-1)/2) * vent_spacing
        y = (j - (ny-1)/2) * vent_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(vent_diameter/2, height)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, height/2) * Cylinder(mount_hole_diameter/2, height)

part = solid_body
part.name = "vented_box_with_pocket"
export_step(part, "output.step")