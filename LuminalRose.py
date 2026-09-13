import math
import cmath
import sys
import pygame


def generate_penrose_subdivision(divisions=6, base=5):
    """Create triangles using the Robinson triangle substitution (thin/thick).

    Returns a list of tuples: (shape, v1, v2, v3) where v* are complex points.
    """
    triangles = []
    for i in range(base * 2):
        v2 = cmath.rect(1, (2 * i - 1) * math.pi / (base * 2))
        v3 = cmath.rect(1, (2 * i + 1) * math.pi / (base * 2))

        if i % 2 == 0:
            v2, v3 = v3, v2

        triangles.append(("thin", 0 + 0j, v2, v3))

    phi = (5 ** 0.5 + 1) / 2

    for _ in range(divisions):
        new_triangles = []
        for shape, v1, v2, v3 in triangles:
            if shape == "thin":
                p1 = v1 + (v2 - v1) / phi
                new_triangles.append(("thin", v3, p1, v2))
                new_triangles.append(("thicc", p1, v3, v1))
            else:
                p2 = v2 + (v1 - v2) / phi
                p3 = v2 + (v3 - v2) / phi
                new_triangles.append(("thicc", p3, v3, v1))
                new_triangles.append(("thicc", p2, p3, v2))
                new_triangles.append(("thin", p3, p2, v1))
        triangles = new_triangles

    # filter degenerate triangles
    def area(a, b, c):
        return abs((b.real - a.real) * (c.imag - a.imag) - (c.real - a.real) * (b.imag - a.imag)) * 0.5

    triangles = [t for t in triangles if area(t[1], t[2], t[3]) > 1e-8]
    return triangles


def to_screen(point, offset, scale):
    return int(offset[0] + point.real * scale), int(offset[1] - point.imag * scale)


def main():
    # configurable parameters
    divisions = 3
    scale = 240  # pixels per unit
    size = (800, 800)

    pygame.init()
    offset = [size[0] // 2, size[1] // 2]

    # Try to create a visible window; if that fails, fall back to a Surface
    headless = False
    try:
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Penrose Tiling - Interactive")
    except pygame.error:
        headless = True
        screen = pygame.Surface(size)

    # paint jobs
    PAINT_BACKROOMS = 1
    PAINT_DEFAULT = 0

    paint_job = PAINT_BACKROOMS

    def apply_paint(job):
        nonlocal fat_color, thin_color, border_color, background_color, ground_color, wall_color, ceiling_color
        if job == PAINT_BACKROOMS:
            # Backrooms style: dingy carpet, sickly walls, darker background for contrast
            fat_color = (190, 170, 90)
            thin_color = (170, 150, 80)
            border_color = (35, 25, 15)
            background_color = (120, 110, 60)
            ground_color = (80, 75, 50)
            wall_color = (200, 185, 90)
            ceiling_color = (185, 175, 120)
        else:
            fat_color = (230, 200, 100)
            thin_color = (95, 155, 215)
            border_color = (20, 20, 20)
            background_color = (18, 18, 32)
            ground_color = (46, 40, 52)
            wall_color = (80, 80, 90)
            ceiling_color = (160, 160, 170)

    # default vars (will be set by apply_paint)
    fat_color = thin_color = border_color = background_color = ground_color = wall_color = ceiling_color = None
    apply_paint(paint_job)

    triangles = generate_penrose_subdivision(divisions=divisions, base=5)

    clock = pygame.time.Clock()
    running = True
    outlines = False
    dragging = False
    last_mouse = (0, 0)
    save_request = None
    saved_once = False

    # --- First-person camera utilities ---
    cam_x, cam_y, cam_z = 0.0, -0.5, 0.9
    yaw, pitch = 0.0, -0.4
    mouse_look = True
    move_speed = 0.0018
    sprint = 1.0

    if not headless:
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    wallpaper_texture = None
    try:
        wallpaper_texture = pygame.image.load("wallpaper texture.png").convert()
    except Exception:
        wallpaper_texture = None

    # 60 degree FOV for claustrophobic feel
    fov_deg = 60.0
    focal = (size[0] / 2.0) / math.tan(math.radians(fov_deg) / 2.0)

    # --- build walls from Penrose triangle edges ---
    wall_thickness = 0.40
    wall_height = 1.6
    ceiling_height = 2.8
    door_gap_fraction = 0.28  # fraction of edge length left open in middle

    # scale triangles to world units (bigger rooms feel more unsettling)
    tile_scale = 18.0
    verts = []
    for _, v1, v2, v3 in triangles:
        verts.extend([v1, v2, v3])
    # compute bounding box of vertices
    xs = [v.real * tile_scale for v in verts]
    ys = [v.imag * tile_scale for v in verts]
    if xs and ys:
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
    else:
        min_x = min_y = -5
        max_x = max_y = 5

    # build edge map
    edge_count = {}
    edge_pts = {}
    def edge_key(a, b):
        # sort by coordinates
        if (a.real, a.imag) <= (b.real, b.imag):
            return (round(a.real, 6), round(a.imag, 6), round(b.real, 6), round(b.imag, 6))
        else:
            return (round(b.real, 6), round(b.imag, 6), round(a.real, 6), round(a.imag, 6))

    for shape, v1, v2, v3 in triangles:
        tri = [v1, v2, v3]
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            k = edge_key(a, b)
            edge_count[k] = edge_count.get(k, 0) + 1
            edge_pts[k] = (a, b)

    walls = []
    # for each unique edge create two wall segments leaving a gap at center
    for k, (a, b) in edge_pts.items():
        ax, ay = a.real * tile_scale, a.imag * tile_scale
        bx, by = b.real * tile_scale, b.imag * tile_scale
        # door gap in middle
        gap = door_gap_fraction
        # segment points at t0..t1 and t2..t3
        t0 = 0.0
        t1 = (1.0 - gap) / 2.0
        t2 = (1.0 + gap) / 2.0
        t3 = 1.0
        def lerp(t):
            return (ax + (bx - ax) * t, ay + (by - ay) * t)
        p0 = lerp(t0)
        p1 = lerp(t1)
        p2 = lerp(t2)
        p3 = lerp(t3)
        # add segments if length > small epsilon
        if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) > 1e-6:
            x1, y1, x2, y2 = p0[0], p0[1], p1[0], p1[1]
            mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length != 0:
                nx, ny = (-dy / length, dx / length)
                walls.append((x1, y1, x2, y2, mx, my, nx, ny, length))
        if math.hypot(p3[0] - p2[0], p3[1] - p2[1]) > 1e-6:
            x1, y1, x2, y2 = p2[0], p2[1], p3[0], p3[1]
            mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length != 0:
                nx, ny = (-dy / length, dx / length)
                walls.append((x1, y1, x2, y2, mx, my, nx, ny, length))

    # movement speed scales with world scale so camera moves sensibly
    move_speed = 0.00012 * tile_scale

    # rendering culling radius (world units) to limit work per-frame
    render_radius = 35.0
    render_radius_min = 20.0
    render_radius_max = 80.0
    render_radius_step = 6.0
    render_radius_sq = render_radius * render_radius

    # spatial hash (uniform grid) for walls and triangles
    spatial_cell = max(2.0, tile_scale * 3.0)
    spatial_walls = {}
    spatial_tris = {}

    def cell_coords(x, y):
        return int(math.floor(x / spatial_cell)), int(math.floor(y / spatial_cell))

    def add_to_grid(grid, ix, iy, idx):
        key = (ix, iy)
        if key not in grid:
            grid[key] = []
        grid[key].append(idx)

    def build_spatial_index():
        spatial_walls.clear()
        spatial_tris.clear()
        for i, w in enumerate(walls):
            x1, y1, x2, y2 = w[0], w[1], w[2], w[3]
            margin = wall_thickness * 0.6
            minx = min(x1, x2) - margin
            maxx = max(x1, x2) + margin
            miny = min(y1, y2) - margin
            maxy = max(y1, y2) + margin
            ix0, iy0 = cell_coords(minx, miny)
            ix1, iy1 = cell_coords(maxx, maxy)
            for ix in range(ix0, ix1 + 1):
                for iy in range(iy0, iy1 + 1):
                    add_to_grid(spatial_walls, ix, iy, i)

        for i, item in enumerate(triangles_world):
            cx, cy = item[4], item[5]
            ix, iy = cell_coords(cx, cy)
            add_to_grid(spatial_tris, ix, iy, i)

    def query_wall_indices(x, y, radius):
        ix, iy = cell_coords(x, y)
        r = int(math.ceil(radius / spatial_cell))
        found = set()
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                key = (ix + dx, iy + dy)
                if key in spatial_walls:
                    found.update(spatial_walls[key])
        return found

    def query_tri_indices(x, y, radius):
        ix, iy = cell_coords(x, y)
        r = int(math.ceil(radius / spatial_cell))
        found = set()
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                key = (ix + dx, iy + dy)
                if key in spatial_tris:
                    found.update(spatial_tris[key])
        return found

    def ray_segment_intersect(ax, ay, bx, by, x1, y1, x2, y2):
        # ray from A to B, segment [x1,y1]->[x2,y2]
        r_px = bx - ax
        r_py = by - ay
        s_px = x2 - x1
        s_py = y2 - y1
        denom = r_px * s_py - r_py * s_px
        if abs(denom) < 1e-9:
            return False
        t = ((x1 - ax) * s_py - (y1 - ay) * s_px) / denom
        u = ((x1 - ax) * r_py - (y1 - ay) * r_px) / denom
        return 0.0 < t < 1.0 and 0.0 <= u <= 1.0

    def is_occluded(cx, cy):
        nearby = query_wall_indices(cx, cy, render_radius)
        for i in nearby:
            w = walls[i]
            x1, y1, x2, y2 = w[0], w[1], w[2], w[3]
            if ray_segment_intersect(cam_x, cam_y, cx, cy, x1, y1, x2, y2):
                return True
        return False

    # collision helpers
    def dist_point_segment(px, py, x1, y1, x2, y2):
        vx = x2 - x1
        vy = y2 - y1
        wx = px - x1
        wy = py - y1
        c = vx * vx + vy * vy
        if c == 0:
            t = 0
        else:
            t = (wx * vx + wy * vy) / c
            t = max(0.0, min(1.0, t))
        bx = x1 + t * vx
        by = y1 + t * vy
        dx = px - bx
        dy = py - by
        return math.hypot(dx, dy)

    def collides(px, py, radius=0.18):
        # query nearby walls only
        nearby = query_wall_indices(px, py, radius + wall_thickness)
        for i in nearby:
            w = walls[i]
            x1, y1, x2, y2 = w[0], w[1], w[2], w[3]
            if dist_point_segment(px, py, x1, y1, x2, y2) < (radius + wall_thickness * 0.4):
                return True
        return False

    player_radius = 0.08

    def find_spawn_point():
        # preferentially spawn in an open tile centroid
        open_spots = []
        for shape, p1, p2, p3, cx, cy in triangles_world:
            if not collides(cx, cy, radius=player_radius * 0.8):
                open_spots.append((cx, cy))
        if open_spots:
            center_x = (min_x + max_x) / 2.0
            center_y = (min_y + max_y) / 2.0
            open_spots.sort(key=lambda p: ((p[0]-center_x)**2 + (p[1]-center_y)**2))
            return open_spots[0]

        origin_x = (min_x + max_x) / 2.0
        origin_y = (min_y + max_y) / 2.0
        if not collides(origin_x, origin_y, radius=player_radius):
            return origin_x, origin_y

        radii = [3.0, 6.0, 9.0, 12.0]
        for radius in radii:
            steps = max(16, int(radius * 4) + 8)
            for i in range(steps):
                angle = 2.0 * math.pi * i / steps
                x = origin_x + math.cos(angle) * radius
                y = origin_y + math.sin(angle) * radius
                if not collides(x, y, radius=player_radius):
                    return x, y
        return origin_x, origin_y

    def reset_spawn():
        nonlocal cam_x, cam_y
        cam_x, cam_y = find_spawn_point()

    # minimap bounds and scale
    world_w = max_x - min_x
    world_h = max_y - min_y
    world_size = max(world_w, world_h)
    minimap_size = 200
    minimap_scale = minimap_size / world_size if world_size > 0 else 1.0
    minimap_margin = 8
    half = world_size / 2.0
    minimap_enabled = True
    minimap_bg = (20, 20, 20, 180)

    # center camera on penrose bounds
    cam_x = (min_x + max_x) / 2.0
    cam_y = (min_y + max_y) / 2.0
    cam_z = 1.0


    def world_to_camera(px, py, pz=0.0):
        dx = px - cam_x
        dy = py - cam_y
        fx = math.cos(yaw)
        fy = math.sin(yaw)
        rx = -fy
        ry = fx
        x_cam = dx * rx + dy * ry
        z_cam = dx * fx + dy * fy
        y_cam = cam_z - pz
        # pitch rotation
        y2 = math.cos(pitch) * y_cam - math.sin(pitch) * z_cam
        z2 = math.sin(pitch) * y_cam + math.cos(pitch) * z_cam
        return x_cam, y2, z2

    center_x = size[0] // 2
    center_y = size[1] // 2

    def project_point(px, py, pz=0.0):
        x_cam, y2, z2 = world_to_camera(px, py, pz)
        if z2 <= 0.0001:
            return None
        sx = center_x + (x_cam / z2) * focal
        sy = center_y - (y2 / z2) * focal
        return (int(sx), int(sy))

    def project_plane_polygon(corners, pz):
        near = 0.0001
        projected = []
        cam_corners = []
        for x, y in corners:
            x_cam, y2, z2 = world_to_camera(x, y, pz)
            cam_corners.append((x, y, x_cam, y2, z2))
        for i in range(len(cam_corners)):
            x1, y1, x_cam1, y21, z21 = cam_corners[i]
            x2, y2, x_cam2, y22, z22 = cam_corners[(i + 1) % len(cam_corners)]
            if z21 > near:
                proj = project_point(x1, y1, pz)
                if proj is not None:
                    projected.append(proj)
            if (z21 > near) != (z22 > near):
                t = (near - z21) / (z22 - z21)
                ix = x1 + (x2 - x1) * t
                iy = y1 + (y2 - y1) * t
                proj = project_point(ix, iy, pz)
                if proj is not None:
                    projected.append(proj)
        if len(projected) > 2:
            cx = sum(p[0] for p in projected) / len(projected)
            cy = sum(p[1] for p in projected) / len(projected)
            projected.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        return projected

    def draw_textured_polygon(target, texture, proj_pts, shade):
        xs = [p[0] for p in proj_pts]
        ys = [p[1] for p in proj_pts]
        min_x, max_x = int(min(xs)), int(max(xs))
        min_y, max_y = int(min(ys)), int(max(ys))
        width = max(1, max_x - min_x)
        height = max(1, max_y - min_y)
        if width * height > 250000 or width > 512 or height > 512:
            # too large to safely texture per frame; fall back to flat shaded wall
            try:
                pygame.draw.polygon(target, shade, proj_pts)
            except Exception:
                pass
            return
        tile_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        tw, th = texture.get_size()
        for ty in range(0, height, th):
            for tx in range(0, width, tw):
                tile_surf.blit(texture, (tx, ty))
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        poly = [(p[0] - min_x, p[1] - min_y) for p in proj_pts]
        pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
        tile_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        tile_surf.fill(shade + (0,), special_flags=pygame.BLEND_RGBA_MULT)
        target.blit(tile_surf, (min_x, min_y))

    def render():
        screen.fill(background_color)

        # ground quad covering penrose bounds, clipped to view frustum
        corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        proj_corners = project_plane_polygon(corners, 0.0)
        if len(proj_corners) >= 3:
            try:
                pygame.draw.polygon(screen, ground_color, proj_corners)
            except Exception:
                pass

        # draw ceiling plane for depth and room feeling
        ceiling_corners = project_plane_polygon(corners, ceiling_height)
        if len(ceiling_corners) >= 3:
            try:
                pygame.draw.polygon(screen, ceiling_color, ceiling_corners)
            except Exception:
                pass

        # draw filled triangles (as decoration) with simple distance culling and occlusion
        for i in query_tri_indices(cam_x, cam_y, render_radius):
            shape, p1, p2, p3, cx, cy = triangles_world[i]
            dx = cx - cam_x
            dy = cy - cam_y
            dist2 = dx * dx + dy * dy
            if dist2 > render_radius_sq:
                continue
            if is_occluded(cx, cy):
                continue
            proj = [project_point(p[0], p[1]) for p in (p1, p2, p3)]
            if any(p is None for p in proj):
                continue
            base = thin_color if shape == "thin" else fat_color
            shade = max(0.25, 1.0 - (math.sqrt(dist2) / render_radius) * 0.6)
            color = tuple(max(0, min(255, int(c * shade))) for c in base)
            try:
                pygame.draw.polygon(screen, color, proj)
            except Exception:
                pass

        # outlines
        if outlines:
            for item in triangles_world:
                shape, p1, p2, p3, cx, cy = item
                dx = cx - cam_x
                dy = cy - cam_y
                if dx * dx + dy * dy > render_radius_sq:
                    continue
                pts = [p2, p1, p3]
                proj = [project_point(x, y) for x, y in pts]
                if any(p is None for p in proj):
                    continue
                pygame.draw.lines(screen, border_color, False, proj, 1)

    # helper to regenerate triangles when divisions change
    # this also precomputes world-space triangle verts and wall metadata for faster per-frame rendering
    def regen(n):
        nonlocal triangles, verts, min_x, max_x, min_y, max_y, edge_count, edge_pts, walls, minimap_scale, world_w, world_h, world_size, triangles_world
        n = max(0, min(9, n))
        triangles = generate_penrose_subdivision(divisions=n, base=5)
        # recompute verts/bounds and walls
        verts = []
        for _, v1, v2, v3 in triangles:
            verts.extend([v1, v2, v3])
        xs = [v.real * tile_scale for v in verts]
        ys = [v.imag * tile_scale for v in verts]
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x = min_y = -5
            max_x = max_y = 5
        # rebuild edge map
        edge_count = {}
        edge_pts = {}
        def edge_key2(a, b):
            if (a.real, a.imag) <= (b.real, b.imag):
                return (round(a.real, 6), round(a.imag, 6), round(b.real, 6), round(b.imag, 6))
            else:
                return (round(b.real, 6), round(b.imag, 6), round(a.real, 6), round(a.imag, 6))
        for shape, v1, v2, v3 in triangles:
            tri = [v1, v2, v3]
            for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                k = edge_key2(a, b)
                edge_count[k] = edge_count.get(k, 0) + 1
                edge_pts[k] = (a, b)
        walls = []
        for k, (a, b) in edge_pts.items():
            ax, ay = a.real * tile_scale, a.imag * tile_scale
            bx, by = b.real * tile_scale, b.imag * tile_scale
            gap = door_gap_fraction
            t1 = (1.0 - gap) / 2.0
            t2 = (1.0 + gap) / 2.0
            def lerp2(t):
                return (ax + (bx - ax) * t, ay + (by - ay) * t)
            p0 = lerp2(0.0)
            p1 = lerp2(t1)
            p2 = lerp2(t2)
            p3 = lerp2(1.0)
            if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) > 1e-6:
                x1, y1, x2, y2 = p0[0], p0[1], p1[0], p1[1]
                mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                if length == 0: continue
                nx, ny = (-dy / length, dx / length)
                walls.append((x1, y1, x2, y2, mx, my, nx, ny, length))
            if math.hypot(p3[0] - p2[0], p3[1] - p2[1]) > 1e-6:
                x1, y1, x2, y2 = p2[0], p2[1], p3[0], p3[1]
                mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                if length == 0: continue
                nx, ny = (-dy / length, dx / length)
                walls.append((x1, y1, x2, y2, mx, my, nx, ny, length))
        world_w = max_x - min_x
        world_h = max_y - min_y
        world_size = max(world_w, world_h)
        minimap_scale = minimap_size / world_size if world_size > 0 else 1.0

        # precompute triangle world coordinates and centroids for fast culling
        triangles_world = []
        for shape, v1, v2, v3 in triangles:
            x1, y1 = v1.real * tile_scale, v1.imag * tile_scale
            x2, y2 = v2.real * tile_scale, v2.imag * tile_scale
            x3, y3 = v3.real * tile_scale, v3.imag * tile_scale
            cx = (x1 + x2 + x3) / 3.0
            cy = (y1 + y2 + y3) / 3.0
            triangles_world.append((shape, (x1, y1), (x2, y2), (x3, y3), cx, cy))
        # build spatial index for render and collision
        build_spatial_index()

    # precomputed triangle/world caches
    triangles_world = []

    regen(divisions)
    reset_spawn()

    target_fps = 30
    detail_check_interval = 1500
    last_detail_check = pygame.time.get_ticks()

    print("Controls: mouse-wheel zoom, drag to pan, +/- expand/shrink view, o toggle outlines, s save, ESC quit")

    while running:
        dt = clock.tick(target_fps)
        raw_dt = clock.get_rawtime()
        if raw_dt <= 0:
            raw_dt = dt

        now = pygame.time.get_ticks()
        if now - last_detail_check >= detail_check_interval:
            last_detail_check = now
            target_ms = 1000.0 / target_fps
            if raw_dt < target_ms * 0.85 and render_radius < render_radius_max:
                render_radius = min(render_radius_max, render_radius + render_radius_step)
                render_radius_sq = render_radius * render_radius
                print("view radius increased to", render_radius)
            elif raw_dt > target_ms * 1.15 and render_radius > render_radius_min:
                render_radius = max(render_radius_min, render_radius - render_radius_step)
                render_radius_sq = render_radius * render_radius
                print("view radius reduced to", render_radius)

        # print FPS occasionally
        if now % 3000 < 40:
            fps = clock.get_fps()
            if fps > 0:
                print(f"FPS: {fps:.1f} raw {raw_dt:.1f}ms radius {render_radius}")
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    render_radius = min(render_radius_max, render_radius + render_radius_step)
                    render_radius_sq = render_radius * render_radius
                    print("view radius increased to", render_radius)
                elif event.key == pygame.K_MINUS:
                    render_radius = max(render_radius_min, render_radius - render_radius_step)
                    render_radius_sq = render_radius * render_radius
                    print("view radius reduced to", render_radius)
                elif event.key == pygame.K_o:
                    outlines = not outlines
                elif event.key == pygame.K_s:
                    # request a save after rendering this frame
                    save_request = f"penrose_radius{int(render_radius)}.png"
                elif event.key == pygame.K_r:
                    cam_x, cam_y, cam_z = 0.0, -0.5, 0.9
                    yaw, pitch = 0.0, -0.4
                elif event.key == pygame.K_TAB:
                    # toggle mouse look
                    mouse_look = not mouse_look
                    pygame.event.set_grab(mouse_look)
                    pygame.mouse.set_visible(not mouse_look)
                elif event.key == pygame.K_m:
                    minimap_enabled = not minimap_enabled
                elif event.key == pygame.K_p:
                    paint_job = (paint_job + 1) % 2
                    apply_paint(paint_job)
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    focal *= 1.05
                else:
                    focal /= 1.05

        # mouse look
        if mouse_look and not headless:
            mx, my = pygame.mouse.get_rel()
            # make horizontal axis match vertical: moving mouse right turns camera right
            yaw += mx * 0.002
            # moving mouse up should look up
            pitch += -my * 0.002
            pitch = max(-1.4, min(1.4, pitch))

        # movement
        move = 0.0
        strafe = 0.0
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            sprint = 3.0
        else:
            sprint = 1.0
        if keys[pygame.K_w]:
            move += 1.0
        if keys[pygame.K_s]:
            move -= 1.0
        if keys[pygame.K_a]:
            strafe -= 1.0
        if keys[pygame.K_d]:
            strafe += 1.0

        if move != 0.0 or strafe != 0.0:
            # compute forward/right in XY plane
            fx = math.cos(yaw)
            fy = math.sin(yaw)
            rx = -fy
            ry = fx
            dx = (fx * move + rx * strafe) * move_speed * dt * sprint
            dy = (fy * move + ry * strafe) * move_speed * dt * sprint
            new_x = cam_x + dx
            new_y = cam_y + dy
            # try full move first
            if not collides(new_x, new_y, radius=player_radius):
                cam_x = new_x
                cam_y = new_y
            else:
                # sliding: try X only then Y only
                if not collides(new_x, cam_y, radius=player_radius):
                    cam_x = new_x
                elif not collides(cam_x, new_y, radius=player_radius):
                    cam_y = new_y
                else:
                    # reduce step if blocked in tight spaces
                    cam_x += dx * 0.25
                    cam_y += dy * 0.25

        render()
        nearby_wall_indices = query_wall_indices(cam_x, cam_y, render_radius + wall_thickness)
        sorted_walls = sorted((walls[i] for i in nearby_wall_indices), key=lambda w: ((w[4] - cam_x) ** 2 + (w[5] - cam_y) ** 2), reverse=True)
        for entry in sorted_walls:
            x1, y1, x2, y2, mx, my, nx, ny, length = entry
            dx = mx - cam_x
            dy = my - cam_y
            if dx * dx + dy * dy > render_radius_sq:
                continue
            half = wall_thickness * 0.5
            p1a = (x1 + nx * half, y1 + ny * half)
            p1b = (x1 - nx * half, y1 - ny * half)
            p2a = (x2 + nx * half, y2 + ny * half)
            p2b = (x2 - nx * half, y2 - ny * half)

            # choose visible wall face from camera side
            side = 1.0 if ((cam_x - mx) * nx + (cam_y - my) * ny) >= 0 else -1.0
            if side > 0:
                front_a, front_b = p1a, p2a
            else:
                front_a, front_b = p1b, p2b

            fa_b = project_point(front_a[0], front_a[1])
            fb_b = project_point(front_b[0], front_b[1])
            fa_t = project_point(front_a[0], front_a[1], pz=wall_height)
            fb_t = project_point(front_b[0], front_b[1], pz=wall_height)
            if fa_b and fb_b and fb_t and fa_t:
                dist = math.sqrt(dx * dx + dy * dy)
                shade = max(0.25, 1.0 - (dist / render_radius) * 0.7)
                wall_shade = tuple(max(0, min(255, int(c * shade))) for c in wall_color)
                if wallpaper_texture is not None:
                    draw_textured_polygon(screen, wallpaper_texture, [fa_b, fb_b, fb_t, fa_t], wall_shade)
                else:
                    try:
                        pygame.draw.polygon(screen, wall_shade, [fa_b, fb_b, fb_t, fa_t])
                    except Exception:
                        pass

                # draw a dirty yellow rim only on the two vertical end edges of the wall face
                wall_dx = front_b[0] - front_a[0]
                wall_dy = front_b[1] - front_a[1]
                wall_len = math.hypot(wall_dx, wall_dy)
                if wall_len > 1e-6:
                    rim_depth = min(0.8, max(0.18, wall_thickness * 0.35))
                    dir_x = wall_dx / wall_len
                    dir_y = wall_dy / wall_len
                    left_inner = (front_a[0] + dir_x * rim_depth, front_a[1] + dir_y * rim_depth)
                    right_inner = (front_b[0] - dir_x * rim_depth, front_b[1] - dir_y * rim_depth)
                    left_a_b = project_point(front_a[0], front_a[1])
                    left_a_t = project_point(front_a[0], front_a[1], pz=wall_height)
                    left_inner_b = project_point(left_inner[0], left_inner[1])
                    left_inner_t = project_point(left_inner[0], left_inner[1], pz=wall_height)
                    right_b_b = project_point(front_b[0], front_b[1])
                    right_b_t = project_point(front_b[0], front_b[1], pz=wall_height)
                    right_inner_b = project_point(right_inner[0], right_inner[1])
                    right_inner_t = project_point(right_inner[0], right_inner[1], pz=wall_height)
                    rim_color = (150, 125, 45)
                    if left_a_b and left_inner_b and left_inner_t and left_a_t:
                        try:
                            pygame.draw.polygon(screen, rim_color, [left_a_b, left_inner_b, left_inner_t, left_a_t])
                        except Exception:
                            pass
                    if right_b_b and right_inner_b and right_inner_t and right_b_t:
                        try:
                            pygame.draw.polygon(screen, rim_color, [right_b_b, right_inner_b, right_inner_t, right_b_t])
                        except Exception:
                            pass

        if save_request is not None:
            try:
                pygame.image.save(screen, save_request)
                print(f"Saved {save_request}")
            except Exception as e:
                print("Save failed:", e)
            save_request = None

        if not saved_once:
            try:
                pygame.image.save(screen, "penrose_preview.png")
                print("Saved penrose_preview.png")
            except Exception as e:
                print("Preview save failed:", e)
            saved_once = True

        # draw minimap on top-left
        if minimap_enabled:
            mm_surf = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
            mm_surf.fill((0, 0, 0, 0))
            pygame.draw.rect(mm_surf, (25, 25, 25, 220), (0, 0, minimap_size, minimap_size))
            # draw walls scaled
            for w in walls:
                x1, y1, x2, y2 = w[0], w[1], w[2], w[3]
                mx1 = (x1 - min_x) * minimap_scale
                my1 = (y1 - min_y) * minimap_scale
                mx2 = (x2 - min_x) * minimap_scale
                my2 = (y2 - min_y) * minimap_scale
                pygame.draw.line(mm_surf, (30, 30, 30), (mx1, my1), (mx2, my2), 3)
            # player marker
            px = (cam_x - min_x) * minimap_scale
            py = (cam_y - min_y) * minimap_scale
            heading = yaw
            psize = 6
            tri = []
            for ang in (0, 2.6, -2.6):
                ax = px + math.cos(heading + ang) * psize
                ay = py + math.sin(heading + ang) * psize
                tri.append((ax, ay))
            pygame.draw.polygon(mm_surf, (240, 60, 60), tri)
            # blit minimap
            screen.blit(mm_surf, (minimap_margin, minimap_margin))

        if not headless:
            pygame.display.flip()


    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
