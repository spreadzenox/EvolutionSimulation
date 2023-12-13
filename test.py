import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import pygame
from pygame.locals import *



Test_behaviour =["a","a","b","b","b","c"]
def behaviour_to_graph(liste):
	fig = pylab.figure(figsize=[4, 4], # Inches
					   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
					   )
	pylab.hist(liste)
	canvas = agg.FigureCanvasAgg(fig)
	canvas.draw()
	renderer = canvas.get_renderer()
	raw_data = renderer.tostring_rgb()
	size = canvas.get_width_height()
	surf = pygame.image.fromstring(raw_data, size, "RGB")
	return(surf)
	
	





import pygame
from pygame.locals import *

# pygame.init()

# window = pygame.display.set_mode((600, 400), DOUBLEBUF)
# screen = pygame.display.get_surface()


# screen.blit(behaviour_to_graph(Test_behaviour), (0,0))
# pygame.display.flip()

# crashed = False
# while not crashed:
# 	for event in pygame.event.get():
# 		if event.type == pygame.QUIT:
# 			crashed = True