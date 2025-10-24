include <BOSL2/std.scad>
use <lazy.scad>

printer_fudge = 0.15;

board_thickness = 5;
wire_26ga_outer_diameter = 1.6;

pixel_grid_size = 5;
pixel_cell_size = 5 + printer_fudge * 2;
pixel_cell_depth = 1.7;
bend_bars_inset = 0.4;
bend_bar_height = 2.25;

lock_bar_height = 3;

card_tray_width = 90;
card_tray_height = 120;
card_tray_thickness = 3;
card_rim_thickness = 9;
card_wall_width = 7;
card_waist_height = 70;

magnet_height = 3;
magnet_diameter = 8;
magnet_hole_diameter = magnet_diameter + printer_fudge * 2;
inset_piece_depth = 0.4;

lock_sphere_diameter = 2;
lock_bar_width = card_tray_width - card_wall_width * 2;

Flip = false;
Suppress_Da_Mess = true;
Debug = false;

$fn = 43;

// Customizer limit module
module __Customizer_Limit__ () {}

intra_pixel_spacing = 11.5;
bend_allowance = 1;
pixel_cell_spacing = pixel_cell_size + intra_pixel_spacing - bend_bar_height * 2;

strip_width = 10;
strip_separator_width = pixel_cell_spacing - strip_width - bend_allowance * 2;
strip_pin_width = 1.7;
strip_pin_spacing = 3;

echo(str("Pixel Cell Spacing: ", pixel_cell_spacing));

card_height = card_tray_height - card_wall_width;
card_width = card_tray_width - card_wall_width * 2;
card_waist_start = (card_height - card_waist_height - card_wall_width * 2) / 2;

card_tray_x_0 = 0; 
card_tray_x_1 = card_wall_width;
card_tray_x_2 = card_wall_width * 2;
card_tray_x_3 = card_tray_width - card_wall_width * 2;
card_tray_x_4 = card_tray_width - card_wall_width;
card_tray_x_5 = card_tray_width;

card_tray_y_0 = 0;
card_tray_y_1 = card_wall_width;
card_tray_y_2 = card_wall_width + card_waist_start;
card_tray_y_3 = card_wall_width + card_waist_start + card_wall_width;
card_tray_y_4 = card_wall_width + card_waist_start + card_wall_width + card_waist_height;
card_tray_y_5 = card_wall_width + card_waist_start + card_wall_width + card_waist_height + card_wall_width;
card_tray_y_6 = card_tray_height;

epsilon = 0.01; // Small value to ensure proper subtraction

wire_run("red", [[0,0,0], [10,0,0], [10,10,0], [20,10,0]]);

module wire_run(wire_color, wire_path, wire_diameter = wire_26ga_outer_diameter)
{
    if(len(wire_path) < 2)
    {
        echo("wire_run: Path must have at least two points");
    } else {
        color(wire_color)
        {
            sphere(d=wire_diameter);
            for(i = [0 : len(wire_path) - 2]) {
                echo(str("Wire Segment ", i, ": ", wire_path[i], " to ", wire_path[i+1]));
                extrude_from_to(wire_path[i], wire_path[i+1], convexity=4, twist=0, scale=1.0, slices=8)
                    circle(d=wire_diameter);
                translate(wire_path[i+1])
                sphere(d=wire_diameter);
            }
        }
    }
}

* ry(Flip ? 180 : 0)
{
    card_tray();

    wiring_inset();

    if(!Suppress_Da_Mess)
    {
        lock_bar_assy();

        tx(card_tray_width)
        tz(lock_bar_height)
        rz(90)
        lock_bars();
    }
}

module wiring_inset()
{
    xcopies(intra_pixel_spacing, pixel_grid_size)
    {
        color("darkgray")
        cube([strip_width, pixel_cell_spacing * pixel_grid_size + epsilon, 0.4], anchor=TOP);

        color("orange")
        xcopies(strip_pin_spacing, 3)
        cube([strip_pin_width, pixel_cell_spacing * pixel_grid_size + epsilon, 0.6], anchor=TOP);
    }

}

module card_tray()
{
    difference()
    {
        tx(-card_tray_width/2)
        ty(-card_tray_height/2)
        {
            difference()
            {
                card_outer_tray(card_tray_thickness);

                // Inner tray
                tz(-epsilon)
                scale([1, 1, 10]) card_inner_tray();
                tz(card_tray_thickness)
                scale([1, 1, 10]) card_waist();
            }
            card_inner_tray();
        }

        // Magnet holes
        ty(card_wall_width / 2)
        tz(card_tray_thickness - inset_piece_depth)
        xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        cylinder(h=magnet_height, d=magnet_hole_diameter, anchor = BOTTOM);

        pixel_grid();
    }

    // Board Support Posts
    ty(card_wall_width / 2)
    tz(-epsilon)
    xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
    ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
    cylinder(h=board_thickness, d=magnet_hole_diameter, anchor = TOP);

}

module card_waist()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_0, card_tray_y_3],
        [card_tray_x_5, card_tray_y_3],
        [card_tray_x_5, card_tray_y_4],
        [card_tray_x_0, card_tray_y_4]
    ]);
}

module card_inner_tray()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_1, card_tray_y_1],
        [card_tray_x_4, card_tray_y_1],
        [card_tray_x_4, card_tray_y_2],
        [card_tray_x_3, card_tray_y_3],
        [card_tray_x_3, card_tray_y_4],
        [card_tray_x_4, card_tray_y_5],
        [card_tray_x_4, card_tray_y_6],
        [card_tray_x_1, card_tray_y_6],
        [card_tray_x_1, card_tray_y_5],
        [card_tray_x_2, card_tray_y_4],
        [card_tray_x_2, card_tray_y_3],
        [card_tray_x_1, card_tray_y_2]
    ]);
}

module card_outer_tray(tray_depth = card_rim_thickness)
{
    linear_extrude(height=tray_depth)
    polygon([
        [card_tray_x_0, card_tray_y_0],
        [card_tray_x_2, card_tray_y_0],
        [card_tray_x_2, card_tray_y_1],
        [card_tray_x_3, card_tray_y_1],
        [card_tray_x_3, card_tray_y_0],
        [card_tray_x_5, card_tray_y_0],
        [card_tray_x_5, card_tray_y_2],
        [card_tray_x_4, card_tray_y_3],
        [card_tray_x_4, card_tray_y_4],
        [card_tray_x_5, card_tray_y_5],
        [card_tray_x_5, card_tray_y_6],
        [card_tray_x_0, card_tray_y_6],
        [card_tray_x_0, card_tray_y_5],
        [card_tray_x_1, card_tray_y_4],
        [card_tray_x_1, card_tray_y_3],
        [card_tray_x_0, card_tray_y_2]
    ]);
}

module pixel_grid() {
    color("pink")
    tz(-epsilon)
    xcopies(pixel_cell_spacing, pixel_grid_size)
    {
        ycopies(pixel_cell_spacing, pixel_grid_size)
        {
            cube([pixel_cell_size, pixel_cell_size, card_tray_thickness * 2], anchor=BOTTOM);
        }
    }
}

module lock_bar_assy()
{
    difference()
    {
        // Grid Base
        cube([
            lock_bar_width, 
            pixel_cell_spacing * pixel_grid_size + epsilon, 
            lock_bar_height + epsilon
        ], anchor=TOP);

        lock_bars();

        color("blue")
        ycopies(pixel_cell_spacing, pixel_grid_size)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size + bend_allowance * 4,
            lock_bar_height + epsilon
        ], anchor = TOP);

        color("red")
        tz(-bend_bar_height)
        xcopies(pixel_cell_spacing, pixel_grid_size)
        cube([
            strip_width + printer_fudge * 4,
            pixel_cell_spacing * pixel_grid_size + epsilon,
            lock_bar_height + epsilon
        ], anchor = TOP);

        color("magenta")
        ycopies(pixel_cell_spacing * pixel_grid_size, 2)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size + bend_allowance * 4,
            lock_bar_height + epsilon
        ], anchor = TOP);
    }
}

module lock_bars()
{
    ycopies(pixel_cell_spacing, pixel_grid_size)
    lock_bar();
}

module lock_bar()
{
    color("green")
    {
        cube([
            lock_bar_width,
            pixel_cell_size,
            (lock_bar_height + epsilon)
        ], anchor = TOP);
        
        tz(-lock_bar_height / 2)
        ycopies(pixel_cell_size, 2)
        xcopies(lock_bar_width - pixel_cell_size, 2)
        sphere(d=lock_sphere_diameter);
    }

}

// Bar width calc here assumes a 90 degree bend, strip should have a touch of slack since it will be
// crossing the hypotenuse of the triangle formed by the bend
bend_bar_width = intra_pixel_spacing - bend_bar_height * 2 - bend_allowance * 2;
strip_seg_length = pixel_cell_size + bend_allowance * 2 + bend_bar_width;
strip_seg_thickness = 1;

module strips(seg_width = strip_width)
{
    xcopies(pixel_cell_spacing, pixel_grid_size)
    translate([
        -seg_width / 2,
        -pixel_cell_size / 2 - bend_allowance,
        pixel_cell_depth + strip_seg_thickness / 2
    ])
    ycopies(strip_seg_length, 7)
    strip_segment(seg_width);
}

module strip_segment(seg_width = strip_width)
{
    bent_path = [
        [0, 0], 
        [0 + pixel_cell_size, 0], 
        [0 + pixel_cell_size + bend_allowance / 2, bend_bar_height], 
        [0 + pixel_cell_size + bend_allowance / 2 + bend_bar_width, bend_bar_height], 
        [0 + pixel_cell_size + bend_allowance + bend_bar_width, 0], 
    ];

    path = [
        [0, bend_bar_height],
        [bend_allowance, 0], 
        [bend_allowance + pixel_cell_size, 0],
        [bend_allowance + pixel_cell_size + bend_allowance, bend_bar_height], 
        [bend_allowance + pixel_cell_size + bend_allowance + bend_bar_width, bend_bar_height], 
    ];

    color("red")
    rx(90)
    ry(90)
    linear_extrude(height=seg_width)
    stroke(path, width=strip_seg_thickness);
}