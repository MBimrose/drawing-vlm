from build123d import *

# ---- dimensions (mm) ----
overall_width = 80.0            # flange width
overall_height = 29.3           # overall height (flange top to web bottom)
extrude_depth = 30.8            # part length
flange_thickness = 4.0          # flange plate thickness
web_width = 25.0                # web width
web_radius = 13.0               # web bottom radius
hole_diameter = 18.5            # through hole diameter
hole_center_y = 13.0            # hole center above web bottom
fillet_radius = 3.9             # fillet at flange-to-web transition

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            # flat top flange
            Line((-overall_width / 2, overall_height), (overall_width / 2, overall_height))
            Line((overall_width / 2, overall_height), (overall_width / 2, overall_height - flange_thickness))
            # right flange underside -> web
            Line((overall_width / 2, overall_height - flange_thickness), (web_width / 2, overall_height - flange_thickness))
            Line((web_width / 2, overall_height - flange_thickness), (web_width / 2, web_radius))
            # rounded web bottom
            ThreePointArc((web_width / 2, web_radius), (0.0, 0.0), (-web_width / 2, web_radius))
            # left web -> flange underside
            Line((-web_width / 2, web_radius), (-web_width / 2, overall_height - flange_thickness))
            Line((-web_width / 2, overall_height - flange_thickness), (-overall_width / 2, overall_height - flange_thickness))
            # left flange edge up to top
            Line((-overall_width / 2, overall_height - flange_thickness), (-overall_width / 2, overall_height))
        make_face()
    extrude(amount=extrude_depth)

    # fillet the two flange-to-web transition corners (vertical edges at web sides)
    transition_edges = [
        e for e in p.edges().filter_by(Axis.Z)
        if abs(abs(e.center().X) - web_width / 2) < 0.5
    ]
    fillet(transition_edges, fillet_radius)

    # single through hole in the web
    with Locations((0.0, hole_center_y, extrude_depth / 2)):
        Cylinder(hole_diameter / 2, extrude_depth, mode=Mode.SUBTRACT)

part = p.part
part.name = "t_profile_with_hole"
export_step(part, "output.step")