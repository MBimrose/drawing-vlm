from build123d import *

hub_radius = 10.0
hub_height = 10.0
blade_height = 70.0
blade_chord = 30.0
blade_thickness = 5.0
root_fillet_radius = 2.0
tip_chamfer = 0.5
hole_diameter = 4.0
hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(hub_radius)
    extrude(amount=hub_height)
    with BuildSketch(Plane.XY.offset(hub_height)) as s2:
        Ellipse(blade_chord/2, blade_thickness)
    with BuildSketch(Plane.XY.offset(hub_height + blade_height/2)) as s3:
        Ellipse(blade_chord/4, blade_thickness/2)
    with BuildSketch(Plane.XY.offset(blade_height)) as s4:
        Ellipse(blade_chord/8, blade_thickness/4)
    loft()

solid_body = p.part
solid_body = solid_body - Pos(hole_offset, 0, blade_height/2) * Cylinder(hole_diameter/2, blade_height + 10)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), tip_chamfer)

part = solid_body
part.name = "blade_hub"
export_step(part, "output.step")