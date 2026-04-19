import pygame
import threading


class AsyncPygameRenderer:
    def __init__(self, width=800, height=600, fps=20, title="Game Display"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title

        self.render_list = []        # List of {image_path, x, y, (optional) scale}
        self.lock = threading.Lock()
        self.running = True
        self._image_cache = {}       # Cache loaded surfaces by path

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def update_render_list(self, render_list: list):
        """
        Called from CV thread. render_list is provided by story0.
        Expected format per entry:
            {
                "image_path": "assets/tomato.png",
                "x": 300,
                "y": 200,
                "scale": (100, 100)   # optional (w, h) in pixels
            }
        """
        with self.lock:
            self.render_list = render_list

    def _load_image(self, path, scale=None, frame=None, frame_width=None):
        """Load and cache image surfaces, slicing spritesheet if frame provided."""
        cache_key = (path, scale)
        if cache_key not in self._image_cache:
            surface = pygame.image.load(path).convert_alpha()
            self._image_cache[cache_key] = surface

        surface = self._image_cache[cache_key]

        if frame is not None and frame_width is not None:
            # Slice horizontal spritesheet
            frame_h = surface.get_height()
            rect = pygame.Rect(frame * frame_width, 0, frame_width, frame_h)
            surface = surface.subsurface(rect)

        if scale:
            surface = pygame.transform.scale(surface, tuple(scale))

        return surface

    def _run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            with self.lock:
                snapshot = list(self.render_list)

            screen.fill((20, 20, 20))

            for item in snapshot:
                try:
                    scale = item.get("scale", None)
                    frame = item.get("frame", None)
                    frame_width = item.get("frame_width", None)
                    surface = self._load_image(item["image_path"], scale, frame, frame_width)
                    screen.blit(surface, (item["x"], item["y"]))
                except Exception as e:
                    print(f"[Pygame] Render error for {item.get('image_path')}: {e}")

            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()

    def stop(self):
        self.running = False
        self.thread.join(timeout=2)