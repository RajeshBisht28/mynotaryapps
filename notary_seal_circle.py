import cairo
import math
import os
import sys
import random
import json
import logging

class LeafletNotarySeal:
    def __init__(self):
        pass

    def draw_curved_text(self, ctx, text, center_x, center_y, radius, start_angle_deg, clockwise=True, font_size=12, font_family="Times New Roman", font_weight=cairo.FONT_WEIGHT_NORMAL, text_direction="outward"):
        """
        Draws text along an arc.

        :param ctx: Cairo context.
        :param text: The string to draw.
        :param center_x, center_y: Center of the circle.
        :param radius: Radius of the arc the text follows (baseline of the text).
        :param start_angle_deg: The angle (in degrees) where the text block is centered.
                                0 degrees is right, 90 degrees is top.
        :param clockwise: True for clockwise flow, False for anti-clockwise.
        :param font_size: Font size.
        :param font_family: Font family (e.g., "Times New Roman").
        :param font_weight: Font weight (e.g., cairo.FONT_WEIGHT_NORMAL, cairo.FONT_WEIGHT_BOLD).
        :param text_direction: "outward" (text outside arc, top of chars point outward)
                            or "inward" (text inside arc, top of chars point inward).
        """
        ctx.set_font_size(font_size)
        ctx.select_font_face(font_family, cairo.FONT_SLANT_NORMAL, font_weight)
        ctx.set_source_rgb(0, 0, 0) # Black color for text

        # Calculate total text width on the baseline
        total_text_width = 0
        for char in text:
            extents = ctx.text_extents(char)
            total_text_width += extents.x_advance
        
        # Calculate the total angle span for the text
        total_angular_span = total_text_width / radius
        
        # Convert start_angle_deg to radians
        start_angle_rad = math.radians(start_angle_deg)
        
        ctx.save()
        ctx.translate(center_x, center_y)

        # Initial rotation to position the starting point of the text arc
        # This centers the entire text block around start_angle_rad
        if clockwise:
            ctx.rotate(start_angle_rad - total_angular_span / 2)
        else: # Anti-clockwise
            ctx.rotate(start_angle_rad + total_angular_span / 2)

        for char in text:
            extents = ctx.text_extents(char)
            char_width = extents.x_advance
            
            # Calculate angle for this character based on its width
            char_angle_increment = char_width / radius
            
            if clockwise:
                ctx.rotate(char_angle_increment / 2) # Rotate to the center of the character
            else: # Anti-clockwise
                ctx.rotate(-char_angle_increment / 2) # Rotate to the center of the character (negatively)

            ctx.save()
            # Move to the position on the radius for the character's baseline
            ctx.translate(radius, 0)
            
            # Rotate character upright relative to tangent based on text_direction
            if text_direction == "outward":
                ctx.rotate(math.pi / 2) # Characters point away from center
            else: # "inward"
                ctx.rotate(-math.pi / 2) # Characters point towards center

            # Move back by half the character's width to center it visually
            ctx.move_to(-extents.width / 2, 0)

            ctx.show_text(char)
            ctx.restore() # Restore after showing char
            
            if clockwise:
                ctx.rotate(char_angle_increment / 2) # Rotate past the character to the next start point
            else: # Anti-clockwise
                ctx.rotate(-char_angle_increment / 2) # Rotate past the character to the next start point
                
        ctx.restore()

    def generate_notary_seal(self, upper_circle_text, lower_circle_text, notaryId, expireOn,  output_filename):
        """
        Generates an e-notary seal image based on the latest feedback:
        - Reduced gap between outer and inner circles.
        - "NOTARY" and "PUBLIC" placed inside the innermost circle.
        - Increased border density (line width).
        """
        WIDTH, HEIGHT = 500, 500 # Image dimensions
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        ctx = cairo.Context(surface)
        ctx.set_antialias(cairo.ANTIALIAS_BEST)
        ctx.set_line_width(3)     
        center_x, center_y = WIDTH / 2, HEIGHT / 2
        outermost_circle_radius = 140
        innermost_circle_radius = 70 
        outer_text_radius_baseline = (outermost_circle_radius + innermost_circle_radius) / 2 
        inner_text_radius_baseline = innermost_circle_radius -25 
        ctx.set_source_rgb(0, 0, 0) # Black color for lines
        # Outermost circle
        ctx.arc(center_x, center_y, outermost_circle_radius, 0, 2 * math.pi)
        ctx.stroke()
        # Innermost circle
        ctx.arc(center_x, center_y, innermost_circle_radius, 0, 2 * math.pi)
        ctx.stroke()
        
        self.draw_curved_text(ctx, upper_circle_text, center_x, center_y, 
                        outer_text_radius_baseline-10, 270, True, 22, 
                        "Times New Roman", cairo.FONT_WEIGHT_NORMAL, "outward")

        # "STATE OF YOUR STATE" (anti-clockwise, bottom half, centered at 270 degrees)
        self.draw_curved_text(ctx, lower_circle_text, center_x, center_y, 
                        outer_text_radius_baseline+10, 90, False, 22, 
                        "Times New Roman", cairo.FONT_WEIGHT_NORMAL, "inward")

        self.draw_curved_text(ctx, "NOTARY", center_x, center_y, 
                        inner_text_radius_baseline, 270, True, 16, # Reduced font size to fit
                        "Times New Roman", cairo.FONT_WEIGHT_BOLD, "outward")

        # "PUBLIC" (anti-clockwise, bottom half, centered at 270 degrees, bold)
        self.draw_curved_text(ctx, "PUBLIC", center_x, center_y, 
                        inner_text_radius_baseline+10, 90, False, 16, # Reduced font size to fit
                        "Times New Roman", cairo.FONT_WEIGHT_BOLD, "inward")

        # --- Draw Horizontal Text in the Center ---
        ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14) # Smaller font for horizontal text
        ctx.set_source_rgb(0, 0, 0) # Black

        text1 = f"Expires: {expireOn}"
        text2 = f"Notary ID: {notaryId}"

        extents1 = ctx.text_extents(text1)
        extents2 = ctx.text_extents(text2)
        line_spacing = 5    
        text_block_height = extents1.height + extents2.height + line_spacing
        first_line_baseline_y = center_y - text_block_height / 2 + extents1.height

        ctx.move_to(center_x - extents1.width / 2, first_line_baseline_y)
        ctx.show_text(text1)

        ctx.move_to(center_x - extents2.width / 2, first_line_baseline_y + extents1.height + line_spacing)
        ctx.show_text(text2)
        surface.write_to_png(output_filename)
    
    def load_json_data(self, json_data):
        try:
            return json.loads(json_data)
        except Exception as e:
            return str(e)
            
    def mainprocess(self, logger, jsonStr):
        logger.debug(f"Notary Seal mainprocess jsonStr : {jsonStr}")
        data = {}
        output_filename = ""
        try:
            data = self.load_json_data(jsonStr)            
            output_filename = data.get('outFile')
            upper_circle_text = data.get('upperCircleText')
            lower_circle_text = data.get('lowerCircleText')
            notaryId = data.get('notaryId')
            expireOn = data.get('expireOn')
            self.generate_notary_seal(upper_circle_text, lower_circle_text, notaryId, expireOn, output_filename)            
            data['status'] = True 
        except Exception as e:
            data['message'] = str(e)
            data['outFile'] = output_filename
            data['status'] = False

        return data
       
       

if __name__ == "__main__":
    arguments = sys.argv
    jsonStr = arguments[1]
    #jsonpath = r'C:\Users\leaflet_javaVB_delhi\Workspace\rajeshbisht\pythonTesting\stamp_outcomes\notary_seal.json'
    clobj = LeafletNotarySeal()
    response = clobj.mainprocess(jsonStr)
    #print(f"{response}")
    #print("Notary seal 'notary_seal_revised.png' generated successfully with updated layout!")
