from typing import Any, Optional, Tuple

import pygame

global WIDTH_info
global HEIGHT_info
WIDTH_info, HEIGHT_info = 300, 300
WIN_info = pygame.display.set_mode((WIDTH_info, HEIGHT_info))

pygame.init()
global FONT
FONT = pygame.font.SysFont("comicsans", 16)


buttons: pygame.sprite.Group = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    """Create a button clickable with changing hover color"""

    def __init__(
        self,
        font: pygame.font.Font,
        image_path: str,
        window: pygame.Surface,
        size: Tuple[int, int] = (50, 50),
        text: str = "Click",
        pos: Tuple[int, int] = (0, 0),
    ) -> None:
        super().__init__()
        self.text = text
        self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        self.window = window
        self.font = font
        self.pos = pos
        self.size = size
        self.pressed: int = 1
        self.create_original()

    def create_original(self) -> None:
        self.bg = self.create_bg()
        self.original_image = self.image.copy()

    def create_bg(self) -> pygame.Surface:
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos
        bgo = pygame.Surface((self.rect.w, self.rect.h))
        bgo.blit(self.image, (0, 0))
        return bgo

    def update(self, *args: Any, **kwargs: Any) -> Optional[bool]:
        """CHECK IF HOVER AND IF CLICK THE BUTTON"""
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return self.check_if_click()
        return None

    def check_if_click(self) -> Optional[bool]:
        """checks if you click on the button and makes the call to the action just one time"""
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] and self.pressed == 1:
                self.pressed = 0
                return True
            if pygame.mouse.get_pressed() == (0, 0, 0):
                self.pressed = 1
        return None

    def draw(self) -> None:
        self.window.blit(self.image, self.pos)


# if __name__ == "__main__":
# # Hello, this is a snippet

#     pygame.init()

#     pygame.display.set_caption('Example of button')
#     screen = WIN_info
#     clock = pygame.time.Clock()
#     b1 = Button(font=FONT,image_path="./pause.png",window=screen, pos=(0,0),
#         command=lambda: print("clicked right now"))


#     is_running = True
#     while is_running:
#         screen.fill((255, 255, 255))
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 is_running = False

#         b1.draw()
#         b1.update()
#         pygame.display.update()
#         clock.tick(60)

#     pygame.quit()
