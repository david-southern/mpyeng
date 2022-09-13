include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <BOSL/paths.scad>
use <BOSL/metric_screws.scad>

include <polyround.scad>

$fn = 43;

difference_fudge = 0.01;
extrusion_fudge = 0.1;
wall_thickness = 2;

display_width = 50.6;
display_height = 19.1;
display_depth = 8;
display_x_offset = 6.5;

wire_x_offset_start = 12;
wire_x_offset_end = 4.5;
wire_height = 13;

board_width = 66.5;
board_height = 27;
board_depth = 1.6;

corner_radius = 1;

profile_height = 6;
profile_base_width = 12;
profile_top_width = 5;
profile_tight_corner = 1;
profile_wide_corner = 2;

support_depth = board_depth * 2.5 + wall_thickness;
metric_screw_size = 3;
screw_spread = display_height + profile_base_width * 1.25;

// To make the rim printable:
// Set build_blank to true
// render and export the rim blank
// Import the blank into 3D Builder - it will offer to fix the object
// when the object is fixed, reposition it to x = 0, y = 0, settled
// Save as rim_blank_fixed.stl
// Set build_blank to false and re-render
build_blank = false;
printable();

module printable()
{
    if(build_blank)
    {
        rim(display_width + 1.25, display_height + 2);
    } else {
        top_half(z = wall_thickness + board_depth + difference_fudge)
        difference()
        {
            import("rim_blank_fixed.stl");
            translate([0, 0, board_depth + wall_thickness])
            base_plate();
            
            translate([0, 0, 
                board_depth + wall_thickness
            ])
            yspread(n=2, l=screw_spread)
            screw(screwsize=metric_screw_size, screwlen=15,
                headsize=get_metric_socket_cap_diam(metric_screw_size), 
                headlen=get_metric_socket_cap_height(metric_screw_size) * 1.25
            );
        }
        
        translate([0, 100, 0])
        bottom_half(z = wall_thickness + board_depth - difference_fudge)
        difference()
        {
            import("rim_blank_fixed.stl");
            translate([0, 0, board_depth + wall_thickness])
            display();
            
            translate([0, 0, 
                board_depth + wall_thickness
            ])
            yspread(n=2, l=screw_spread)
            screw(screwsize=metric_screw_size, screwlen=15,
                headsize=get_metric_socket_cap_diam(metric_screw_size), 
                headlen=get_metric_socket_cap_height(metric_screw_size)
            );
        }
    }
}

module rim(inner_width, inner_height) {
    rim_points=[
        [0, -inner_height/2, 0],
        [-inner_width / 2, -inner_height / 2,  corner_radius],
        [-inner_width / 2,  inner_height / 2,  corner_radius],
        [ inner_width / 2,  inner_height / 2,  corner_radius],
        [ inner_width / 2, -inner_height / 2,  corner_radius],
        [0, -inner_height/2, 0],
    ];
    
    // polygon(polyRound(rim_points,5));

    rail = [ for (i = polyRound(rim_points, 23)) [ i.x, i.y, 0] ]; ;

    shape_points=[
        [0, -support_depth, 0],
        [0, profile_height, profile_tight_corner],
        [profile_top_width, profile_height, profile_wide_corner],
        [profile_base_width, 0, profile_wide_corner],
        [profile_base_width, -support_depth, profile_tight_corner]
    ];
    // echo(shape_points=shape_points);

    shape = polyRound(shape_points, 5);
    

    // polygon(shape);
    extrude_2dpath_along_3dpath(shape, rail, ang=-90);
}

module base_plate()
{
    translate([-display_width / 2 + board_width / 2 - display_x_offset, 0, 0])
    {
        color("green")
        translate([0, 0, -board_depth / 2])
        cuboid([board_width, board_height, board_depth]);
    }
}

module display()
{
    color("silver")
    translate([
        0, 
        0, 
        display_depth / 2])
    cuboid([display_width, display_height, display_depth]);

    base_plate();
    
    translate([-display_width / 2 + board_width / 2 - display_x_offset, 0, 0])
    {
        wire_width = wire_x_offset_start - wire_x_offset_end;
        wire_depth = board_depth * 5;
        
        color("red")
        translate([
            board_width / 2 - wire_width / 2 - wire_x_offset_end, 
            0, 
            -wire_depth / 2 + board_depth])
        cuboid([wire_width, wire_height, wire_depth]);
    }
}
