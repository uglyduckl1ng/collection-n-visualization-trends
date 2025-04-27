import csv, math
import svgwrite


def generate_radar_map():
    # === Configuration and constants ===
    outer_radius = 400 #Написать функцию расшинерия радиуса в зависимости от количества трендов
    ring_count = 4
    ring_width = outer_radius / ring_count
    # Colors for rings (inner to outer). Using blue shades as example.
    ring_colors = ['#0B82F4', '#51A0FA', '#8DC0FD', '#CFE5FE']
    category_text_color = ring_colors[0]  # use inner ring color for category labels
    # Font sizes for trend labels and category labels
    trend_font_size = 12
    category_font_size = 18
    # Element sizes and spacing
    point_radius = 4        # radius of trend point circle
    gap = 5                 # gap between trend point and label oval
    pad_x = 5               # horizontal padding inside oval
    pad_y = 2               # vertical padding inside oval
    # Line and fill colors
    line_color = 'black'    # connector line color
    line_width = 1
    oval_fill = 'white'     # oval background color

    # Input/output files
    input_csv = 'data/trends.csv'
    output_svg = 'pics/trends_diagram.svg'

    # Time range mapping to ring indices
    time_to_ring = {
        'Now': 0, 'Сейчас': 0,
        '1-5 years': 1, '1-5': 1, '1-5 лет': 1,
        '5-20 years': 2, '5-20': 2, '5-20 лет': 2,
        '>15 years': 3, '20+ лет (Долгосрочное планирование)': 3, '20+ лет': 3
    }

    # === Read CSV data ===
    categories = []
    cat_index = {}
    trend_list = []
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trend_name = row.get('trend', '').strip()
            category_name = row.get('category', '').strip()
            time_range = row.get('time_zone', '').strip()
            if not trend_name or not category_name:
                continue  # skip empty entries
            # Track category order of first appearance
            if category_name not in cat_index:
                cat_index[category_name] = len(categories)
                categories.append(category_name)
            # Map time range to ring index (default to outermost if unknown)
            ring_idx = time_to_ring.get(time_range, ring_count - 1)
            trend_list.append({
                'name': trend_name,
                'cat_idx': cat_index[category_name],
                'ring_idx': ring_idx
            })

    # Ensure we have exactly 6 categories (as expected by design)
    if len(categories) != 6:
        # If not, proceed anyway but distribution assumes 6 sectors
        pass

    # === Calculate layout parameters ===
    # Category angles (evenly spaced around full circle)
    start_angle = 90  # first category at 90 degrees (pointing up)
    angle_step = 360 / (len(categories) if len(categories) > 0 else 6)
    category_angles = [start_angle - i * angle_step for i in range(len(categories))]

    # Midpoint radius for each time-range ring
    ring_radius_pos = [(i + 0.5) * ring_width for i in range(ring_count)]

    # Group trends by sector (category index + ring index)
    from collections import defaultdict
    grouped = defaultdict(list)
    for t in trend_list:
        grouped[(t['cat_idx'], t['ring_idx'])].append(t)

    # Assign angle offsets for multiple trends in the same sector to avoid overlap
    trend_positions = []
    for (cat_idx, ring_idx), items in grouped.items():
        base_angle = start_angle - cat_idx * angle_step
        n = len(items)
        offsets = [0] * n
        if n > 1:
            # Distribute multiple points within the 60° sector
            step = 10  # default offset step in degrees
            max_step = 60 / n
            if max_step < step:
                step = max_step
            for j in range(n):
                offsets[j] = (j - (n - 1) / 2) * step
        for item, off in zip(items, offsets):
            angle = base_angle + off
            trend_positions.append({
                'name': item['name'],
                'cat_idx': cat_idx,
                'ring_idx': ring_idx,
                'angle': angle
            })

    # Prepare category labels info (for positioning and extent calculation)
    categories_info = []
    for i, cat in enumerate(categories):
        angle_deg = category_angles[i]
        angle_rad = math.radians(angle_deg)
        # Position category labels just outside outer ring (20px outward)
        r = outer_radius + 20
        x_rel = r * math.cos(angle_rad)
        y_rel = r * math.sin(angle_rad)
        text = cat
        text_width = 0.6 * category_font_size * len(text)
        cos_val = math.cos(angle_rad)
        if cos_val > 1e-6:  # right side
            anchor = 'start'
            left = x_rel
            right = x_rel + text_width
        elif cos_val < -1e-6:  # left side
            anchor = 'end'
            left = x_rel - text_width
            right = x_rel
        else:  # top or bottom (centered)
            anchor = 'middle'
            left = x_rel - text_width / 2
            right = x_rel + text_width / 2
        top = y_rel - category_font_size / 2
        bottom = y_rel + category_font_size / 2
        categories_info.append({
            'text': cat,
            'anchor': anchor,
            'x_rel': x_rel,
            'y_rel': y_rel,
            'left': left,
            'right': right,
            'top': top,
            'bottom': bottom
        })

    # Compute overall bounding box needed (consider category labels and outer circle)
    min_x = min(ci['left'] for ci in categories_info) if categories_info else 0
    max_x = max(ci['right'] for ci in categories_info) if categories_info else 0
    min_y = min(ci['top'] for ci in categories_info) if categories_info else 0
    max_y = max(ci['bottom'] for ci in categories_info) if categories_info else 0
    min_x = min(min_x, -outer_radius)
    max_x = max(max_x, outer_radius)
    min_y = min(min_y, -outer_radius)
    max_y = max(max_y, outer_radius)
    # Round out the extents
    min_x = math.floor(min_x);  max_x = math.ceil(max_x)
    min_y = math.floor(min_y);  max_y = math.ceil(max_y)
    width = int(max_x - min_x)
    height = int(max_y - min_y)
    # Offsets to translate center to SVG coordinate origin (top-left)
    center_x = -min_x
    center_y = -min_y

    # === Create SVG drawing ===
    dwg = svgwrite.Drawing(output_svg, size=(f"{width}px", f"{height}px"))

    # Draw concentric time-range rings (from outermost to innermost)
    for idx in reversed(range(ring_count)):
        r = (idx + 1) * ring_width
        color = ring_colors[idx] if idx < len(ring_colors) else ring_colors[-1]
        dwg.add(dwg.circle(center=(center_x, center_y), r=r, fill=color))

    # Draw radial lines for category boundaries (6 sectors => 3 lines through center)
    for angle_deg in [0, 60, 120]:
        a_rad = math.radians(angle_deg)
        x_off = outer_radius * math.cos(a_rad)
        y_off = outer_radius * math.sin(a_rad)
        x1 = center_x + x_off;    y1 = center_y - y_off
        x2 = center_x - x_off;    y2 = center_y + y_off
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke='white', stroke_width=1))

    # Prepare lists for drawing connectors, points, ovals, and trend texts
    connector_lines = []
    point_circles = []
    oval_rects = []
    trend_text_elems = []

    outer_sector_arc = outer_radius * math.radians(60)  # arc length of sector at outer edge, for text fit check

    # Calculate positions and shapes for each trend point and label
    for trend in trend_positions:
        name = trend['name']
        ring_idx = trend['ring_idx']
        angle_deg = trend['angle']
        angle_rad = math.radians(angle_deg)
        # Base radial position for this trend (default to ring midpoint)
        r = ring_radius_pos[ring_idx]
        text_width = 0.5 * trend_font_size * len(name)
        # If in outer ring and text might overflow, move point inward within ring
        if ring_idx == ring_count - 1 and text_width > outer_sector_arc:
            r -= ring_width * 0.5
            if r < ring_idx * ring_width:
                r = ring_idx * ring_width
        # Compute point coordinates relative to center
        x_rel = r * math.cos(angle_rad)
        y_rel = r * math.sin(angle_rad)
        px = center_x + x_rel
        py = center_y - y_rel
        # Determine side for label placement (left or right of point)
        side = 'right' if math.cos(angle_rad) >= 0 else 'left'
        # Compute horizontal span of label (including padding)
        if side == 'right':
            base_x = px + point_radius + gap
            left_edge = base_x
            right_edge = base_x + 2 * pad_x + text_width #тут поставил 1 вместо 2
            text_anchor = 'start'
            text_insert_x = base_x + pad_x
        else:
            base_x = px - (point_radius + gap)
            right_edge = base_x
            left_edge = base_x - 2 * pad_x - text_width
            text_anchor = 'end'
            text_insert_x = base_x - pad_x
        # Connector line from point to label oval
        connector_lines.append({
            'start': (px, py),
            'end': ((left_edge if side == 'right' else right_edge), py)
        })
        # Store point circle (white dot)
        point_circles.append({
            'center': (px, py),
            'radius': point_radius
        })
        # Oval background dimensions
        oval_width = right_edge - left_edge
        oval_height = trend_font_size + 2 * pad_y
        oval_rects.append({
            'insert': (left_edge, py - oval_height/2),
            'size': (oval_width, oval_height)
        })
        # Trend text element info
        trend_text_elems.append({
            'text': name,
            'insert': (text_insert_x, py),
            'anchor': text_anchor
        })

    # Draw all connectors (behind other elements)
    for line in connector_lines:
        dwg.add(dwg.line(start=line['start'], end=line['end'], stroke=line_color, stroke_width=line_width))
    # Draw all trend points (white circles)
    for point in point_circles:
        dwg.add(dwg.circle(center=point['center'], r=point['radius'], fill='white'))
    # Draw all label ovals (adaptive width)
    for oval in oval_rects:
        dwg.add(dwg.rect(insert=oval['insert'], size=oval['size'],
                        rx=oval['size'][1]/2, ry=oval['size'][1]/2, fill=oval_fill))
    # Draw all trend text labels
    for text in trend_text_elems:
        dwg.add(dwg.text(text['text'], insert=text['insert'],
                        text_anchor=text['anchor'], dominant_baseline="middle",
                        fill='black', font_size=trend_font_size))

    # Draw category labels (around outside of chart)
    for ci in categories_info:
        cx = center_x + ci['x_rel'];    cy = center_y - ci['y_rel']
        dwg.add(dwg.text(ci['text'], insert=(cx, cy),
                        text_anchor=ci['anchor'], dominant_baseline="middle",
                        fill=category_text_color, font_size=category_font_size))

    # Save SVG file
    dwg.save()
    print(f"SVG diagram saved as '{output_svg}' ({width}x{height}px)")

generate_radar_map()