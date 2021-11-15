import pygame
import math
import pickle
import random
vec = pygame.math.Vector2

pygame.init()
title_font = pygame.font.SysFont('Arial', 30)
font = pygame.font.SysFont('Arial', 24)
smallfont = pygame.font.SysFont('Arial', 20)

display_width = 1000
display_height = 800

settings_width = 300
settings_height = display_height

simulation_width = display_width - settings_width
simulation_height = display_height

gridSide = 200
rowLen = 6
columnLen = 6

world_width = gridSide * rowLen
world_height = gridSide * columnLen

Simulation_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Cambrians')

frames_per_second = 60

min_animals = 10

draw = True
display_settings = True

mode = 1

environment = 2

animal1 = None
animal2 = None
same_animal = False

camera_offset = [0,0]
camera_zoom = 1

reproduction_rate = 60

dead_animals_array = []
living_animals_array = []
plantsArray = []
corpseArray = []
earthArray = []

fitest_animals = []
selected_animal = []
setting_boxes = []
loaded_animals = []
fitest_stats = []
fitest_name_stats = []
herb_stats = []
carn_stats = []
hour = 1

settings_color = (49, 68, 102)
text_margin = 20
bottom_line_margin = 20
margin = 5

save_width = 120
save_height = 20

box_x = 0

box1_title = 'Fittest organism'
box1_y = 60
box1_width = settings_width
box1_height = 20
box1_open = False

box2_title = 'Selected organism'
box2_y = (box1_y + box1_height) + 20
box2_width = settings_width
box2_height = 20
box2_open = False

fitest_animals_file = 'fitest_animals'

def random_name():
	array1 = ['Vo','Ra','Ca', 'He', 'Ba', "Vi", "Lo", 'So' ]
	random1 = random.randint(0, 7)
	part1 = array1[random1]

	array2 = ['lou', "to", 'bri', 'gre', "vi", "tra", "so", 'ti', 'bi', 'ri', 'da', "do"]
	random2 = random.randint(0, 11)
	part2 = array2[random2]

	array3 = ['tus', 'ria', 'vasum', 'dadum', 'matia', 'ta', 'tum']
	random3 = random.randint(0, 6)
	part3 = array3[random3]

	array_test = random.randint(0,1000)
	if array_test < 200:
		specie_name = part1 + part3
	elif array_test <= 750:
		specie_name = part1 + part2 + part3
	else:
		specie_name = part1 + part2 + part2 + part3

	return specie_name

def calc_fitness(animal):
	return animal.birth_fitness

def reset_fitest():
	loaded_file_animals = []
	file_object = open(fitest_animals_file, 'wb')
	pickle.dump( loaded_file_animals, file_object )
	file_object.close()
	print('reset')

def save_fitest():
	global hour
	file_object = open(fitest_animals_file, 'rb')
	loaded_file_animals = pickle.load(file_object)
	loaded_file_animals.append( my_max_by_weight(fitest_animals))
	file_object = open(fitest_animals_file, 'wb')
	pickle.dump( loaded_file_animals, file_object )
	file_object.close()

	total_fitness = 0
	for fit_animal in fitest_animals:
		total_fitness += calc_fitness(fit_animal)
	median_fitness = (total_fitness / len(fitest_animals))

	print('Fitest saved')
	fitest_stats.append((hour, median_fitness))
	fitest_name_stats.append((hour, my_max_by_weight(fitest_animals).name, my_max_by_weight(fitest_animals).birthed_kin ))
	hour += 1
	print('Stats saved:')
	print(fitest_stats)

def save_selected():
	file_object = open(fitest_animals_file, 'rb')
	loaded_file_animals = pickle.load(file_object)
	loaded_file_animals.append( selected_animal[0] )
	file_object = open(fitest_animals_file, 'wb')
	pickle.dump( loaded_file_animals, file_object )
	file_object.close()
	print('Selected saved')


def load_fitest():
	global loaded_animals
	file_object = open(fitest_animals_file, 'rb')
	loaded_animals = pickle.load(file_object)
	return loaded_animals

def load_fitest_array():
	file_object = open(fitest_animals_file, 'rb')
	loaded_animals = pickle.load(file_object)
	return loaded_animals

def load_specific_fitest( number ):
	file_object = open(fitest_animals_file, 'rb')
	loaded_animals = pickle.load(file_object)
	try:
		gotdata = loaded_animals[number]
	except IndexError:
		gotdata = None
	return gotdata

def clamp(color):
	if color > 255:
		color = 255
	if color < 0:
		color = 0
	return (color, color, color)

def toggle_tab( box ):
	if box == 1:
		setting_boxes[0].box1_open = not setting_boxes[0].box1_open
		#setting other equal to false
		setting_boxes[1].box2_open = False
	if box == 2:
		setting_boxes[1].box2_open = not setting_boxes[1].box2_open
		#setting other equal to false
		setting_boxes[0].box1_open = False

def update_settings(animal):

	#calculating birth fitness for all dead organisms
	for dead_animal in dead_animals_array:
		if id(dead_animal) in animal.parents:
			dead_animal.birth_fitness += (10 / ((animal.gen - dead_animal.gen) + 1)) * animal.birthed_kin

		specie_in_fitest_array = False
		#check if same specie is better in list
		for fit_animal in fitest_animals:

			if fit_animal.name == dead_animal.name:
				if dead_animal.birth_fitness > fit_animal.birth_fitness:
					print('Better version of '+ dead_animal.name +' found! Appended and replaced.')
					fitest_animals.remove(fit_animal)
					fitest_animals.append(dead_animal)

			if fit_animal.name == animal.name:
				specie_in_fitest_array = True

		if specie_in_fitest_array == False and animal.birthed_kin > 0:
			fitest_animals.append(animal)
			print('No '+ animal.name +' in fit_list, appended.')



def my_max_by_weight(fitest_array):
	if not fitest_array:
		raise ValueError('empty fitest_array')

	maximum = fitest_array[0]

	for animal in fitest_array:
	# Compare elements by their weight stored
	# in their second element.
		if calc_fitness(animal) > calc_fitness(maximum):
			maximum = animal

	return maximum

def my_min_by_weight(fitest_array):
	if not fitest_array:
		raise ValueError('empty fitest_array')

	minimum = fitest_array[0]

	for animal in fitest_array:
	# Compare elements by their weight stored
	# in their second element.
		if calc_fitness(animal) < calc_fitness(minimum):
			minimum = animal

	return minimum

class Box1:
	def __init__(self, box_x, box1_y, box1_width, box1_height, box1_open, box1_title):
		self.box_x = box_x
		self.box1_y = box1_y
		self.box1_width = box1_width
		self.box1_height = box1_height
		self.box1_open = box1_open
		self.box1_title = box1_title

	def update_box(self):
		if self.box1_open == True:
			self.box1_height = settings_height/2
		if self.box1_open == False:
			self.box1_height = 20

	def draw_box(self):
		#fitest organism, box1
		text1 = font.render( self.box1_title, True, settings_color)
		Simulation_display.blit(text1, (self.box_x, self.box1_y))
		pygame.draw.line(Simulation_display, settings_color, (self.box_x, self.box1_y + bottom_line_margin), (settings_width - text_margin, self.box1_y + bottom_line_margin), 1 )

		if self.box1_open == True:
			if len(fitest_animals) == 0:
				selected_text = smallfont.render( 'none yet', True, settings_color)
				Simulation_display.blit(selected_text, (self.box_x + 100, self.box1_y + self.box1_height/2 - 20))
			if len(fitest_animals) > 0:

				save_text = smallfont.render( 'Save organism', True, settings_color)
				Simulation_display.blit(save_text, ((self.box1_width - (save_width/2)), self.box1_y + 20 + margin))
				#Animal preview
				selected_animal_pos_x = self.box1_width/1 - (fitest_animals[len(fitest_animals) - 1].sizeRadius) * 1.5
				selected_animal_pos_y = self.box1_y + self.box1_height/1 + (fitest_animals[len(fitest_animals) - 1].sizeRadius) * 1.5
				selected_animal_pos = (int(selected_animal_pos_x), int(selected_animal_pos_y))
				selected_animal_x_mouth = int((selected_animal_pos_x + math.cos(math.radians(-90)) * fitest_animals[len(fitest_animals) - 1].mouth_len))
				selected_animal_y_mouth = int((selected_animal_pos_y + math.sin(math.radians(-90)) * fitest_animals[len(fitest_animals) - 1].mouth_len))
				selected_animal_mouth_pos = (selected_animal_x_mouth, selected_animal_y_mouth)
				selected_animal_flagellum_len = fitest_animals[len(fitest_animals) - 1].sizeRadius + ((fitest_animals[len(fitest_animals) - 1].acc_factor * 15) + 3)
				selected_animal_flagellum_left_len = fitest_animals[len(fitest_animals) - 1].sizeRadius + (fitest_animals[len(fitest_animals) - 1].rot_speed_left * 1) + 1
				selected_animal_flagellum_right_len = fitest_animals[len(fitest_animals) - 1].sizeRadius + (fitest_animals[len(fitest_animals) - 1].rot_speed_right * 1) + 1
				#flagella
				selected_animal_flagellum_x = selected_animal_pos_x + math.cos(math.radians(-90 + 180)) * selected_animal_flagellum_len
				selected_animal_flagellum_y = selected_animal_pos_y + math.sin(math.radians(-90 + 180)) * selected_animal_flagellum_len

				#left
				selected_animal_flagellum_left_x = selected_animal_pos_x + math.cos(math.radians(-90 - 90)) * selected_animal_flagellum_left_len
				selected_animal_flagellum_left_y = selected_animal_pos_y + math.sin(math.radians(-90 - 90)) * selected_animal_flagellum_left_len

				#right
				selected_animal_flagellum_right_x = selected_animal_pos_x + math.cos(math.radians(-90 + 90)) * selected_animal_flagellum_right_len
				selected_animal_flagellum_right_y = selected_animal_pos_y + math.sin(math.radians(-90 + 90)) * selected_animal_flagellum_right_len

				pygame.draw.line(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_pos, selected_animal_mouth_pos, 2 )
				pygame.draw.circle(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_mouth_pos, fitest_animals[len(fitest_animals) - 1].mouth_radius)

				#flagellums
				pygame.draw.line(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_pos, (selected_animal_flagellum_x, selected_animal_flagellum_y), 3 )
				pygame.draw.line(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_pos, (selected_animal_flagellum_left_x, selected_animal_flagellum_left_y), 3 )
				pygame.draw.line(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_pos, (selected_animal_flagellum_right_x, selected_animal_flagellum_right_y), 3 )

				pygame.draw.circle(Simulation_display, fitest_animals[len(fitest_animals) - 1].color, selected_animal_pos, int(fitest_animals[len(fitest_animals) - 1].sizeRadius))

				name = smallfont.render( fitest_animals[len(fitest_animals) - 1].name, True, settings_color)
				Simulation_display.blit(name, (self.box_x / 4 + text_margin, self.box1_y + 20 + margin))

				fitness_text = smallfont.render( 'Fitness: ' + str(int(calc_fitness(fitest_animals[len(fitest_animals) - 1]))), True, settings_color)
				Simulation_display.blit(fitness_text, (self.box_x / 4 + text_margin, selected_animal_pos_y + 40))

class Box2:
	def __init__(self, box_x, box2_y, box2_width, box2_height, box2_open, box2_title):
		self.box_x = box_x
		self.box2_y = box2_y
		self.box2_width = box2_width
		self.box2_height = box2_height
		self.box2_open = box2_open
		self.box2_title = box2_title

	def update_box(self):
		self.box2_y = setting_boxes[0].box1_y + setting_boxes[0].box1_height + 20
		if self.box2_open == True:
			self.box2_height = settings_height/1.5
		if self.box2_open == False:
			self.box2_height = 20

	def draw_box(self):
			#selected organism, box2
		text2 = font.render( self.box2_title, True, settings_color)
		Simulation_display.blit(text2, (self.box_x, self.box2_y))
		pygame.draw.line(Simulation_display, settings_color, (self.box_x, self.box2_y + bottom_line_margin), (settings_width - text_margin, self.box2_y + bottom_line_margin), 1 )

		if self.box2_open == True:
			if selected_animal == []:
				selected_text = smallfont.render( 'no organism selected', True, settings_color)
				Simulation_display.blit(selected_text, (self.box_x + 65, self.box2_y + self.box2_height/2 - 30))
			else:

				save_text = smallfont.render( 'Save organism', True, settings_color)
				Simulation_display.blit(save_text, ((self.box2_width - (save_width/3)), self.box2_y + 30 + margin))

				#Animal preview
				selected_animal_pos_x = (settings_width/2)
				selected_animal_pos_y = self.box2_y + 80 + selected_animal[0].sizeRadius
				selected_animal_pos = (int(selected_animal_pos_x), int(selected_animal_pos_y))
				selected_animal_x_mouth = int((selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot)) * selected_animal[0].mouth_len))
				selected_animal_y_mouth = int((selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot)) * selected_animal[0].mouth_len))
				selected_animal_left_eye_x = selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot - selected_animal[0].eye_rot)) * selected_animal[0].sizeRadius
				selected_animal_left_eye_y = selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot - selected_animal[0].eye_rot)) * selected_animal[0].sizeRadius
				selected_animal_right_eye_x = selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot + selected_animal[0].eye_rot)) * selected_animal[0].sizeRadius
				selected_animal_right_eye_y = selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot + selected_animal[0].eye_rot)) * selected_animal[0].sizeRadius
				selected_animal_mouth_pos = (selected_animal_x_mouth, selected_animal_y_mouth)
				selected_animal_flagellum_len = selected_animal[0].sizeRadius + ((selected_animal[0].acc_factor * 15) + 3)
				selected_animal_flagellum_left_len = selected_animal[0].sizeRadius + (selected_animal[0].rot_speed_left * 1) + 1
				selected_animal_flagellum_right_len = selected_animal[0].sizeRadius + (selected_animal[0].rot_speed_right * 1) + 1
				#flagella
				selected_animal_flagellum_x = selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot + 180)) * selected_animal_flagellum_len
				selected_animal_flagellum_y = selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot + 180)) * selected_animal_flagellum_len

				#left
				selected_animal_flagellum_left_x = selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot - 90)) * selected_animal_flagellum_left_len
				selected_animal_flagellum_left_y = selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot - 90)) * selected_animal_flagellum_left_len

				#right
				selected_animal_flagellum_right_x = selected_animal_pos_x + math.cos(math.radians(selected_animal[0].rot + 90)) * selected_animal_flagellum_right_len
				selected_animal_flagellum_right_y = selected_animal_pos_y + math.sin(math.radians(selected_animal[0].rot + 90)) * selected_animal_flagellum_right_len

				pygame.draw.line(Simulation_display, selected_animal[0].color, selected_animal_pos, selected_animal_mouth_pos, 2 )
				pygame.draw.circle(Simulation_display, selected_animal[0].color, selected_animal_mouth_pos, selected_animal[0].mouth_radius)

				#flagellums
				pygame.draw.line(Simulation_display, selected_animal[0].color, selected_animal_pos, (selected_animal_flagellum_x, selected_animal_flagellum_y), 3 )
				pygame.draw.line(Simulation_display, selected_animal[0].color, selected_animal_pos, (selected_animal_flagellum_left_x, selected_animal_flagellum_left_y), 3 )
				pygame.draw.line(Simulation_display, selected_animal[0].color, selected_animal_pos, (selected_animal_flagellum_right_x, selected_animal_flagellum_right_y), 3 )

				pygame.draw.circle(Simulation_display, selected_animal[0].color, selected_animal_pos, int(selected_animal[0].sizeRadius))

				#eyes
				pygame.draw.circle(Simulation_display, (selected_animal[0].color[0] / 1.6, selected_animal[0].color[1] / 1.6, selected_animal[0].color[2] / 1.6), (int(selected_animal_left_eye_x), int(selected_animal_left_eye_y)), int(selected_animal[0].view_distance/50))
				pygame.draw.circle(Simulation_display, (selected_animal[0].color[0] / 1.6, selected_animal[0].color[1] / 1.6, selected_animal[0].color[2] / 1.6), (int(selected_animal_right_eye_x), int(selected_animal_right_eye_y)), int(selected_animal[0].view_distance/50))

				name = font.render(selected_animal[0].name, True, settings_color)
				Simulation_display.blit(name, (self.box_x + 4, self.box2_y + 30 + margin))

				energy_text = smallfont.render( 'Energy: ' + str(int(selected_animal[0].energy)), True, settings_color)
				Simulation_display.blit(energy_text, (self.box_x + text_margin, selected_animal_pos_y + 30))

				health_text = smallfont.render( 'Health: ' + str(int(selected_animal[0].health)), True, settings_color)
				Simulation_display.blit(health_text, (self.box_x + text_margin, selected_animal_pos_y + 50))

				age_text = smallfont.render( 'Age: ' + str(int(selected_animal[0].age / frames_per_second )) + ' seconds', True, settings_color)
				Simulation_display.blit(age_text, (self.box_x + text_margin, selected_animal_pos_y + 70))

				gen_text = smallfont.render( 'Gen: ' + str(int(selected_animal[0].gen)), True, settings_color)
				Simulation_display.blit(gen_text, (self.box_x + text_margin, selected_animal_pos_y + 90))

				if( selected_animal[0].protein_metabolism == 1 ):
					metabolism_font = 'Carnivore'
				if( selected_animal[0].protein_metabolism == 0 ):
					metabolism_font = 'Herbivore'

				metabolism_text = smallfont.render( metabolism_font, True, settings_color)
				Simulation_display.blit(metabolism_text, (self.box_x + text_margin, selected_animal_pos_y + 110))

				mutations_text = smallfont.render( 'Amount of mutations: ' + str(selected_animal[0].mutations), True, settings_color)
				Simulation_display.blit(mutations_text, (self.box_x + text_margin, selected_animal_pos_y + 150))

				mutation_rate_text = smallfont.render( 'Mutation_rate: ' + str(selected_animal[0].mutation_rate), True, settings_color)
				Simulation_display.blit(mutation_rate_text, (self.box_x + text_margin, selected_animal_pos_y + 170))


def toggle_visable_settings():
	global display_settings
	if display_settings == True:
		display_settings = False
		print('not drawing settings')
	else:
		display_settings = True
		print('drawing settings')

def draw_settings():

	if display_settings == True:

		#redrawing the settings background
		pygame.draw.rect(Simulation_display, (175, 198, 234), (0, 0, settings_width, settings_height))

		settings = title_font.render( 'Control Panel', True, settings_color)
		Simulation_display.blit(settings, (settings_width/2 - 70, 20))

		for box in setting_boxes:
			box.update_box()
			box.draw_box()

def draw_brain( input_names, output_names, input_size, hidden_sizes, output_size, weights, animal_inputs, animal_outputs, hidden_layer1, hidden_layer2):
	neuron_rad = 8
	brain_container_y = box2_y + 220

	hidden1_x = 165
	hidden2_x = 185
	hidden3_x = 195

	input_dis = 2.5
	hidden_dis = 4
	output_dis = 4
	output_margin = 0

	box2 = setting_boxes[1]

	if box2.box2_open == True:

		for c1 in range(0, input_size):
			for c2 in range(0, hidden_sizes[0]):
				pygame.draw.line(
					Simulation_display,
					(0,0,0),
					( box2.box_x + text_margin + (neuron_rad / 2) + 40, int((brain_container_y) + (c1 * input_dis * neuron_rad + ((box2.box2_height/2) - (input_size * input_dis * neuron_rad)/2))) ),
					( hidden1_x, int((brain_container_y) + (c2 * hidden_dis * neuron_rad + ((box2.box2_height/2) - (hidden_sizes[0] * hidden_dis * neuron_rad)/2))) ),
					1
					)

		for c1 in range(0, hidden_sizes[0]):
			for c2 in range(0, output_size):
				pygame.draw.line(
					Simulation_display,
					(0,0,0),
					( hidden1_x, int((brain_container_y) + (c1 * hidden_dis * neuron_rad + ((box2.box2_height/2) - (hidden_sizes[0] * hidden_dis * neuron_rad)/2))) ),
					( settings_width - text_margin - neuron_rad - 40, int((brain_container_y) + (c2 * output_dis * neuron_rad + ((box2.box2_height/2) - (output_size * output_dis * neuron_rad)/2))) ),
					1
					)

		#input_layer
		for x in range(0, input_size):
			input_name = smallfont.render( input_names[x], True, settings_color)
			Simulation_display.blit(input_name, (box2.box_x + text_margin, int((brain_container_y) + (x * input_dis * neuron_rad + ((box2.box2_height/2) - (input_size * input_dis * neuron_rad)/2) - 6))))
			pygame.draw.circle(
				Simulation_display,
				(clamp(animal_inputs[x]*(255))),
				(box2.box_x + text_margin + neuron_rad + 40, int((brain_container_y) + (x * input_dis * neuron_rad + ((box2.box2_height/2) - (input_size * input_dis * neuron_rad)/2))) ),
				neuron_rad,
				)
			pygame.draw.circle(
				Simulation_display,
				(80, 80, 80),
				(box2.box_x + text_margin + neuron_rad + 40, int((brain_container_y) + (x * input_dis * neuron_rad + ((box2.box2_height/2) - (input_size * input_dis * neuron_rad)/2))) ),
				neuron_rad,
				1
				)

		#hidden_layer1
		for x in range(0, hidden_sizes[0]):
			pygame.draw.circle(
				Simulation_display,
				(clamp(hidden_layer1[x]*(255))),
				(hidden1_x, int((brain_container_y) + (x * hidden_dis * neuron_rad + ((box2.box2_height/2) - (hidden_sizes[0] * hidden_dis * neuron_rad)/2))) ),
				neuron_rad,
				)
			pygame.draw.circle(
				Simulation_display,
				(80, 80, 80),
				(hidden1_x , int((brain_container_y) + (x * hidden_dis * neuron_rad + ((box2.box2_height/2) - (hidden_sizes[0] * hidden_dis * neuron_rad)/2))) ),
				neuron_rad,
				1
				)

		#output_layer
		for x in range(0, output_size):
			output_name = smallfont.render( output_names[x], True, settings_color)
			Simulation_display.blit(output_name, (settings_width - text_margin - 34, int((brain_container_y) + (x * output_dis * neuron_rad + ((box2.box2_height/2) - (output_size * output_dis * neuron_rad)/2) + output_margin)) ))
			pygame.draw.circle(
				Simulation_display,
				(clamp(animal_outputs[x]*(255))),
				(settings_width - text_margin - neuron_rad - 40, int((brain_container_y) + (x * output_dis * neuron_rad + ((box2.box2_height/2) - (output_size * output_dis * neuron_rad)/2)) + output_margin) ),
				neuron_rad,
				)
			pygame.draw.circle(
				Simulation_display,
				(80, 80, 80),
				(settings_width - text_margin - neuron_rad - 40, int((brain_container_y) + (x * output_dis * neuron_rad + ((box2.box2_height/2) - (output_size * output_dis * neuron_rad)/2)) + output_margin) ),
				neuron_rad,
				1
				)



class Plant:
	def __init__(self, x, y, rad):
		self.pos = vec(x,y)
		self.age = 0
		self.sizeRadius = rad

	def update_plant(self):
		if self.age > 180 * 30:
			plantsArray.remove(self)

		self.age += 1

	def draw_plant(self):
		pygame.draw.circle(Simulation_display, (0, 150, 0), (int(self.pos.x + camera_offset[0]), int(self.pos.y + camera_offset[1])), int(self.sizeRadius))

def create_plant():
	plantX = random.randint(0, world_width)
	plantY = random.randint(0, world_height)

	plant = Plant(plantX, plantY, 8)
	plantsArray.append(plant)
