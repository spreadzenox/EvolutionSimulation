from __future__ import annotations

import gc

import numpy as np
import pygame

from . import constants as C
from .entities import Blob, Grid
from .state import state
from .ui import (
    BackToMenuButton,
    FPSSlider,
    ImageManager,
    LightweightMonitor,
    ParameterSlider,
    PauseButton,
    StartMenu,
)


def init_pygame() -> None:
    pygame.init()
    state.WIN = pygame.display.set_mode(
        (C.WIDTH + C.WIDTH_INFO, C.HEIGHT), pygame.RESIZABLE
    )
    pygame.display.set_caption("Evolution Simulation")
    base_font_size = 16
    base_font_petit = 12
    base_font_grand = 20
    state.FONT = pygame.font.SysFont("comicsans", base_font_size)
    state.FONT_PETIT = pygame.font.SysFont("comicsans", base_font_petit)
    state.FONT_GRAND = pygame.font.SysFont("comicsans", base_font_grand)


def apply_menu_settings(menu: StartMenu) -> None:
    state.TAILLE_GRID = int(menu.sliders["TAILLE_GRID"].current_val)
    state.MAX_SPAWN_ENERGY = int(menu.sliders["BASE_ENERGY"].current_val)
    state.MUTATION_RATE = menu.sliders["MUTATION_RATE"].current_val
    state.FOOD_RATE = menu.sliders["FOOD_RATE"].current_val
    state.SPAWN_RATE = menu.sliders["SPAWN_RATE"].current_val
    state.SCAN_RANGE = int(menu.sliders["SCAN_RANGE"].current_val)
    state.CELL_SIZE = C.HEIGHT / max(state.TAILLE_GRID, 1)


def pause(run: bool) -> bool:
    return not run


def main() -> None:
    init_pygame()
    clock = pygame.time.Clock()
    state.image_manager = ImageManager()
    start_menu = StartMenu()
    # Positions and sizes will be scaled at draw time
    fps_slider = FPSSlider(C.WIDTH + C.WIDTH_INFO - 30 - 240, 150, 240, 20, 1, 120)
    monitor = LightweightMonitor()
    back_btn = BackToMenuButton(10, 10, 50)
    pause_btn = PauseButton(80, 10, 120, 40)

    rt_slider_width = 240
    rt_left_x = C.WIDTH + C.WIDTH_INFO - 30 - rt_slider_width
    rt_start_y = 320
    rt_vertical_gap = 12
    rt_slider_height = 20
    realtime_sliders = {
        "MUTATION_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 0 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.MUTATION_RATE,
            "Mutation",
            0.005,
        ),
        "FOOD_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 1 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.FOOD_RATE,
            "Food Rate",
            0.01,
        ),
        "RESET_FOOD_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 2 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            0.05,
            state.RESET_FOOD_RATE,
            "Food Reset",
            0.001,
        ),
        "SPAWN_RATE": ParameterSlider(
            rt_left_x,
            rt_start_y + 3 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            0.0,
            1.0,
            state.SPAWN_RATE,
            "Spawn Rate",
            0.01,
        ),
        "SCAN_RANGE": ParameterSlider(
            rt_left_x,
            rt_start_y + 4 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            1,
            30,
            state.SCAN_RANGE,
            "Scan Range",
            1,
        ),
        "BASE_ENERGY": ParameterSlider(
            rt_left_x,
            rt_start_y + 5 * (rt_slider_height + 40 + rt_vertical_gap),
            rt_slider_width,
            rt_slider_height,
            1,
            200,
            state.MAX_SPAWN_ENERGY,
            "Max spawn energy",
            1,
        ),
    }

    state.running = True
    state.sim_running = True
    state.turn = 0
    state.target_fps = 30
    last_update_time = 0
    update_interval = 1000 // max(state.target_fps, 1)
    memory_cleanup_counter = 0
    state.grid = Grid(list_blobs=[])
    state.grid.update_data()

    while state.running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False
                break
            if event.type == pygame.VIDEORESIZE:
                # Update window size and scale factors
                new_width, new_height = event.w, event.h
                # Constrain minimum sizes to avoid zero divisions
                new_width = max(400, new_width)
                new_height = max(400, new_height)
                state.WIN = pygame.display.set_mode(
                    (new_width, new_height), pygame.RESIZABLE
                )
                # Compute scaling relative to design reference (C.WIDTH + C.WIDTH_INFO, C.HEIGHT)
                state.SCALE_X = new_width / float(C.WIDTH + C.WIDTH_INFO)
                state.SCALE_Y = new_height / float(C.HEIGHT)
                # Update cell size according to vertical scale only to keep cells square
                effective_height = new_height
                C.HEIGHT = effective_height
                state.CELL_SIZE = effective_height / max(state.TAILLE_GRID, 1)
                if state.image_manager:
                    state.image_manager.rescale(state.CELL_SIZE)
                # Update fonts according to vertical scaling
                base_font_size = 16
                base_font_petit = 12
                base_font_grand = 20
                scaled = max(8, int(base_font_size * state.SCALE_Y))
                scaled_petit = max(6, int(base_font_petit * state.SCALE_Y))
                scaled_grand = max(10, int(base_font_grand * state.SCALE_Y))
                state.FONT = pygame.font.SysFont("comicsans", scaled)
                state.FONT_PETIT = pygame.font.SysFont("comicsans", scaled_petit)
                state.FONT_GRAND = pygame.font.SysFont("comicsans", scaled_grand)
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and state.game_state == "simulation"
            ):
                state.sim_running = pause(state.sim_running)
            if state.game_state == "menu":
                # Ensure slider positions reflect current scaling before handling events
                scale_x = state.SCALE_X or 1.0
                scale_y = state.SCALE_Y or 1.0
                current_y = int(140 * scale_y)
                for key in start_menu.slider_keys:
                    slider = start_menu.sliders[key]
                    slider.set_position(
                        int(start_menu.slider_x * scale_x),
                        current_y,
                        int(start_menu.slider_width * scale_x),
                        int(30 * scale_y),
                    )
                    current_y += slider.block_height()
                for slider in start_menu.sliders.values():
                    slider.handle_event(event)
                menu_action = start_menu.handle_event(event)
                if menu_action == "start":
                    apply_menu_settings(start_menu)
                    if state.image_manager:
                        state.image_manager.rescale(state.CELL_SIZE)
                    state.grid = Grid(list_blobs=[])
                    state.grid.update_data()
                    state.turn = 0
                    for k in (
                        "MUTATION_RATE",
                        "FOOD_RATE",
                        "SPAWN_RATE",
                        "SCAN_RANGE",
                    ):
                        realtime_sliders[k].current_val = getattr(state, k)
                    realtime_sliders["BASE_ENERGY"].current_val = state.MAX_SPAWN_ENERGY
                    state.game_state = "simulation"
            elif state.game_state == "simulation":
                # Update control positions based on current scale before handling events
                scale_x = state.SCALE_X or 1.0
                scale_y = state.SCALE_Y or 1.0
                fps_x = int((C.WIDTH + C.WIDTH_INFO - 30 - 240) * scale_x)
                fps_y = int(150 * scale_y)
                fps_slider.set_position(fps_x, fps_y)
                fps_slider.handle_event(event)
                if pause_btn.handle_event(event):
                    state.sim_running = pause(state.sim_running)
                if back_btn.handle_event(event):
                    state.game_state = "menu"
                left_x = int((C.WIDTH + C.WIDTH_INFO - 30 - rt_slider_width) * scale_x)
                start_y = int(320 * scale_y)
                vertical_gap = int(12 * scale_y)
                slider_height = int(20 * scale_y)
                for idx, (_, slider) in enumerate(realtime_sliders.items()):
                    slider.set_position(
                        left_x,
                        start_y
                        + idx * (slider_height + int(40 * scale_y) + vertical_gap),
                        int(rt_slider_width * scale_x),
                        slider_height,
                    )
                    slider.handle_event(event)

        if state.game_state == "menu":
            pass
        elif state.game_state == "simulation":
            for slider in realtime_sliders.values():
                slider.update()
            state.MUTATION_RATE = realtime_sliders["MUTATION_RATE"].current_val
            state.FOOD_RATE = realtime_sliders["FOOD_RATE"].current_val
            state.RESET_FOOD_RATE = realtime_sliders["RESET_FOOD_RATE"].current_val
            state.SPAWN_RATE = realtime_sliders["SPAWN_RATE"].current_val
            state.SCAN_RANGE = int(realtime_sliders["SCAN_RANGE"].current_val)
            state.MAX_SPAWN_ENERGY = int(realtime_sliders["BASE_ENERGY"].current_val)
            state.target_fps = fps_slider.current_fps
            update_interval = 1000 // max(state.target_fps, 1)
            if current_time - last_update_time >= update_interval:
                if state.sim_running and state.grid is not None:
                    memory_cleanup_counter += 1
                    if memory_cleanup_counter >= 100:
                        gc.collect()
                        memory_cleanup_counter = 0
                    blobs_to_process: list[Blob] = state.grid.list_blobs.copy()
                    for blob in blobs_to_process:
                        if blob in state.grid.list_blobs:
                            blob.main()
                    if state.turn % 4 == 0 and state.turn != 0:
                        state.grid.reset_food()
                    if state.turn % (1000 // C.REPRODUCE_RATE) == 0 and state.turn != 0:
                        blobs_to_reproduce = state.grid.list_blobs.copy()
                        for blob in blobs_to_reproduce:
                            if blob in state.grid.list_blobs:
                                blob.reproduce()
                    monitor.update_stats(state.grid.list_blobs, state.grid)
                    if len(state.grid.list_blobs) <= 0:
                        if state.grid.oldest_blob != 0:
                            with open("oldest.txt", "w") as file:
                                for line in state.grid.oldest_blob.brain.weight:
                                    file.write(np.array2string(line))
                        state.grid.reset_map()
                        state.game_state = "menu"
                    state.turn += 1
                last_update_time = current_time

        assert state.WIN is not None
        state.WIN.fill((0, 0, 0))
        if state.game_state == "menu":
            start_menu.draw(state.WIN)
        elif state.game_state == "simulation":
            state.grid.update_data()
            # Scale anchor positions for right panel
            monitor_x = int((C.WIDTH + 30) * (state.SCALE_X or 1.0))
            monitor_y = int(60 * (state.SCALE_Y or 1.0))
            monitor.draw(state.WIN, monitor_x, monitor_y)
            for i in range(state.TAILLE_GRID):
                for j in range(state.TAILLE_GRID):
                    current_object = state.grid.grid[i][j]
                    if current_object:
                        current_object[0].update()
                        current_object[0].draw(state.WIN)
            # Hover tooltip for blob stats
            try:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_pixel_size = int(state.CELL_SIZE * state.TAILLE_GRID)
                if 0 <= mouse_x < grid_pixel_size and 0 <= mouse_y < grid_pixel_size:
                    cell_x = int(mouse_x // max(state.CELL_SIZE, 1))
                    cell_y = int(mouse_y // max(state.CELL_SIZE, 1))
                    cell_x = max(0, min(state.TAILLE_GRID - 1, cell_x))
                    cell_y = max(0, min(state.TAILLE_GRID - 1, cell_y))
                    cell = state.grid.grid[cell_x][cell_y]
                    if (
                        cell
                        and isinstance(cell[0], Blob)
                        and state.FONT_PETIT
                        and state.FONT
                    ):
                        blob = cell[0]
                        last_beh = blob.behaviour[-1] if blob.behaviour else "none"
                        age = max(0, state.turn - blob.birth_turn)
                        # Behaviour percentages
                        perc = blob.behaviour_percentages()
                        lines = [
                            f"Blob {blob.id}",
                            f"Energy: {blob.energy}",
                            f"Age: {age}",
                            f"Last: {last_beh}",
                            "Actions:",
                            f"  manger: {perc.get('manger', 0):.0f}%   taper: {perc.get('taper', 0):.0f}%",
                            f"  bas: {perc.get('bas', 0):.0f}%      haut: {perc.get('haut', 0):.0f}%",
                            f"  droite: {perc.get('droite', 0):.0f}%  gauche: {perc.get('gauche', 0):.0f}%",
                            f"  reproduire: {perc.get('reproduire', 0):.0f}%",
                        ]
                        # Compute tooltip size
                        padding = 6
                        text_surfaces = [
                            state.FONT_PETIT.render(t, True, C.COLOR["WHITE"])
                            for t in lines
                        ]
                        width = (
                            max(ts.get_width() for ts in text_surfaces) + 2 * padding
                        )
                        height = (
                            sum(ts.get_height() for ts in text_surfaces)
                            + 2 * padding
                            + (len(lines) - 1) * 2
                        )
                        # Position tooltip near cursor, keep on-screen
                        tip_x = mouse_x + 12
                        tip_y = mouse_y + 12
                        win_w, win_h = state.WIN.get_size()
                        if tip_x + width > win_w:
                            tip_x = max(0, win_w - width - 5)
                        if tip_y + height > win_h:
                            tip_y = max(0, win_h - height - 5)
                        # Draw background and border
                        pygame.draw.rect(
                            state.WIN, (30, 30, 30), (tip_x, tip_y, width, height)
                        )
                        pygame.draw.rect(
                            state.WIN,
                            C.COLOR["LIGHT_GREY"],
                            (tip_x, tip_y, width, height),
                            1,
                        )
                        # Blit text
                        cy = tip_y + padding
                        for ts in text_surfaces:
                            state.WIN.blit(ts, (tip_x + padding, cy))
                            cy += ts.get_height() + 2
            except Exception:
                pass
            # Position FPS slider with scaling
            fps_x = int((C.WIDTH + C.WIDTH_INFO - 30 - 240) * (state.SCALE_X or 1.0))
            fps_y = int(150 * (state.SCALE_Y or 1.0))
            fps_slider.set_position(fps_x, fps_y)
            fps_slider.draw(state.WIN)
            state.current_fps = clock.get_fps()
            if state.FONT_PETIT:
                fps_text = state.FONT_PETIT.render(
                    f"Current FPS: {state.current_fps:.1f}", True, C.COLOR["ORANGE"]
                )
                state.WIN.blit(
                    fps_text,
                    (
                        int(
                            (C.WIDTH + C.WIDTH_INFO - 30 - 240) * (state.SCALE_X or 1.0)
                        ),
                        int(100 * (state.SCALE_Y or 1.0)),
                    ),
                )
            # Draw real-time sliders scaled and repositioned
            scale_x = state.SCALE_X or 1.0
            scale_y = state.SCALE_Y or 1.0
            left_x = int((C.WIDTH + C.WIDTH_INFO - 30 - rt_slider_width) * scale_x)
            start_y = int(320 * scale_y)
            vertical_gap = int(12 * scale_y)
            slider_height = int(20 * scale_y)
            for idx, (_, slider) in enumerate(realtime_sliders.items()):
                slider.set_position(
                    left_x,
                    start_y + idx * (slider_height + int(40 * scale_y) + vertical_gap),
                    int(rt_slider_width * scale_x),
                    slider_height,
                )
                slider.draw(state.WIN)
            back_btn.draw(state.WIN)
            pause_btn.draw(state.WIN, state.sim_running)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
