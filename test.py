from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random, math, time

# ---------------------------------------------------
# ULTRA 64 AUGMENTER – B3313‑Inspired Ursina Tech Demo
# Adds an N64‑style boot sequence + start‑menu *and* a
# snappy loading screen that actually boots the engine.
# ---------------------------------------------------

app = Ursina()
window.borderless   = False
window.title        = "Ultra 64 Augmenter"
window.size         = (1280, 720)
window.color        = color.rgb(100, 120, 200)
window.fps_counter.enabled = True

# Global flag so the update hook only routes to the
# player once the world exists.

_game_started = False

# ---------------------------------------------------
#  N64‑STYLE STARTUP SPLASH
# ---------------------------------------------------
startup_logo = Text(
    text="Nintendo 64",
    origin=(0, 0),
    scale=5,
    y=0.1,
    color=color.white,
    background=True,
)
# Add your own high‑fidelity chime to /assets to replace
# this silent placeholder.
Audio("n64_startup.wav", autoplay=True)

# ---------------------------------------------------
#  MAIN MENU
# ---------------------------------------------------
_menu_text = None


def _show_start_menu():
    """Replaces splash with list‑driven start menu."""
    global _menu_text
    destroy(startup_logo)

    _menu_text = Text(
        text=(
            "Ultra 64 Augmenter\n\n"
            "1  Start Game\n"
            "2  Load SM64 (stub)\n"
            "3  Options (stub)\n"
            "[X] Quit"
        ),
        origin=(0, 0),
        scale=2.5,
        y=0,
        align="center",
        color=color.white,
        background=False,
    )

    # ----------------------------
    #  MENU KEY HANDLER
    # ----------------------------
    def on_key_down(key):
        if key == "1":
            _boot_engine()
        elif key == "2":
            print("[Load SM64] Not yet implemented – stay tuned!")
        elif key == "3":
            print("[Options] Not yet implemented – stay tuned!")
        elif key in ("x", "q", "escape"):
            print("Exiting – thanks for playing!")
            application.quit()

    application.input_system.on_key_down += on_key_down


# Display menu 3 seconds after the logo.
invoke(_show_start_menu, delay=3)

# ---------------------------------------------------
#  LIGHTWEIGHT LOADING SCREEN
# ---------------------------------------------------
_loading_text = None

def _boot_engine():
    """Shows a quick loading splash, then boots the world."""
    destroy(_menu_text)

    global _loading_text
    _loading_text = Text(
        text="Loading Koopa Engine…",
        origin=(0, 0),
        scale=2,
        y=0,
        blink=True,
        background=False,
    )

    # Give Ursina a frame to paint the loading text, then
    # actually create the whole world.
    invoke(_start_game, delay=0.1)


# ---------------------------------------------------
#  GAME‑WORLD INITIALISATION
# ---------------------------------------------------


def _initialize_game_world():
    """Build Peach’s Castle hub, portals, player, etc."""
    global sky, portal_ents, player

    # Skybox
    sky = Entity(
        parent=scene,
        model="sphere",
        scale=1000,
        double_sided=True,
        color=color.lime.tint(-0.5).lerp(color.cyan, 0.7),
        texture="shore",
    )
    sky.texture_scale = (2, 2)

    # Peach’s Castle (block‑out)
    castle = Entity(
        model="cube",
        color=color.rgb(220, 210, 200),
        position=(0, 0, 0),
        scale=(30, 15, 30),
        collider="box",
    )
    Entity(model="cube", color=color.red, position=(0, 8, 0), scale=(32, 2, 32), parent=castle)
    Entity(model="cube", color=color.brown, position=(0, 0.5, 15.5), scale=(4, 7, 0.5), collider="box", parent=castle)
    for x in (-8, 0, 8):
        Entity(model="quad", color=color.azure, position=(x, 5, 15.7), scale=(2, 2, 0.1), parent=castle)

    # Portals
    portal_ents = []
    for pos, col, zone in (
        ((12, 0, 0),   color.orange,  "Backrooms"),
        ((-12, 0, 0),  color.green,   "Flooded"),
        ((0, 0, -15),  color.magenta, "Dark Realm"),
        ((0, 0, 15.7), color.yellow,  "Castle Exit"),
    ):
        portal_ents.append(Entity(model="cube", position=pos, scale=(3, 6, 1), color=col, collider="box", name=zone))

    # Player entity
    class KoopaPlayer(Entity):
        def __init__(self):
            super().__init__(
                model="cube",
                color=color.white,
                scale=(1, 2, 1),
                position=(0, 2, 10),
                collider="box",
            )
            self._vel_y            = 0
            self._grounded         = False
            self._triple_jump      = 0
            self._last_jump_time   = time.time()
            self._last_ground_time = time.time()
            self._cam_offset       = Vec3(0, 5, -18)

        def update(self):
            dt      = time.dt
            speed   = 8
            gravity = 28

            # WASD ground movement
            self.position += Vec3(
                (held_keys["d"] - held_keys["a"]) * speed * dt,
                0,
                (held_keys["w"] - held_keys["s"]) * speed * dt,
            )

            # Gravity & ground check
            if self.y > 2 or not self.intersects().hit:
                self._grounded = False
                self._vel_y   -= gravity * dt
            else:
                if not self._grounded:
                    self._grounded       = True
                    self._triple_jump    = 0
                    self._vel_y          = 0
            self.y += self._vel_y * dt

            # Camera follow
            camera.position = self.position + self._cam_offset
            camera.look_at(self.position + Vec3(0, 3, 0))

            # Jump / triple‑jump chain
            if held_keys["space"] and self._grounded and time.time() - self._last_jump_time > 0.18:
                if time.time() - self._last_ground_time < 0.35:
                    self._triple_jump += 1
                else:
                    self._triple_jump = 1
                self._last_jump_time   = time.time()
                self._last_ground_time = time.time()
                self._vel_y            = 11 + 2 * self._triple_jump
                self._grounded         = False

            # Ground‑pound
            if held_keys["ctrl"] and not self._grounded:
                self._vel_y = -30

            # Portal collision detection
            for p in portal_ents:
                if self.intersects(p).hit:
                    _teleport_zone(self, p.name)
                    break

    player = KoopaPlayer()

    # Ground plane
    Entity(model="plane", scale=(200, 1, 200), color=color.rgb(120, 180, 110), position=(0, 0, 0), collider="box")

    # Basic lighting
    AmbientLight(color=color.rgba(255, 255, 255, 220))
    DirectionalLight(y=2, z=-2, shadows=True)

    # HUD overlay
    Text(
        text="ULTRA 64 AUGMENTER  |  B3313 DEMO",
        origin=(0.5, -17),
        scale=1.5,
        position=(0, 0.48),
        background=True,
    )


# ---------------------------------------------------
#  PORTAL DESTINATION HANDLER
# ---------------------------------------------------

def _teleport_zone(player, zone):
    if zone == "Backrooms":
        player.position = (50, 2, 0)
        sky.color       = color.yellow.tint(-0.5)
        print("[Backrooms] The hum of fluorescent lights surrounds you…")
    elif zone == "Flooded":
        player.position = (-50, 2, 0)
        sky.color       = color.cyan.tint(-0.2)
        print("[Flooded] Water levels rising – better keep moving!")
    elif zone == "Dark Realm":
        player.position = (0, 2, -50)
        sky.color       = color.black
        print("[Dark Realm] Something watches from the shadows…")
    elif zone == "Castle Exit":
        player.position = (0, 2, 40)
        sky.color       = color.lime.tint(-0.3)
        print("[Overworld] Fresh air and adventure await!")


# ---------------------------------------------------
#  WORLD BOOTSTRAP & GLOBAL UPDATE LOOP
# ---------------------------------------------------

def _start_game():
    global _game_started
    if not _game_started:
        _initialize_game_world()
        _game_started = True
        destroy(_loading_text)


def update():
    # Hooked by Ursina every frame. Forward to player only once
    # the game world exists.
    if _game_started:
        player.update()


# -------------------------
#  GO! (Ursina main‑loop)
# -------------------------
app.run()
