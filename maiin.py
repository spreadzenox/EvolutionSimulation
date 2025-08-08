# IMPORTS

import copy
import math
import random as rd
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pygame

from button import Button
from Pylab_to_pygame import behaviour_to_graph
from Useful_function import calculate_type_density

pygame.init()


# SIMULATION PARAMETERS

FRAMERATE: int = 30
HIT_RANGE: int = 1
EAT_RANGE: int = 3
REPRODUCE_RATE: int = 100
BASE_ENERGY: int = 30
REPRODUCE_DISTANCE: int = 3
MOOVE_SPEED: int = 1
SCAN_RANGE: int = 7
DENSITY_SCAN_RANGE: int = 10
MUTATION_RATE: float = 0.1
MUTATION_POWER: float = 0.5
FOOD_RATE: float = 0.95
RESET_FOOD_RATE: float = 0.002
BLOB_RATE: float = 1 - FOOD_RATE
SPAWN_RATE: float = 0.2
RESET_SPAWN_RATE: float = 0.001
TAILLE_GRID: int = 400


# DISPLAY PARAMETER
# CAREFUL THE MAIN WINDOW HAVE TO BE A SQUARE

WIDTH: int = 900
HEIGHT: int = 900
WIDTH_info: int = 600
CELL_SIZE: float = HEIGHT / TAILLE_GRID

WIN: pygame.Surface = pygame.display.set_mode((WIDTH + WIDTH_info, HEIGHT))

pygame.display.set_caption("Evolution Simulation")

COLOR: Dict[str, Tuple[int, int, int]] = {
    "WHITE": (255, 255, 255),
    "YELLOW": (255, 255, 0),
    "BLUE": (100, 149, 237),
    "RED": (188, 39, 50),
    "DARK_GREY": (80, 78, 81),
}

FONT: pygame.font.Font = pygame.font.SysFont("comicsans", 16)
FONT_PETIT: pygame.font.Font = pygame.font.SysFont("comicsans", 12)

# Global variables
blobs_images: List["BlobImage"] = []
grid: "Grid"
pgm_running: bool
run: bool
turn: int


# CLASS


class Grid:
    def __init__(self, list_blobs: Optional[List[Any]] = None) -> None:
        if list_blobs is None:
            list_blobs = []
        self.list_blobs: List[Any] = list_blobs
        self.oldest_blob: Any = 0
        self.better_blob: Any = 0
        self.grid: List[List[List[Any]]] = [
            [[] for i in range(TAILLE_GRID)] for j in range(TAILLE_GRID)
        ]
        for i in range(TAILLE_GRID):
            for j in range(TAILLE_GRID):
                rd_spawn = rd.random()
                rd_type = rd.random()
                if rd_spawn <= SPAWN_RATE:
                    if rd_type <= FOOD_RATE:
                        self.grid[i][j].append(Food(i, j, rd.randint(1, 8)))
                    else:
                        self.grid[i][j].append(Blob(i, j, BASE_ENERGY, grid=self))

    def instantiate(self, entity: Any) -> None:
        self.grid[entity.x][entity.y] = [entity]

    def reset_food(self) -> None:
        for i in range(TAILLE_GRID):
            for j in range(TAILLE_GRID):
                rd_spawn = rd.random()
                if rd_spawn <= RESET_FOOD_RATE:
                    if self.grid[i][j] != []:
                        if (
                            isinstance(self.grid[i][j][0], Blob)
                            and self.grid[i][j][0].energy > 0
                        ):
                            self.grid[i][j][0].suicide()
                    self.grid[i][j] = [Food(i, j, rd.randint(1, 8))]

    def reset_spawn(self, brain: Any) -> None:
        for i in range(TAILLE_GRID):
            for j in range(TAILLE_GRID):
                rd_spawn = rd.random()
                if rd_spawn <= RESET_SPAWN_RATE:
                    self.grid[i][j] = [Blob(i, j, BASE_ENERGY, brain=brain, grid=self)]

    def reset_map(self) -> None:
        self.grid = [[[] for i in range(TAILLE_GRID)] for j in range(TAILLE_GRID)]
        for i in range(TAILLE_GRID):
            for j in range(TAILLE_GRID):
                rd_spawn = rd.random()
                rd_type = rd.random()
                if rd_spawn <= SPAWN_RATE:
                    if rd_type <= FOOD_RATE:
                        self.grid[i][j].append(Food(i, j, rd.randint(1, 8)))
                    else:
                        self.grid[i][j].append(Blob(i, j, BASE_ENERGY, grid=self))

    def update_data(self) -> None:
        self.all_latest_behaviours: List[str] = []
        for blob in self.list_blobs:
            if len(blob.behaviour) >= 1:
                self.all_latest_behaviours += [blob.behaviour[-1]]
        self.list_blobs.sort(key=lambda x: len(x.behaviour))
        self.oldest_blob = self.list_blobs[-1]
        self.list_blobs.sort(key=lambda x: x.energy)
        self.better_blob = self.list_blobs[-1]


# FONCTION DE DISTANCE MODULO TAILLE_GRID
def distance(obj1: Any, obj2: Any) -> int:
    return abs(dist_x(obj1, obj2)) + abs(dist_y(obj1, obj2))


# ATTENTION CES FONCTION DONNE LES MOUVEMENTS SUR X et Y A FAIRE POUR SOURCE POUR ALLER JUSQU'A DESTINATION
def dist_x(source: Any, destination: Any) -> int:
    dist = (destination.x - source.x) % TAILLE_GRID
    absolute = abs(dist)
    if absolute > TAILLE_GRID / 2:
        return int(absolute - TAILLE_GRID)
    else:
        return int(dist)


def dist_y(source: Any, destination: Any) -> int:
    absolute = abs((destination.y - source.y) % TAILLE_GRID)
    if absolute > TAILLE_GRID / 2:
        return int(absolute - TAILLE_GRID)
    else:
        return int(absolute)


class Brain:
    def __init__(
        self, blob: Any, input_size: int = 15, output_size: int = 6, n_layer: int = 4
    ) -> None:
        self.weight: List[np.ndarray] = [
            np.random.randn(input_size, input_size) / math.sqrt(input_size)
            for i in range(n_layer)
        ] + [np.random.randn(output_size, input_size) / math.sqrt(input_size)]
        self.blob: Any = blob

    def predict(self, entree: np.ndarray) -> np.ndarray:
        r = entree
        for layer in self.weight:
            r = np.tanh(np.matmul(layer, r))
        return r


class Food:
    def __init__(self, x: int, y: int, amount: int) -> None:
        self.x: int = x
        self.y: int = y
        self.amount: int = amount
        self.color: Tuple[int, int, int] = (min(amount * 30, 255), 0, 0)
        self.radius: float = CELL_SIZE / 8 * amount / 2

    def draw(self, win: pygame.Surface) -> None:
        x_pos = self.x * CELL_SIZE + CELL_SIZE / 2
        y_pos = self.y * CELL_SIZE + CELL_SIZE / 2
        pygame.draw.circle(win, self.color, (x_pos, y_pos), self.radius)

    def update(self) -> None:
        self.color = (min([self.amount * 30, 255]), 0, 0)
        self.radius = CELL_SIZE / 8 * self.amount / 2

    def suicide(self) -> None:
        grid.grid[self.x][self.y] = []


class BlobImage:
    def __init__(
        self, x: float, y: float, radius: float, color: Tuple[int, int, int], blob: Any
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: float = radius
        self.color: Tuple[int, int, int] = color
        self.blob: Any = blob
        blobs_images.append(self)


class Blob:
    TIMESTEP: float = 0.1

    def __init__(
        self,
        x: int,
        y: int,
        energy: int,
        grid: Grid,
        brain: Any = 0,
        mutation_rate: float = 0,
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.grid: Grid = grid
        x_real: float = self.x * CELL_SIZE + CELL_SIZE / 2
        y_real: float = self.y * CELL_SIZE + CELL_SIZE / 2
        self.radius: float = CELL_SIZE / 2
        self.color: Tuple[int, int, int] = (
            0,
            min([energy * 5, 255]),
            max([0, 255 - energy * 5]),
        )
        self.energy: int = energy
        self.behaviour: List[str] = []
        self.fail: int = 0
        self.image: BlobImage = BlobImage(
            color=self.color, x=x_real, y=y_real, radius=self.radius, blob=self
        )
        if mutation_rate == 0:
            self.mutation_rate = MUTATION_RATE
        else:
            self.mutation_rate = mutation_rate
        if brain == 0:
            self.brain = Brain(blob=self)
        else:
            self.brain = brain
            self.brain.blob = self
        self.grid.list_blobs.append(self)

    def update(self) -> None:
        self.color = (0, min([self.energy * 5, 255]), max([0, 255 - self.energy * 5]))
        self.radius = CELL_SIZE / 2
        self.image.color = self.color
        x_real = self.x * CELL_SIZE + CELL_SIZE / 2
        y_real = self.y * CELL_SIZE + CELL_SIZE / 2
        self.image.x = x_real
        self.image.y = y_real
        self.image.radius = self.radius

    def draw(self, win: pygame.Surface) -> None:
        x = self.x * CELL_SIZE + CELL_SIZE / 2
        y = self.y * CELL_SIZE + CELL_SIZE / 2
        if self.energy > 0:
            pygame.draw.circle(win, self.color, (x, y), self.radius)

    def scan_near_creatures(self) -> List[Tuple[Any, int]]:
        near_list: List[Tuple[Any, int]] = []
        for i in range(-SCAN_RANGE, SCAN_RANGE):
            for j in range(-SCAN_RANGE, SCAN_RANGE):
                if abs(i) + abs(j) <= SCAN_RANGE:
                    try:
                        c = grid.grid[(self.x + i) % TAILLE_GRID][
                            (self.y + j) % TAILLE_GRID
                        ]
                        if c:
                            if type(c[0]) is Blob:
                                dist = abs(distance(self, c[0]))
                                near_list.append((c[0], dist))
                    except IndexError:
                        pass
        near_list.sort(key=lambda x: x[1])
        return near_list

    def scan_near_food(self) -> List[Tuple[Food, int]]:
        near_list: List[Tuple[Food, int]] = []
        for i in range(-SCAN_RANGE, SCAN_RANGE):
            for j in range(-SCAN_RANGE, SCAN_RANGE):
                if abs(i) + abs(j) <= SCAN_RANGE:
                    c = grid.grid[(self.x + i) % TAILLE_GRID][
                        (self.y + j) % TAILLE_GRID
                    ]
                    if c:
                        if type(c[0]) is Food:
                            dist = abs(distance(self, c[0]))
                            near_list.append((c[0], dist))
        near_list.sort(key=lambda x: x[1])
        return near_list

    def scan_food_density(self) -> List[float]:
        # CALCULTE FOOD DENSITY FOR EACH SQUARE IN EACH FOUR DIRECTIONS
        d_NE = calculate_type_density(
            self.grid.grid, self.x, self.y, "NE", DENSITY_SCAN_RANGE, Food
        )
        d_NW = calculate_type_density(
            self.grid.grid, self.x, self.y, "NW", DENSITY_SCAN_RANGE, Food
        )
        d_SE = calculate_type_density(
            self.grid.grid, self.x, self.y, "SE", DENSITY_SCAN_RANGE, Food
        )
        d_SW = calculate_type_density(
            self.grid.grid, self.x, self.y, "SW", DENSITY_SCAN_RANGE, Food
        )
        return [d_NE, d_NW, d_SE, d_SW]

    def scan_blob_density(self) -> List[float]:
        # CALCULTE FOOD DENSITY FOR EACH SQUARE IN EACH FOUR DIRECTIONS
        d_NE = calculate_type_density(
            self.grid.grid, self.x, self.y, "NE", DENSITY_SCAN_RANGE, Blob
        )
        d_NW = calculate_type_density(
            self.grid.grid, self.x, self.y, "NW", DENSITY_SCAN_RANGE, Blob
        )
        d_SE = calculate_type_density(
            self.grid.grid, self.x, self.y, "SE", DENSITY_SCAN_RANGE, Blob
        )
        d_SW = calculate_type_density(
            self.grid.grid, self.x, self.y, "SW", DENSITY_SCAN_RANGE, Blob
        )
        return [d_NE, d_NW, d_SE, d_SW]

    def moove(self, direction: int) -> int:
        self.energy -= 1
        if (
            direction == 1
            and grid.grid[self.x][(self.y + MOOVE_SPEED) % TAILLE_GRID] == []
        ):
            self.y += MOOVE_SPEED
            self.y = self.y % TAILLE_GRID
            self.fail = 0
            return 0
        elif (
            direction == 2
            and grid.grid[self.x][(self.y - MOOVE_SPEED) % TAILLE_GRID] == []
        ):
            self.y -= MOOVE_SPEED
            self.y = self.y % TAILLE_GRID
            self.fail = 0
            return 0
        elif (
            direction == 3
            and grid.grid[(self.x + MOOVE_SPEED) % TAILLE_GRID][self.y] == []
        ):
            self.x += MOOVE_SPEED
            self.x = self.x % TAILLE_GRID
            self.fail = 0
            return 0
        elif (
            direction == 4
            and grid.grid[(self.x - MOOVE_SPEED) % TAILLE_GRID][self.y] == []
        ):
            self.x -= MOOVE_SPEED
            self.x = self.x % TAILLE_GRID
            self.fail = 0
            return 0
        else:
            return 1

    def hit_closer(self) -> int:
        near_blob = self.scan_near_creatures()
        if near_blob == []:
            self.energy -= 1
            return 1
        closer_tuple = near_blob[0]
        if closer_tuple[1] < HIT_RANGE:
            closer_tuple[0].energy -= closer_tuple[0].energy
            self.energy += int(closer_tuple[0].energy * 1)
        self.energy -= 1
        self.fail = 0
        return 0

    def eat_closer(self) -> int:
        near_food = self.scan_near_food()
        if near_food == []:
            self.energy -= 1
            return 1
        for couple in near_food:
            if couple[1] < EAT_RANGE:
                self.energy += couple[0].amount
                couple[0].suicide()
                self.fail = 0
                self.energy -= 1
                return 0
        self.energy -= 1
        return 1

    def reproduce(self) -> None:
        proba = self.energy / (4 * BASE_ENERGY)
        random_truc = rd.random()
        if random_truc <= proba:
            x = rd.randint(0, 1)
            if x == 1:
                x = -REPRODUCE_DISTANCE
            elif x == 0:
                x = REPRODUCE_DISTANCE
            y = rd.randint(0, 1)
            if y == 1:
                y = -REPRODUCE_DISTANCE
            elif y == 0:
                y = REPRODUCE_DISTANCE
            interdit = list(range(0, REPRODUCE_DISTANCE)) + list(
                range(TAILLE_GRID - REPRODUCE_DISTANCE, TAILLE_GRID)
            )
            if self.x not in interdit and self.y not in interdit and self.energy > 0:
                if grid.grid[self.x + x][self.y + y] != [] and isinstance(
                    grid.grid[self.x + x][self.y + y][0], Food
                ):
                    grid.grid[self.x + x][self.y + y][0].suicide()
                new_weights = copy.deepcopy(self.brain.weight)
                for couche in new_weights:
                    for neurone in couche:
                        for poid in neurone:
                            if rd.random() <= self.mutation_rate:
                                poid += rd.gauss(0, 1) * MUTATION_POWER / (self.energy)
                new_brain = Brain(blob=self)
                new_brain.weight = new_weights
                if rd.random() <= self.mutation_rate:
                    self.mutation_rate += (
                        rd.gauss(0, 0.3) * MUTATION_POWER / (self.energy)
                    )
                new = Blob(
                    x=self.x + x,
                    y=self.y + y,
                    energy=BASE_ENERGY,
                    brain=new_brain,
                    mutation_rate=self.mutation_rate,
                    grid=self.grid,
                )
                new.brain.blob = new
                grid.instantiate(new)

    def main(self) -> None:
        # SCAN
        near_food = self.scan_near_food()
        near_blob = self.scan_near_creatures()
        # CHOICE+ACTION
        if near_food == []:
            closer_food_vector = [0, 0, 0]
        else:
            closer_food = near_food[0]
            closer_food_vector = [
                dist_x(self, closer_food[0]),
                dist_y(self, closer_food[0]),
                closer_food[0].amount,
            ]
        if near_blob == []:
            closer_blob_vector = [0, 0, 0, self.fail]
        else:
            closer_blob = near_blob[0]
            closer_blob_vector = [
                dist_x(self, closer_blob[0]),
                dist_y(self, closer_blob[0]),
                closer_blob[0].energy,
                self.fail,
            ]
        entree = (
            closer_food_vector
            + closer_blob_vector
            + self.scan_blob_density()
            + self.scan_food_density()
        )
        result = list(self.brain.predict(np.array(entree)))
        choice = result.index(max(result))
        self.consigne_behaviour(choice)
        if choice in [1, 2, 3, 4]:
            self.fail += self.moove(choice)
        if choice == 0:
            self.fail += self.eat_closer()
        if choice == 5:
            self.fail += self.hit_closer()
        if self.energy <= 0:
            self.suicide()

    def consigne_behaviour(self, choice: int) -> None:
        if choice in [1, 2, 3, 4]:
            if choice == 1:
                self.behaviour.append("bas")
            if choice == 2:
                self.behaviour.append("haut")
            if choice == 3:
                self.behaviour.append("droite")
            if choice == 4:
                self.behaviour.append("gauche")
        if choice == 0:
            self.behaviour.append("manger")
        if choice == 5:
            self.behaviour.append("taper")

    def main_behaviour(self) -> str:
        return max(set(self.behaviour), key=self.behaviour.count)

    def behaviour_recap(self) -> str:
        manger = str(self.behaviour.count("manger"))
        taper = str(self.behaviour.count("taper"))
        bas = str(self.behaviour.count("bas"))
        droite = str(self.behaviour.count("droite"))
        haut = str(self.behaviour.count("haut"))
        gauche = str(self.behaviour.count("gauche"))
        return (
            "bas= "
            + bas
            + " haut= "
            + haut
            + " droite= "
            + droite
            + " gauche= "
            + gauche
            + " taper= "
            + taper
            + " manger= "
            + manger
        )

    def suicide(self) -> None:
        grid.grid[self.x][self.y] = []
        self.grid.list_blobs.remove(self)
        blobs_images.remove(self.image)


def main() -> None:
    global pgm_running, run, blobs_images, grid, turn
    pgm_running = True
    run = True
    clock: pygame.time.Clock = pygame.time.Clock()
    blobs_images = []
    grid = Grid(list_blobs=[])
    grid.update_data()
    turn = 0
    extinc: int = 0

    def pause(run: bool) -> bool:
        if run:
            return False
        if not run:
            return True

    pause_btn: Button = Button(
        font=FONT,
        image_path="./pause.png",
        window=WIN,
        size=(50, 50),
        pos=(int(WIDTH + WIDTH_info / 2), 10),
    )
    while pgm_running:
        clock.tick(FRAMERATE)
        # ACTUAL SIMULATION STUFF
        if run:
            for blob in grid.list_blobs:
                blob.main()
            if turn % 4 == 0 and turn != 0:
                grid.reset_food()
            if turn % 40 == 0 and turn != 0:
                file = open("oldest.txt", "w")
                for line in grid.oldest_blob.brain.weight:
                    file.write(np.array2string(line))
                file.close()
            if turn % (1000 // REPRODUCE_RATE) == 0 and turn != 0:
                for blob in grid.list_blobs:
                    blob.reproduce()
            print("TOUR NUMERO" + str(turn))
            print("Generation numero" + str(turn // (1000 // REPRODUCE_RATE)))
            print("blobs en vie = " + str(len(grid.list_blobs)))
            print("extinction = " + str(extinc))
            if len(grid.list_blobs) <= 1:
                file = open("oldest.txt", "w")
                for line in grid.oldest_blob.brain.weight:
                    file.write(np.array2string(line))
                file.close()
                grid.reset_map()
                extinc += 1
            turn += 1

        # GRAPHIC UPDATES AND HUD UPDATE
        WIN.fill((0, 0, 0))
        grid.update_data()
        # HUD
        better_blob_graph = behaviour_to_graph(grid.better_blob.behaviour, 0.5)
        WIN.blit(better_blob_graph, (WIDTH + 30, 100))
        img = FONT.render("MEILLEUR BLOB BEHAVIOUR", True, COLOR["WHITE"])
        WIN.blit(img, (WIDTH + 20, 100 + better_blob_graph.get_size()[1] + 10))
        oldest_blob_graph = behaviour_to_graph(grid.oldest_blob.behaviour, 0.5)
        WIN.blit(
            oldest_blob_graph, (WIDTH + 30 + better_blob_graph.get_size()[0] + 40, 100)
        )
        img = FONT.render("OLDEST BLOB BEHAVIOUR", True, COLOR["WHITE"])
        WIN.blit(
            img,
            (
                WIDTH + 20 + better_blob_graph.get_size()[0] + 40,
                100 + oldest_blob_graph.get_size()[1] + 10,
            ),
        )
        total_behaviour_graph = behaviour_to_graph(grid.all_latest_behaviours, 0.8)
        WIN.blit(
            total_behaviour_graph,
            (WIDTH + 30, 100 + better_blob_graph.get_size()[1] + 50),
        )
        img = FONT.render("TOTAL BEHAVIOUR", True, COLOR["WHITE"])
        WIN.blit(
            img,
            (
                WIDTH + 20,
                100
                + better_blob_graph.get_size()[1]
                + 50
                + total_behaviour_graph.get_size()[1]
                + 10,
            ),
        )

        # BLOBS UPDATES
        for i in range(TAILLE_GRID):
            # pygame.draw.line(WIN,width=1,start_pos=(HEIGHT/TAILLE_GRID*i,0),color=WHITE,end_pos=(HEIGHT/TAILLE_GRID*i,HEIGHT))
            for j in range(TAILLE_GRID):
                # pygame.draw.line(WIN,width=1,start_pos=(0,(HEIGHT/TAILLE_GRID)*j),color=WHITE,end_pos=(HEIGHT,(HEIGHT/TAILLE_GRID)*j))
                current_object = grid.grid[i][j]
                if current_object:
                    current_object[0].update()
                    current_object[0].draw(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pgm_running = False
                pygame.quit()
        for blob in blobs_images:
            img = FONT_PETIT.render(str(blob.blob.energy), True, COLOR["WHITE"])
            WIN.blit(img, (blob.x, blob.y - 10))
            mouse_pos = pygame.mouse.get_pos()  # Or `pg.mouse.get_pos()`.
            # Calculate the x and y distances between the mouse and the center.
            dist_x = mouse_pos[0] - blob.x
            dist_y = mouse_pos[1] - blob.y
            # Calculate the length of the hypotenuse. If it's less than the
            # radius, the mouse collides with the circle
            if math.hypot(dist_x, dist_y) < blob.radius:
                img = FONT.render(
                    "main = " + blob.blob.main_behaviour(), True, COLOR["WHITE"]
                )
                WIN.blit(img, (blob.x, blob.y))
                img = FONT.render(
                    "last = " + blob.blob.behaviour[-1], True, COLOR["WHITE"]
                )
                WIN.blit(img, (blob.x, blob.y + 10))
                img = FONT.render(blob.blob.behaviour_recap(), True, COLOR["WHITE"])
                WIN.blit(img, (blob.x, blob.y + 20))
        pause_btn.draw()
        update_result = pause_btn.update()
        if update_result:
            print("paused")
            run = pause(run)
        pygame.display.update()
    pygame.quit()


main()
