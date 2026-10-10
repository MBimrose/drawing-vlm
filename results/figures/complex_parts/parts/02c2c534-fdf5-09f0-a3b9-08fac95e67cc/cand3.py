from build123d import *

hub_radius = 10.0
hub_length = 10.0
blade_root_chord = 20.0
blade_tip_chord = 5.0
blade_thickness_root = 8.0
blade_thickness_tip = 3.0
blade_span = 60.0
num_sections = 6
section_height = blade_span / (num_sections - 1)
shaft_hole_diameter = 4.0

hub = Pos(0, 0, hub_length / 2) * Cylinder(hub_radius, hub_length)

with BuildPart() as bp:
    for i in range(num_sections):
        z = hub_length + i * section_height
        chord = blade_root_chord + (blade_tip_chord - blade_root_chord) * (i / (num_sections - 1))
        thickness = blade_thickness_root + (blade_thickness_tip - blade_thickness_root) * (i / (num_sections - 1))
        with BuildSketch(Plane.XY.offset(z)) as sk:
            with BuildLine() as bl:
                Spline((0, 0), (chord * 0.25, thickness * 0.5), (chord * 0.75, thickness * 0.5), (chord, 0))
                Line((chord, 0), (0, 0))
            make_face()
    loft()

blade = bp.part
result = hub + blade
result = result - Cylinder(shaft_hole_diameter / 2, 200)
result = split(result, Plane.YZ)

part = result
part.name = "impeller_half"
export_step(part, "output.step")