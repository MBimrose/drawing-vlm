from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 60.0
material_thickness = 8.0
extrusion_width = 20.0
fillet_radius = 0.5
hole_diameter = 5.0
hole_offset = 10.0
gusset = True

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (material_thickness, vertical_leg_length),
                     (material_thickness, material_thickness), (horizontal_leg_length, material_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=extrusion_width)

solid_body = p.part

if gusset:
    with BuildPart() as g:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((0, vertical_leg_length), (material_thickness, vertical_leg_length),
                         (material_thickness, vertical_leg_length - material_thickness), close=True)
            make_face()
        extrude(amount=extrusion_width)
    solid_body = solid_body + g.part

solid_body = solid_body - Pos(hole_offset, vertical_leg_length/2, extrusion_width/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, vertical_leg_length + 10)
solid_body = solid_body - Pos(horizontal_leg_length/2, hole_offset, extrusion_width/2) * Rot(0, -90, 0) * Cylinder(hole_diameter/2, horizontal_leg_length + 10)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")