from build123d import *

horizontal_leg_length = 80.0
vertical_leg_height = 70.0
plate_thickness = 6.0
bracket_depth = 6.0
rib_thickness = 4.0
rib_height = 40.0
rib_extension = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
hole_spacing_horizontal = 20.0
hole_spacing_vertical = 25.0
hole_offset_from_corner = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, plate_thickness),
                     (plate_thickness, plate_thickness), (plate_thickness, vertical_leg_height),
                     (0, vertical_leg_height), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ) as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((plate_thickness, 0), (plate_thickness + rib_extension, 0),
                     (plate_thickness, rib_height), close=True)
        make_face()
    extrude(amount=rib_thickness)

solid_body = solid_body + rib_p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing_horizontal
    y = plate_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_depth - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth + 10)

for i in range(2):
    x = plate_thickness / 2
    y = hole_offset_from_corner + i * hole_spacing_vertical
    solid_body = solid_body - Pos(x, y, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth + 10)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")