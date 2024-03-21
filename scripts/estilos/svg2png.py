import os
import json
import argparse
import cairosvg
from PIL import Image

def generate_combined_image_and_json(svg_folder, output_combined_png, output_json):
    # List all SVG files in the specified folder
    svg_files = [f for f in os.listdir(svg_folder) if f.endswith('.svg')]
    svg_files = [os.path.join(svg_folder, f) for f in svg_files]

    total_svgs = len(svg_files)
    max_svgs_per_row = int(total_svgs**0.5)  # Use the square root for a balanced grid
    num_rows = (total_svgs + max_svgs_per_row - 1) // max_svgs_per_row
    num_cols = (total_svgs + num_rows - 1) // num_rows

    target_width = 50
    target_height = 50

    total_width = num_cols * target_width
    total_height = num_rows * target_height

    sprite_data = {}

    for i, svg_file in enumerate(svg_files):
        png_output = svg_file.replace('.svg', '.png')
        cairosvg.svg2png(url=svg_file, write_to=png_output)

        svg_image = Image.open(png_output)

        if svg_image.size != (target_width, target_height):
            svg_image = svg_image.resize((target_width, target_height), Image.ANTIALIAS)

        row = i // num_cols
        col = i % num_cols

        sprite_name = svg_file.split("/")[-1].replace(".svg", "")
        sprite_data[sprite_name] = {
            'height': target_height,
            'pixelRatio': 1,
            'width': target_width,
            'x': col * target_width,
            'y': row * target_height
        }

        # Remove the temporary PNG file
        os.remove(png_output)

    combined_image = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))

    for i, svg_file in enumerate(svg_files):
        sprite_info = sprite_data[svg_file.split("/")[-1].replace(".svg", "")]
        png_output = svg_file.replace('.svg', '.png')
        cairosvg.svg2png(url=svg_file, write_to=png_output)

        svg_image = Image.open(png_output)

        if svg_image.size != (target_width, target_height):
            svg_image = svg_image.resize((target_width, target_height), Image.ANTIALIAS)

        combined_image.paste(svg_image, (sprite_info['x'], sprite_info['y']))

        os.remove(png_output)

    combined_image.save(output_combined_png)

    with open(output_json, 'w') as json_file:
        json.dump(sprite_data, json_file, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Combine SVGs into a single PNG and generate JSON metadata.')
    parser.add_argument('svg_folder', help='Path to the folder containing SVG files')
    parser.add_argument('output_png', help='Path to the output PNG file')
    parser.add_argument('output_json', help='Path to the output JSON file')

    args = parser.parse_args()

    generate_combined_image_and_json(args.svg_folder, args.output_png, args.output_json)

if __name__ == "__main__":
    main()

