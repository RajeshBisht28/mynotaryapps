import cairo
import math
import os
import sys
import random
import json
import logging

class LeafletNotaryStampGeneratorCairo:
    def __init__(self, width=600, height=250):
        self.width = width
        self.height = height
        # Create Cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        self.ctx = cairo.Context(self.surface)
        
        # Set white background
        self.ctx.set_source_rgb(1, 1, 1)  # White background
        self.ctx.paint()
        
        # Set default drawing color to black
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(2)
    
    def draw_rounded_border(self, border_width=3, border_color=(0, 0, 0)):
        """Draw rounded rectangle border around the entire stamp"""
        self.ctx.set_source_rgb(*border_color)
        self.ctx.set_line_width(border_width)
        
        # Draw rounded rectangle
        radius = 5
        x, y = 0, 0
        width, height = self.width, self.height
        
        self.ctx.new_sub_path()
        self.ctx.arc(x + width - radius, y + radius, radius, -math.pi/2, 0)
        self.ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi/2)
        self.ctx.arc(x + radius, y + height - radius, radius, math.pi/2, math.pi)
        self.ctx.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
        self.ctx.close_path()
        self.ctx.stroke()
    
    def draw_star(self, center_x, center_y, outer_radius=25, inner_radius=10, color=(0, 0, 0), width=2):
        """Draw a 5-pointed star"""
        self.ctx.set_source_rgb(*color)
        self.ctx.set_line_width(width)
        
        # Calculate star points
        points = []
        for i in range(10):  # 5 points * 2 (outer and inner)
            angle = math.pi * i / 5
            if i % 2 == 0:  # Outer points
                x = center_x + outer_radius * math.cos(angle - math.pi/2)
                y = center_y + outer_radius * math.sin(angle - math.pi/2)
            else:  # Inner points
                x = center_x + inner_radius * math.cos(angle - math.pi/2)
                y = center_y + inner_radius * math.sin(angle - math.pi/2)
            points.append((x, y))
        
        # Draw star
        self.ctx.move_to(points[0][0], points[0][1])
        for point in points[1:]:
            self.ctx.line_to(point[0], point[1])
        self.ctx.close_path()
        self.ctx.stroke()
    
    def draw_text_on_arc(self, text, center_x, center_y, radius, start_angle, end_angle, 
                         font_size=16, color=(0, 0, 0), upside_down=False, char_spacing=1.5):
        """Draw text along a circular arc with proper spacing to prevent overlap"""
        char_spacing = 1.5  # Default spacing
        print(f"char_spacing: {char_spacing}")
        self.ctx.set_source_rgb(*color)
        self.ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_font_size(font_size)
        
        text = text.upper()
        text_length = len(text)
        
        if text_length == 0:
            return
        
        # Calculate angular spacing based on text length to prevent overlap
        # Use a more conservative approach
        available_angle = math.pi * 0.5 
        if upside_down:
            # Bottom text - limit to bottom semicircle area
            if text_length < 9:
                available_angle = math.pi * 1.5  # 90 degrees max
            elif text_length > 12:            
                available_angle = math.pi * 0.75  # 90 degrees max
            center_angle = math.pi * 1.5  # 270 degrees (bottom center)
            start_pos = center_angle - available_angle / 2
        else:
            # Top text - limit to top semicircle area  
            if text_length < 9:
                available_angle = math.pi * 1.5  # 90 degrees max
            elif text_length > 12:            
                available_angle = math.pi * 0.75  # 90 degrees max
            center_angle = math.pi * 0.5   # 90 degrees (top center)
            start_pos = center_angle + available_angle / 2
        
        # Calculate spacing between characters using char_spacing parameter
        if text_length > 1:
            base_angle_step = available_angle / (text_length - 1)
            angle_step = base_angle_step * char_spacing  # Now actually using char_spacing!
        else:
            angle_step = 0
        
        # Further reduce spacing if text is long to prevent overlap
        if text_length > 8:
            angle_step *= 0.8  # Reduce spacing for long text
        elif text_length > 12:
            angle_step *= 0.6  # Even more reduction for very long text
        
        # Make sure we don't exceed available angle
        total_angle_needed = angle_step * (text_length - 1) if text_length > 1 else 0
        if total_angle_needed > available_angle:
            angle_step = available_angle / (text_length - 1) if text_length > 1 else 0
        
        # Draw each character
        for i, char in enumerate(text):
            if upside_down:
                # Bottom text: move from left to right
                angle = start_pos + i * angle_step
            else:
                # Top text: move from right to left
                angle = start_pos - i * angle_step
            
            # Calculate position on circle
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Save current transformation
            self.ctx.save()
            
            # Move to character position
            self.ctx.translate(x, y)
            
            # Rotate character to be tangent to circle
            if upside_down:
                self.ctx.rotate(angle + math.pi/2)  # Bottom text rotation
            else:
                self.ctx.rotate(angle - math.pi/2)  # Top text rotation
            
            # Get text extents for centering
            text_extents = self.ctx.text_extents(char)
            
            # Draw character centered
            self.ctx.move_to(-text_extents.width/2, text_extents.height/2)
            self.ctx.show_text(char)
            
            # Restore transformation
            self.ctx.restore()
    
    def draw_horizontal_text(self, text, x, y, font_size=14, color=(0, 0, 0), bold=False):
        """Draw horizontal text"""
        self.ctx.set_source_rgb(*color)
        font_weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
        self.ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, font_weight)
        self.ctx.set_font_size(font_size)        
        self.ctx.move_to(x, y)
        self.ctx.show_text(text)
    
    def create_notary_stamp(self, 
                           top_curved_text="Notary Public",
                           bottom_curved_text="State of Texas",
                           name="Mercedes Smith",
                           notary_id="1234567",
                           expiry_date="05/01/20XX",
                           text_color=(0, 0, 0),
                           border_color=(0, 0, 0),
                           font_size_curved=16,
                           font_size_horizontal=14):
        """Create the complete notary stamp"""
        
        # Draw outer border
        self.draw_rounded_border(border_color=border_color)
        
        # Circle parameters
        circle_center_x = 120
        circle_center_y = self.height // 2
        circle_radius = 80
        
        # Draw simple rectangular border around the circular seal area
        rect_margin = 15
        rect_left = circle_center_x - circle_radius - rect_margin
        rect_top = circle_center_y - circle_radius - rect_margin
        rect_right = circle_center_x + circle_radius + rect_margin
        rect_bottom = circle_center_y + circle_radius + rect_margin
        
        # Draw rectangle border around seal
        self.ctx.set_source_rgb(*border_color)
        self.ctx.set_line_width(2)
        self.ctx.rectangle(rect_left, rect_top, rect_right - rect_left, rect_bottom - rect_top)
        self.ctx.stroke()
        
        # Draw main circle
        self.ctx.set_source_rgb(*border_color)
        self.ctx.set_line_width(3)
        self.ctx.arc(circle_center_x, circle_center_y, circle_radius, 0, 2 * math.pi)
        self.ctx.stroke()
        
        # Draw inner circle
        inner_radius = circle_radius - 20
        self.ctx.set_line_width(2)
        self.ctx.arc(circle_center_x, circle_center_y, inner_radius, 0, 2 * math.pi)
        self.ctx.stroke()
        
        # Draw star in center
        self.draw_star(circle_center_x, circle_center_y, outer_radius=20, inner_radius=8, 
                      color=border_color, width=2)
        
        # Draw curved text with fixed positioning to prevent overlap
        # Top curved text - positioned in upper semicircle only
        self.draw_text_on_arc(
            top_curved_text, 
            circle_center_x, circle_center_y, 
            circle_radius - 12,  # Slightly inside the circle
            0, 0,  # These parameters are now calculated inside the function
            font_size=font_size_curved, 
            color=text_color, 
            upside_down=False,
            char_spacing=2.5     # Conservative spacing
        )
        
        # Bottom curved text - positioned in lower semicircle only
        self.draw_text_on_arc(
            bottom_curved_text, 
            circle_center_x, circle_center_y, 
            circle_radius - 12,  # Slightly inside the circle
            0, 0,  # These parameters are now calculated inside the function
            font_size=font_size_curved, 
            color=text_color, 
            upside_down=True,
            char_spacing=2.5     # Conservative spacing
        )
        
        # Draw horizontal text on the right side
        right_text_x = circle_center_x + circle_radius + 40
        
        # Name (larger and bold)
        self.draw_horizontal_text(name.upper(), right_text_x, circle_center_y - 40, 
                                 font_size=font_size_horizontal + 6, color=text_color, bold=True)
        
        # Add a line under the name
        name_width = len(name) * (font_size_horizontal + 6) * 0.6
        self.ctx.set_source_rgb(*border_color)
        self.ctx.set_line_width(1)
        self.ctx.move_to(right_text_x, circle_center_y - 25)
        self.ctx.line_to(right_text_x + name_width, circle_center_y - 25)
        self.ctx.stroke()
        
        # Notary ID
        self.draw_horizontal_text("Notary ID #", right_text_x, circle_center_y - 10, 
                                 font_size=font_size_horizontal, color=text_color)
        self.draw_horizontal_text(notary_id, right_text_x, circle_center_y + 10, 
                                 font_size=font_size_horizontal + 2, color=text_color, bold=True)
        
        # Commission expiry
        self.draw_horizontal_text("My Commission Expires", right_text_x, circle_center_y + 30, 
                                 font_size=font_size_horizontal, color=text_color)
        self.draw_horizontal_text(expiry_date, right_text_x, circle_center_y + 50, 
                                 font_size=font_size_horizontal + 2, color=text_color, bold=True)
    
    def save_stamp(self, filename="notary_stamp_cairo.png"):
        """Save the generated stamp"""
        self.surface.write_to_png(filename)       
    
    ######## Helper functions for Class interaction #######
    def load_json_data(self, json_data):
            try:
                return json.loads(json_data)
            except Exception as e:
                print(f"json exp : {str(e)}")
                return str(e)

    ###### main process for Stamp Creation ###########
    def main_process(self, logger, json_str):
        logger.debug(f"Rectangle json_str: {json_str}")   
        output_filename = None
        data = self.load_json_data(json_str)
        if(data is None):
          return False

        try:
            output_filename = data.get('outFile')        
            top_curved_text = data['topCurevedText']
            bottom_curved_text = data['bottomCurvedText']
            name = data['notaryName']
            notary_id = data['notaryId']
            expiry_date = data['expireOn']        
            self.create_notary_stamp(
            top_curved_text=top_curved_text,
            bottom_curved_text=bottom_curved_text,
            name=name,
            notary_id=notary_id,
            expiry_date=expiry_date,
            text_color=(0, 0, 0),  # Black text
            border_color=(0, 0, 0),  # Black border
            font_size_curved=16,
            font_size_horizontal=14
        )    
            if(output_filename is not None and output_filename != ""):            
                self.save_stamp(output_filename)
                return True

        except Exception as ex:
            logger.debug(f"Rectangle Seal exception=> {str(ex)}")        
            return str(ex)

if __name__ == "__main__":    
    try:
        arguments = sys.argv
        jsonstr = arguments[1]
        objNotaryClass = LeafletNotaryStampGeneratorCairo(width=600, height=250)
        objNotaryClass.main_process(logger, jsonstr)
    except Exception as ex:
        print(f"exp: {str(ex)}")
        pass

    