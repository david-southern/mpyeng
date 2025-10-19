include <BOSL2/std.scad>
use <lazy.scad>

Flip = true;

pixel_grid_size = 5;
pixel_cell_size = 5.3;
pixel_cell_depth = 1.7;
bend_bars_inset = 0.4;
bend_bar_height = 2.25;

card_tray_width = 90;
card_tray_height = 120;
card_tray_thickness = 3;
card_rim_thickness = 9;
card_wall_width = 7;
card_waist_height = 70;

magnet_diameter = 8;
magnet_hole_diameter = magnet_diameter + 0.2;
magnet_base_thickness = 0.4;

$fn = 83;

// Customizer limit module
module __Customizer_Limit__ () {}

intra_pixel_spacing = 11.5;
bend_allowance = 1;
pixel_cell_spacing = pixel_cell_size + intra_pixel_spacing - bend_bar_height * 2;
// Bar width calc here assumes a 90 degree bend, strip should have a touch of slack since it will be
// crossing the hypotenuse of the triangle formed by the bend
bend_bar_width = intra_pixel_spacing - bend_bar_height * 2 - bend_allowance * 2;

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
Debug = false;

ry(Flip ? 180 : 0)
{
    difference()
    {
        card_tray();
        // tz(pixel_cell_depth)
        // ry(180)
        // {
        //     bend_bars();
        // }
    }
}

// right(100)
// down(pixel_cell_depth - bend_bars_inset)
// bend_bars();

module card_tray()
{
    if(Debug) {
        echo(card_height = card_height);
        echo(card_waist_height = card_waist_height);
        echo(card_waist_start = card_waist_start);
        echo(card_width = card_width);
    }

    difference()
    {
        tx(-card_tray_width/2)
        ty(-card_tray_height/2)
        {
            difference()
            {
                // Outer tray
                color("lightgrey")
                card_outer_tray();

                // Inner tray
                tz(-epsilon)
                scale([1, 1, 10]) card_inner_tray();
                tz(card_tray_thickness)
                scale([1, 1, 10]) card_waist();
            }
            card_inner_tray();
        }

        // Magnet holes
        # ty(card_wall_width / 2)
        tz(card_tray_thickness / 2 + magnet_base_thickness)
        xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        cylinder(h=card_tray_thickness, d=magnet_hole_diameter, center=true);

        scale([1, 1, 10])
        pixel_grid();
    }
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

module card_outer_tray()
{
    linear_extrude(height=card_rim_thickness)
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
    xcopies(pixel_cell_spacing, pixel_grid_size)
    {
        ycopies(pixel_cell_spacing, pixel_grid_size)
        {
            cube([pixel_cell_size, pixel_cell_size, pixel_cell_depth], center=true);
        }
    }
}

module pixel_support_punchout()
{
    // cube([
    //     pixel_cell_spacing * pixel_grid_size + strip_width, 
    //     pixel_cell_spacing * pixel_grid_size + strip_width, 
    //     pixel_cell_depth
    // ], anchor = BOTTOM);
    cube([
        card_tray_x_3 - card_tray_x_2, 
        card_tray_x_3 - card_tray_x_2, 
        pixel_cell_depth
    ], anchor = BOTTOM);
}

module pixel_support(){
        union()
        {
            difference()
            {
                cube([pixel_cell_spacing * pixel_grid_size, pixel_cell_spacing * pixel_grid_size, pixel_cell_depth], anchor = BOTTOM);
                scale([1, 1, 10])
                pixel_grid();
            }

            difference()
            {
                pixel_support_punchout();
                tz(-epsilon)
                cube([
                    pixel_cell_spacing * pixel_grid_size, 
                    pixel_cell_spacing * pixel_grid_size, 
                    pixel_cell_depth * 10
                ], anchor = BOTTOM);
            }

            // bend_bars();
        }
}

module bend_bars()
{
    tz(pixel_cell_depth - bend_bars_inset)
    color("lightblue")
    difference()
    {
        union()
        {
            ycopies(pixel_cell_spacing, pixel_grid_size + 1)
            cube([
                pixel_cell_spacing * pixel_grid_size + strip_width, 
                bend_bar_width,
                bend_bar_height + strip_seg_thickness / 2 + bend_bars_inset
            ], anchor = BOTTOM);

            xcopies(pixel_cell_spacing * pixel_grid_size + strip_width - bend_bar_width, 2)
            cube([
                bend_bar_width,
                pixel_cell_spacing * pixel_grid_size + strip_width, 
                bend_bar_height + strip_seg_thickness / 2 + bend_bars_inset
            ], anchor = BOTTOM);
        }

        tz(bend_bars_inset)
        ycopies(pixel_cell_spacing, pixel_grid_size)
        pixel_lock_bar();

        tz(-bend_bars_inset * 3.25)
        strips(strip_width);
    }
}

module pixel_lock_bar()
{
    color("blue")
    cube([
        pixel_cell_spacing * pixel_grid_size + strip_width + epsilon, 
        pixel_cell_size,
        bend_bar_height * 2
    ], anchor = BOTTOM);
}

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