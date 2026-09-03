from build123d import *
import math

plate_width = 70.0
plate_height = 40.0
plate_thickness = 8.0
oval_width = 30.0
oval_height = 15.0
oval_depth = 4.0
hole_diameter = 5.0
csk_diameter = 8.5
csk_angle = 82.0
hole_spacing = 47.0
hole_offset_y = -plate_height/2 + 10.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 2.0
chamfer_size = 0.5

with BuildPart() as p:
    Box(plate_width, plate_height, plate_thickness)
solid = p.part
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as oval_p:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as oval_sk:
        Ellipse(oval_width/2, oval_height/2)
    extrude(amount=-oval_depth)
solid = solid - oval_p.part

csk_depth = (csk_diameter/2 - hole_diameter/2) / math.tan(math.radians(csk_angle/2))
shaft_depth = plate_thickness - csk_depth
csk_cone = Pos(0, 0, -csk_depth/2) * Cone(hole_diameter/2, csk_diameter/2, csk_depth)
shaft_cyl = Pos(0, 0, -csk_depth - shaft_depth/2) * Cylinder(hole_diameter/2, shaft_depth)
csk_hole = csk_cone + shaft_cyl

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y), (0, plate_height/2 - 10)]:
    solid = solid - Pos(x, y, plate_thickness/2) * csk_hole

rib = Pos(0, 0, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid = solid + rib

part = solid
part.name = "plate_with_oval_pocket_and_rib"
export_step(part, "output.step")