include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <lazy.scad>
use <rounded_collar.scad>

$fn = 67;

// Render/view settings
laser_cut = false;

cutaway_view = false;
show_card = false;
show_card_contacts = false;
show_lighting = false;
show_support_board = false;

// Printer settings
difference_fudge = 0.01;
extrusion_fudge = 0.1;
print_layer_height = 0.15;

// Default minimum thickness of any wall
wall_thickness = 2;

// Thickness of the engineering board support plate.
support_board_thickness = (3/16) * 25.4;

// Thickness of the card acrylic
// acrylic_thickness = 3.25;
acrylic_thickness = 6.2;

// Card dimensions
card_width = 54;
card_height = 81;
card_thickness = acrylic_thickness; // Allow thickness to be variable in case we add any 'decorations' around the card
card_corner_fillet = 2;

// Lighting dimensions
LED_strip_width = 12;
LED_strip_height = 1;
LED_width = 5.2;
LED_height = 2;
// What is the minimum length at which that the physical strip may be cut?
LED_unit_length = 7;
// How much space at each end of the strip do I need to solder the LED wiring?
LED_wiring_allowance = 4;

// If true, the LED strip module will include an acrylic plate to protect the exposed LEDs 
lighting_includes_acrylic = false;
lighting_height = LED_strip_height + LED_height + (lighting_includes_acrylic ? acrylic_thickness : 0);

// The card holder has an open slot in front so the user can see the card.  The slot has a 'flange' on either side so
// that the card doesn't fall out.  This is the width of each of those flanges.
card_support_flange_width = 2;

// The card slot should be just a bit wider than the cards so that the user can slide it in and out of the slot easily
// and quickly.  The card_support_play indicates how much wider than the card the slot should be.
card_support_play = 2;

// This is the front-to-back play at the bottom of the card slot wedge.
card_wedge_play = 1;

card_wedge_width = card_width + card_support_play;

// This is the depth of the bottom of the card slot wedge.  It determines how much front-to-back play there will be when
// the card sits in the slot.
card_wedge_bottom_depth = max(card_thickness + card_wedge_play, LED_width);

// This is the depth of the top of the card slot wedge.  It determines how 'steep' the slot wedge should be
// - how far forward will the card lean when sitting in the slot.  If the top depth is the same as the bottom depths,
//   the slot will be perfectly straight.
card_wedge_top_depth = card_wedge_bottom_depth + card_thickness;

front_wall_thickness = 3;
side_wall_thickness = 6;

// Dimensions of the card holder itself
holder_depth = card_wedge_top_depth + front_wall_thickness;
holder_width = card_width + side_wall_thickness * 2 + lighting_height * 2;

// Making the entire height of the holder the same as the card height will cause the card to poke out of the top of the
// holder by the same amount as the card_resting_height. Adjust the holder height up or down to change the 'poke out'.
holder_height = card_height;  
holder_corner_fillet = 3;

// At the bottom of the card we'll have the metal tabs that close the identification circuit.  The card holder will have
// matching contacts to sense the presence of these tabs.
card_contact_count = 5;
total_contact_count = 6; // Include one contact for the ground wire that the contacts close the circuit with

// This design uses steel/aluminum rod for the connectors.  This is the diameter of the rod
card_contact_diam = 6.18;

// How far should the card contact protrude under the card slot flange
card_contact_underlap = holder_depth - card_wedge_bottom_depth - front_wall_thickness;

// How far should the card contact stick out of the back of the engineering board.
card_contact_back_projection = 7;

// How long (front to back) is each contact
card_contact_depth = card_wedge_bottom_depth + card_contact_underlap + support_board_thickness + card_contact_back_projection;

// This is the bottom-most plate that supports the contact assembly
card_contact_support_thickness = 3;

// This is the y-position of the bottom of the card, resting on top of the contacts.
card_resting_height = card_contact_support_thickness + card_contact_diam;

// Calculae how much space should there be between each contact

// Don't include the fillet corners in the width, we only want the card contacts on the flat part of the base of the
// card add an extra bit of fudge so that it's not too hard to apply the contacts to the card
card_contact_width_fudge = 0;
contact_available_width = card_width - (card_corner_fillet * 2) - card_contact_width_fudge;
contact_space_remaining = contact_available_width - (total_contact_count * card_contact_diam);
contact_spacing = contact_space_remaining  / (total_contact_count - 1);
// Make sure that the contacts get a good connection to the card by setting them a bit proud of the wedge base.
contact_proud_height = 0.75;

echo("In this model:");
echo(str("    there are ", total_contact_count, " card contacts"));
echo(str("    the card contacts are ", card_contact_diam, " mm in diameter and ", card_contact_depth, " mm long"));
echo(str("    the card contacts have an exposed chord length of ", 2 * sqrt(pow(card_contact_diam / 2, 2) - pow(card_contact_diam / 2 - contact_proud_height, 2)), " mm"));
echo(str("    the card contacts are spaced ", contact_spacing, " mm apart"));

LED_strip_length = holder_height - card_resting_height - wall_thickness;
LED_bulb_count = floor((LED_strip_length - LED_wiring_allowance * 2) / LED_unit_length);
cut_strip_length = LED_bulb_count * LED_unit_length;
echo(str("    each LED strip (cut to ", cut_strip_length," mm) will have ", LED_bulb_count, " LED bulbs (with an ", LED_wiring_allowance, " mm wiring allowance)"));

mounting_pin_diam = 3;
mounting_pin_projection = 5;
mounting_pin_depth = support_board_thickness + mounting_pin_projection;

if(laser_cut) {
    projection(cut = true)
    tz(holder_depth / 2 - holder_corner_fillet - difference_fudge)
    rx(90)
    difference()
    {
        card_holder();
        ty(-holder_depth)
        {
            card_contacts();
            mounting_pins();
            // The strip is aligned to the back of the holder.  For the laser cut, center it again so that the LED bulbs
            // are included in the laser cut
            ty(LED_strip_width / 2)
            lighting();
        }
    }
}
else {
    if(cutaway_view) {
        cutaway_offset = -5;
        left_half(x = cutaway_offset, s = max(card_width, card_height) * 3)
        {
            // bottom_half(s = max(card_width, card_height) * 3)
            {
                card_holder();
                if(show_card) {
                    card();
                }
                if(show_card_contacts) {
                    card_contacts();    
                }
                if(show_lighting) {
                    lighting(false);
                }
                if(show_support_board) {
                    color("tan")
                    ty(support_board_thickness / 2)
                    cuboid([holder_width * 125, holder_height * 1.25, support_board_thickness]);
                }
            }
        }
    } else {
        card_holder();
        if(show_card) {
            card();
        }
        if(show_card_contacts) {
            card_contacts();    
        }
        if(show_lighting) {
            lighting();
        }
        if(show_support_board) {
            color("tan")
            ty(holder_depth / 2 + support_board_thickness / 2)
            cuboid([holder_width * 1.25, support_board_thickness, holder_height * 1.25]);
        }
    }
}

module card_holder()
{
    difference()
    {
        card_blank();
        tz(difference_fudge) card_contacts();
        if(!laser_cut)
        {
            card_slot();
            card_wedge();
        }

        ty(difference_fudge)
        lighting();
    }
    mounting_pins();
}

module card_blank()
{
    cuboid(
        [
            holder_width,
            holder_depth,
            holder_height
        ], 
        // fillet=holder_corner_fillet,
        chamfer=holder_corner_fillet,
        edges=EDGES_Y_ALL + EDGES_FRONT
    );
}

module mounting_pins()
{
    holder_sides_width = holder_width - card_wedge_width - lighting_height * 2;

    ty(mounting_pin_depth / 2 + holder_depth / 2 - difference_fudge)
    xspread(holder_width - holder_sides_width / 2)
    zspread(holder_height * 0.75)
    ycyl(d=mounting_pin_diam, h = mounting_pin_depth);
}

module card_contacts()
{
    color("silver")
    tyz(
        card_contact_depth / 2 // Align from the front of the contact
            + holder_depth / 2 // line up with the back of the holder
            - card_wedge_bottom_depth // push into the holder the depth of the card wedge bottom
            - card_contact_underlap // push further into the holder under the card slot so that the card contacts don't see-saw out of their slots
        ,
        -holder_height / 2 + card_resting_height // Align to the care resting plane
        - card_contact_diam / 2 // push down so the contacts are in line with the card resting plane
        + contact_proud_height // then push back up just a touch
    )
    {
        if(laser_cut) {
            hull()
            {
                xspread(card_contact_diam + contact_spacing, n=total_contact_count)
                ycyl(d=card_contact_diam + extrusion_fudge * 10, h=card_contact_depth);
            }
        }
        else
        {
            xspread(card_contact_diam + contact_spacing, n=total_contact_count)
            ycyl(d=card_contact_diam + extrusion_fudge, h=card_contact_depth);
        }
    }
}

module card_slot()
{
    // This is the cutout to make the card visible, it is inset from the card edges and the card_resting_height by
    // card_support_flange_width so the card won't fall out
    tz(card_support_flange_width + card_resting_height)
    cuboid([
        card_width - card_support_flange_width * 2, 
        holder_depth * 2, 
        card_height
    ]);
}

module card_wedge()
{
    card_cutout_height = (card_height - card_resting_height) + difference_fudge;

    // Card slot cutout - wedge
    tyz(holder_depth / 2 - card_wedge_bottom_depth / 2 + difference_fudge, 
        card_resting_height - holder_height / 2)
    prismoid(
        size1=[
            card_wedge_width,
            card_wedge_bottom_depth
        ], 
        size2=[
            card_wedge_width,
            card_wedge_top_depth
        ], 
        h=card_cutout_height, 
        shift=[0,  -(card_wedge_top_depth - card_wedge_bottom_depth) / 2]
    );
}

module card()
{
    color("red", 0.25)
    tyz(holder_depth / 2 - card_thickness / 2, card_resting_height)
    cuboid([card_width, card_thickness, card_height],
        fillet=card_corner_fillet,edges=EDGES_Y_ALL
    );
}

module lighting(render_punchouts = true)
{
    led_strip_z_offset = LED_strip_length / 2 - holder_height / 2 + card_resting_height;

    // If true, then align the LED strip with the slope of the wedge slot, rather than the back of the holder
    rotate_led_strip = true;

    if(rotate_led_strip) {
        delta_wedge = card_wedge_top_depth - card_wedge_bottom_depth;
        // Align the front edge of the LED bulbs with the front edge of the wedge.  
        led_depth_offset = card_wedge_bottom_depth - LED_width / 2 + delta_wedge / 2;

        align_angle = atan(delta_wedge / LED_strip_length);
        echo(align_angle = align_angle);
        // Clip off the front 2mm of the strip base so we don't punch through the front of the holder
        intersection()
        {
            tyz(holder_depth / 2 - led_depth_offset, led_strip_z_offset)
            rx(align_angle) lighting_led_strips(true);
            ty(2) cuboid([ holder_width, holder_depth, holder_height ]);
        }

        if(render_punchouts) 
        {
            rotational_punch_fudge = 0.5;

            // Punch out the sides of the card holder behind the LED strip
            tyz(holder_depth / 2 - card_wedge_bottom_depth / 2 + difference_fudge, led_strip_z_offset + rotational_punch_fudge / 2)
            {
                skew_xy(0, -align_angle)
                {
                    tx(-card_wedge_width / 2 - lighting_height / 2 + difference_fudge)
                    cuboid([lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge]);
                    tx(card_wedge_width / 2 + lighting_height / 2 - difference_fudge)
                    cuboid([lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge]);
                }

                tx(-card_wedge_width / 2 - lighting_height / 2 + difference_fudge)
                cuboid([lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge]);
                tx(card_wedge_width / 2 + lighting_height / 2 - difference_fudge)
                cuboid([lighting_height, card_wedge_bottom_depth, LED_strip_length + rotational_punch_fudge]);
            }
        }
    }
    else 
    {
        // Align the center of the LED bulbs with the center of the card, assuming that the card is pressed against the back wall.
        led_depth_offset = max(LED_width / 2, card_wedge_bottom_depth / 2);
        tyz(holder_depth / 2 - led_depth_offset, led_strip_z_offset)
        lighting_led_strips();

        if(render_punchouts) {
            // If the led offset is greater than the led width (i.e. the card is thicker than the LED bulb) then lay in a copy
            // of the strip aligned with the back of the holder, so we don't have a thin strip of "back wall" generated
            if(led_depth_offset > (LED_width / 2)) {
                tyz(holder_depth / 2, led_strip_z_offset)
                lighting_led_strips();
            }
        }
    }
}

module lighting_led_strips(include_strip_base = true)
{
    tx(-card_wedge_width / 2 - lighting_height + difference_fudge)
    ry(90)
    led_strip(include_strip_base);

    tx(card_wedge_width / 2 + lighting_height - difference_fudge)
    ry(-90)
    led_strip(include_strip_base);
}

module led_strip(include_strip_base = true)
{
    if(include_strip_base)
    {
        color("black")
        upcube([LED_strip_length, LED_strip_width, LED_strip_height]);
    }

    color("white")
    translate([0, 0, LED_strip_height])
    upcube([LED_strip_length, LED_width, LED_height]);

    if(lighting_includes_acrylic)
    {
        translate([0, 0, LED_strip_height + LED_height])
        color("#aaaaaa", 0.3)
        upcube([LED_strip_length, LED_strip_width, acrylic_thickness]);
    }
}