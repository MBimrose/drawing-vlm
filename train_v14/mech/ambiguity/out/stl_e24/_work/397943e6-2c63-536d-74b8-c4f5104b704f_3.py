from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
corner_fillet_radius = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 6.0
hole_diameter = 3.5
countersink_diameter = 5.5
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 4
rib_thickness = 4.0
rib_width = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

csink_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
shaft = Pos(0, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
csink = Pos(0, 0, plate_thickness - csink_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csink_depth)
hole_tool = shaft + csink

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * hole_tool

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x + hole_spacing_x/2
        y = (j - (hole_rows-1)/2) * hole_spacing_y + hole_spacing_y/2
        solid_body = solid_body - Pos(x, y, 0) * hole_tool

rib1 = Pos(plate_length/2 + rib_thickness/2, 0, plate_thickness/2) * Box(rib_thickness, rib_width, plate_thickness)
rib2 = Pos(-plate_length/2 - rib_thickness/2, 0, plate_thickness/2) * Box(rib_thickness, rib_width, plate_thickness)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")