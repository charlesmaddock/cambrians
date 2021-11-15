import pygame
import random
import math
import numpy
import copy
from Settings import *
from Animal import *
from Quadtree import *

pygame.init()

clock = pygame.time.Clock()

crashed = False

animal_boundry = Rectangle(0, 0, world_width, world_height)
animal_quadtree = Quadtree(animal_boundry, 4)

plant_boundry = Rectangle(0, 0, world_width, world_height)
plant_quadtree = Quadtree(plant_boundry, 4)

corpse_boundry = Rectangle(0, 0, world_width, world_height)
corpse_quadtree = Quadtree(corpse_boundry, 4)

def neuron_clamp(weight):
	if weight < 0.6 and weight > 0:
		weight = 0.6
	if weight > -0.6 and weight < 0:
		weight = -0.6
	return weight

def remove_synapses( c1, c2, weights, remove_synapse_rate ):
	#for row in range(0, c1):
	#	for number in range(0, c2):
	#		weights[row][number] = neuron_clamp(weights[row][number])
	#		if random.randint(0, remove_synapse_rate) == 0:
	#			weights[row][number] = 0
	return weights

input_size = 18
output_size = 8
hidden_sizes = [10, 9]

def create_animal():

	remove_synapse_rate = random.randint(2,20)
	
	weights = [
	numpy.random.randn(input_size, hidden_sizes[0]),
	numpy.random.randn(hidden_sizes[0], hidden_sizes[1]),
	numpy.random.randn(hidden_sizes[1], output_size),
	]

	#random start individuals
	if mode == 1:
		animal = Animal(
			random.randint(0,world_width), #x
			random.randint(0,world_height), #y
			(random.randint(50,160), random.randint(50,160), random.randint(50,160)), #color
			random_name(), #name
			random.randint(10, 16), #size
			hidden_sizes,
			weights,
			remove_synapse_rate,
			25, #eye rot
			60, #field of view
			200, #view distance
			random.randint(0, 100) / 100, #build chance
			random.randint(0, 1), #protein metabolism
			1, # generation
			random.randint(10, 30),
			[], #no parents
			0,
			)
		living_animals_array.append(animal)

	#same start individuals
	if mode == 2:
		animal = Animal(
			random.randint(0,world_width), #x
			random.randint(0,world_height), #y
			(130,70,60), #color
			'Cambria Sameus', #name
			8, #size
			hidden_sizes,
			weights,
			15, #
			25, #eye rot
			60, #field of view
			150, #view distance
			1, #build chance
			0, #protein metabolism
			1, #generation
			50, #mutation_rate
			[], #no parents
			0,
			)
		living_animals_array.append(animal)

def clear_fitest_animals():

	for animal in dead_animals_array:
		if len(dead_animals_array) > 1:
			animal.death_age += 10

			if animal.death_age > 400:
				for fit_animal in fitest_animals:
					if id(fit_animal) == id(animal):
						if fit_animal in fitest_animals:
							fitest_animals.remove(fit_animal)
				if animal in dead_animals_array:
					dead_animals_array.remove(animal)

	while len(fitest_animals) > 80:
		fitest_animals.remove(my_min_by_weight(fitest_animals))

	while len(dead_animals_array) > 300:
		dead_animals_array.remove(my_min_by_weight(dead_animals_array))

	print("*--------* Cleared bad organisms *--------*")
	print("Length dead_animals_array:")
	print(len(dead_animals_array))
	print("*-----------------------------------------*")

		#animal_extinct = True
		#for child_animal in dead_animals_array:
		#	if animal in child_animal.parents and child_animal.alive == True:
		#		animal_extinct = False

		#if animal_extinct == True:
		#	if animal in dead_animals_array:
		#		dead_animals_array.remove(animal)


def battle_royal():
	fitest_array = load_fitest_array()
	for loaded_animal in fitest_array:
		copy_respawn(loaded_animal)
	print('all loaded recreated')

def create_fitest_animal():
	#recreating fitest animals
	print('*------------------* Create fitest animal *--------------------*')

	if len(fitest_animals) > 20 and time > 60 * 60 * frames_per_second:

		carnivores = []
		herbivores = []

		all_carnivores = []
		all_herbivores = []

		for animal in fitest_animals:
			if animal.protein_metabolism == 1:
				carnivores.append(animal)
			if animal.protein_metabolism == 0:
				herbivores.append(animal)

		for animal in dead_animals_array:
			if animal.protein_metabolism == 1:
				all_carnivores.append(animal)
			if animal.protein_metabolism == 0:
				all_herbivores.append(animal)

		for x in range(0, 1):

			if len(all_carnivores) > 5:

				best_carnivore = my_max_by_weight(all_carnivores)
				copy_respawn(best_carnivore)
				print('Best carnivore recreated')

			if len(carnivores) > 5:

				parent = carnivores[random.randint( 0, len(carnivores) - 1 )]
				copy_respawn(parent)
				print('Random carnivore recreated')

		for x in range(0, 1):

			if len(all_herbivores) > 5:

				best_herbivore = my_max_by_weight(all_herbivores)
				copy_respawn(best_herbivore)
				print('Best herbivore recreated')

			if len(herbivores) > 5:

				parent = herbivores[random.randint( 0, len(herbivores) - 1 )]
				copy_respawn(parent)
				print('Random herbivore recreated')


	else:
		for x in range(1, 5):
			create_animal()
		print('Random new animals created')

	print('Fitest list length:')
	print(len(fitest_animals))
	print('Dead_animals_array length:')
	print(len(dead_animals_array))
	print('*--------------------------------------------------------------*')
	print(".")
	print(".")
	print(".")

def copy_respawn(animal_to_copy):
	### COPY ANIMAL ###
	copied_animal = copy.deepcopy(animal_to_copy)

	copied_animal.gen = 1
	copied_animal.parents = []

	copied_animal.rot = 0
	copied_animal.vel = vec(0,0)
	copied_animal.acc = vec(0,0)
	copied_animal.acc_factor = 0
	copied_animal.deacc_factor = 0
	copied_animal.rot_speed_left = 0
	copied_animal.rot_speed_right = 0

	copied_animal.selected = False

	copied_animal.age = 0
	copied_animal.birth_timer = 0
	copied_animal.birth_fitness = 0

	copied_animal.birthed_kin = 0
	copied_animal.sizeRadius = mutate_organ(copied_animal.sizeRadius, 1, 11, 16)
	copied_animal.energy = (pow(copied_animal.sizeRadius, 2) * 3.14) / 2
	copied_animal.health = pow(copied_animal.sizeRadius, 2) * 3.14
	copied_animal.pain = 0
	copied_animal.alive = True
	copied_animal.balls_eaten = 0

	copied_animal.view_distance = mutate_organ(copied_animal.view_distance, 1, 10, 250)

	#eyes
	copied_animal.eye_rot = mutate_organ(copied_animal.eye_rot, 0.6, 1, 180)
	copied_animal.FOV = mutate_organ(copied_animal.FOV, 0.6, 1, 180)

	copied_animal.mutations = copied_animal.mutations
	copied_animal.weights = [
	mutate_neuralnetwork( copied_animal, copied_animal.input_size, copied_animal.hidden_sizes[0], copied_animal.weights[0], copied_animal.mutation_rate),
	mutate_neuralnetwork( copied_animal, copied_animal.hidden_sizes[0], copied_animal.hidden_sizes[1], copied_animal.weights[1], copied_animal.mutation_rate),
	mutate_neuralnetwork( copied_animal, copied_animal.hidden_sizes[1], copied_animal.output_size, copied_animal.weights[2], copied_animal.mutation_rate),
	]

	living_animals_array.append(copied_animal)

def restart():
	#emptying lists

	living_animals_array.clear()
	plantsArray.clear()

	#creating the background color
	pygame.draw.rect(Simulation_display, (230 , 230 , 255), (0, 0, world_width + camera_offset[0], world_height + camera_offset[1]))

	#(230 , 230 , 255) water
	#(242, 203, 169) earth

	#creating initial plants


	#creating initial animals
	for x in range(0, min_animals):
		create_animal()


	load_fitest()
	print('Loaded fitest')
	print('.')

#initializing everything
restart()

time = 0
timer = 0
delete_timer = 0
minute = 0
loops = 0
opacity_timer = 0

stat_timer = 0

plant_timer = 0
plant_timer_max = 200

box1 = Box1(text_margin, 60, settings_width - text_margin * 3, 20, False, 'Fittest organism')
setting_boxes.append(box1)
box2 = Box2(text_margin, 110, settings_width - text_margin * 3, 20, False, 'Selected organism')
setting_boxes.append(box2)


		##############
		#  MAIN LOOP #
		##############


while not crashed:

	if len(living_animals_array) < min_animals:
		create_fitest_animal()

	#paint sythtic biology stuff
	#if opacity_timer == 6:
	#	s = pygame.Surface((display_width, display_height))  # the size of your rect
	##	s.set_alpha(1)                # alpha level
	#	s.fill((255,255,255))           # this fills the entire surface
	#	Simulation_display.blit(s, (0,0))    # (0,0) are the top-left coordinates
	#	opacity_timer = 0
	#opacity_timer += 1

	#redrawing the display background
	pygame.draw.rect(Simulation_display, (255 , 255 , 255), (0 , 0 , display_width, display_height))

	#redrawing the border background
	pygame.draw.rect(Simulation_display, (100 , 100 , 100), (-5 + camera_offset[0], -5 + camera_offset[1], world_width + 10, world_height + 10))

	#redrawing the world background
	pygame.draw.rect(Simulation_display, (255 , 255 , 255), (0 + camera_offset[0], 0 + camera_offset[1], world_width, world_height))

	#Recreate quadtree
	animal_boundry = Rectangle(0, 0, world_width, world_height)
	animal_quadtree = Quadtree(animal_boundry, 4)

	#Recreate quadtree
	plant_boundry = Rectangle(0, 0, world_width, world_height)
	plant_quadtree = Quadtree(plant_boundry, 4)

	#Recreate quadtree
	corpse_boundry = Rectangle(0, 0, world_width, world_height)
	corpse_quadtree = Quadtree(corpse_boundry, 4)

	#Do everything plant related
	for plant in plantsArray:
		loops += 1

		plant_quadtree.insert(plant)

		plant.update_plant()
		if plant.pos.x > -camera_offset[0] and plant.pos.x < -camera_offset[0] + display_width and plant.pos.y > -camera_offset[1] and plant.pos.y < -camera_offset[1] + display_height:
			plant.draw_plant()

	#Do everything corpse related
	for corpse in corpseArray:
		loops += 1

		corpse_quadtree.insert(corpse)

		corpse.draw_corpse()

	#Creating random plants every now and then
	if plant_timer >= plant_timer_max:
		create_plant()
		plant_timer = 0

	if draw == True:
		draw_settings()

	#First we must insert all animals into quadtree
	for animal in living_animals_array:
		animal_quadtree.insert(animal)


	#Animal gets input from environment
	for animal in living_animals_array:
		loops += 1

		animal.update()

		#check if animal is inside camera and draw
		if animal.pos.x > -camera_offset[0] and animal.pos.x < -camera_offset[0] + display_width and animal.pos.y > -camera_offset[1] and animal.pos.y < -camera_offset[1] + display_height:
			animal.draw_animal()

		if animal.think_timer == 0:

			animal.think()

			#resetting total eye intensities
			animal.left_eye_plant_intensity = 0
			animal.left_eye_kin_intensity = 0
			animal.left_eye_herbivore_intensity = 0
			animal.left_eye_predator_intensity = 0
			animal.left_eye_corpse_intensity = 0

			animal.right_eye_plant_intensity = 0
			animal.right_eye_predator_intensity = 0
			animal.right_eye_herbivore_intensity = 0
			animal.right_eye_kin_intensity = 0
			animal.right_eye_corpse_intensity = 0
			animal.left_ear = 0
			animal.right_ear = 0

			collision_range = Circle(animal.pos.x - 200, animal.pos.y - 200, 400) #27 max mouth + body range * 2
			in_range_plants = plant_quadtree.query(collision_range, [])

			#check plants for animals
			for plant in in_range_plants:
				loops += 1

				dx = animal.pos.x - plant.pos.x
				dy = animal.pos.y - plant.pos.y
				distance = math.sqrt(dx * dx + dy * dy)
				#collision
				animal.check_eye_collision( distance, plant, 'l', 'p' )
				animal.check_eye_collision( distance, plant, 'r', 'p' )

				if distance < plant.sizeRadius + animal.mouth_len + animal.mouth_radius:
					animal.check_mouth_collision(plant, animal.x_mouth, animal.y_mouth, plant.pos.x, plant.pos.y, plant.sizeRadius, 'p', "plant")

			collision_range = Circle(animal.pos.x - 200, animal.pos.y - 200, 400) #27 max mouth + body range * 2
			in_range_corpses = corpse_quadtree.query(collision_range, [])

			#check corpses for animals
			for corpse in in_range_corpses:
				loops += 1

				dx = animal.pos.x - corpse.pos.x
				dy = animal.pos.y - corpse.pos.y
				distance = math.sqrt(dx * dx + dy * dy)
				if distance < animal.view_distance:
					#mouth collision with corpse
					animal.check_eye_collision( distance, corpse, 'l', 'c' )
					animal.check_eye_collision( distance, corpse, 'r', 'c' )

					if distance < corpse.sizeRadius + animal.mouth_len + animal.mouth_radius:
						animal.check_mouth_collision(corpse, animal.x_mouth, animal.y_mouth, corpse.pos.x, corpse.pos.y, corpse.sizeRadius, 'c', corpse.name)


			viewing_range = Circle(animal.pos.x - 200, animal.pos.y - 200, 400) #400 max viewing range * 2
			in_range_animals = animal_quadtree.query(viewing_range, [])

			#check other animals for animal
			for animal2 in in_range_animals:
				loops += 1

				dx = animal.pos.x - animal2.pos.x
				dy = animal.pos.y - animal2.pos.y
				distance = math.sqrt(dx * dx + dy * dy)
				if distance < animal.view_distance and animal2 != animal:

					animal.check_animal_mouth_collision( animal2, animal.x_mouth, animal.y_mouth, animal2.pos.x, animal2.pos.y, animal2.sizeRadius)

					animal.check_hearing( distance, animal2, 'l' )
					animal.check_hearing( distance, animal2, 'r' )

					animal.check_eye_collision( distance, animal2, 'l', 'ak' )
					animal.check_eye_collision( distance, animal2, 'r', 'ak' )

					animal.check_eye_collision( distance, animal2,'l', 'a' )
					animal.check_eye_collision( distance, animal2, 'r', 'a' )

		#now that we have all the vaules, draw brain in settings.
		if animal.selected == True:
			animal_inputs = [
			animal.left_eye_plant_intensity,
			animal.right_eye_plant_intensity,
			animal.left_eye_corpse_intensity,
			animal.right_eye_corpse_intensity,
			animal.left_eye_herbivore_intensity,
			animal.right_eye_herbivore_intensity,
			animal.left_eye_predator_intensity,
			animal.right_eye_predator_intensity,
			animal.left_eye_kin_intensity,
			animal.right_eye_kin_intensity,
			animal.left_ear,
			animal.right_ear,
			(animal.pain),
			(animal.energy / (pow(animal.sizeRadius, 2) * 3.14)) / 3,
			(animal.health / (pow(animal.sizeRadius, 2) * 3.14)),
			(animal.birth_timer / frames_per_second) / animal.birth_timer_max,
			animal.h_A_in,
			animal.h_B_in,
			]
			animal_outputs = [
			animal.acc_factor,
			animal.deacc_factor,
			animal.rot_speed_left,
			animal.rot_speed_right,
			animal.mouth_extention / (animal.sizeRadius * 1.5),
			animal.birth_p,
			animal.h_A_out,
			animal.h_B_out,
			]

			if display_settings == True:
				draw_brain(
				animal.input_names,
				animal.output_names,
				animal.input_size,
				animal.hidden_sizes,
				animal.output_size,
				animal.weights,
				animal_inputs,
				animal_outputs,
				animal.hidden_layer1,
				animal.hidden_layer2,
				)


		#if the animal leaves the screen
		#x
		if animal.pos.x < 0:
			animal.pos.x = world_width

		if animal.pos.x > world_width:
			animal.pos.x = 0
		#y
		if animal.pos.y < 0:
			animal.pos.y = world_height

		if animal.pos.y > world_height:
			animal.pos.y = 0

	#move camera
	keys = pygame.key.get_pressed()
	if keys[pygame.K_UP]:
		camera_offset[1] += 40
	if keys[pygame.K_DOWN]:
		camera_offset[1] -= 40
	if keys[pygame.K_LEFT]:
		camera_offset[0] += 40
	if keys[pygame.K_RIGHT]:
		camera_offset[0] -= 40

	for event in pygame.event.get():

		if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_q:
			crashed = True
		if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
			reset_fitest()

		if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
			toggle_visable_settings()

		if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
			min_animals -= 1
			print('min_animals:')
			print(min_animals)
		if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
			min_animals += 1
			print('min_animals:')
			print(min_animals)

		if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
			plant_timer_max -= 4
			print('plant_timer_max:')
			print(plant_timer_max)
		if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
			plant_timer_max += 4
			print('plant_timer_max:')
			print(plant_timer_max)

		if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
			frames_per_second += 10
			print('frames_per_second:')
			print(frames_per_second)
		if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
			frames_per_second -= 10
			print('frames_per_second:')
			print(frames_per_second)

		if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
			world_height -= 200
			print('world_height:')
			print(world_height)
		if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
			world_width -= 200
			print('world_width:')
			print(world_width)

		if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
			reproduction_rate -= 1
			print('reproduction_rate:')
			print(reproduction_rate)
		if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
			reproduction_rate += 1
			print('reproduction_rate:')
			print(reproduction_rate)

		if event.type == pygame.KEYDOWN and event.key == pygame.K_0:
			battle_royal()

		if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
			save_selected()

		if event.type == pygame.KEYDOWN and event.key == pygame.K_8:
			pygame.display.set_mode((1, 1))

		if event.type == pygame.KEYDOWN and event.key == pygame.K_9:
			pygame.display.set_mode((display_width, display_height))

		if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
			print('*------------------* INFO *--------------------*')

			print('Fitest list length:')
			print(len(fitest_animals))
			print(".")
			print('living_animals_array length:')
			print(len(living_animals_array))
			print('.')
			print('Dead_animals_array length:')
			print(len(dead_animals_array))
			print('.')
			print('Stats:')
			print(fitest_stats)
			print(".")
			#print('Fitest array fitnesses:')
			species = []
			for x in range(0,(len(fitest_animals)-1)):
				if fitest_animals[x].name not in species:
					species.append(fitest_animals[x].name)
			#	print(fitest_animals[x].name)
			#	print(fitest_animals[x].birth_fitness)
			#	print('.')
			#print(".")
			print('fps:')
			print(clock.get_fps())
			print('.')
			print('loops:')
			print(loops)
			print('.')
			print('Amount of species in fitest array:')
			print(len(species))
			print(".")


			print('herb_stats:')
			print(herb_stats)
			print(".")

			print('carn_stats:')
			print(carn_stats)
			print(".")

			print('amount of plants:')
			print(len(plantsArray))
			print('*----------------------------------------------*')
			print(".")
			print(".")
			print(".")

		if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
			clear_fitest_animals()

		if event.type == pygame.MOUSEBUTTONDOWN:
			for animal in living_animals_array:
				mouse_pos = pygame.mouse.get_pos()
				mouse_x = mouse_pos[0] - camera_offset[0]
				mouse_y = mouse_pos[1] - camera_offset[1]
				dx = mouse_x - animal.pos.x
				dy = mouse_y - animal.pos.y
				distance = math.sqrt(dx * dx + dy * dy)
				if distance < (animal.sizeRadius + 10) and animal.selected == False:
					for listanimal in living_animals_array:
						listanimal.selected = False
					animal.selected = True
					selected_animal.clear()
					selected_animal.append(animal)

		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_pos = pygame.mouse.get_pos()
			mouse_x = mouse_pos[0]
			mouse_y = mouse_pos[1]

			box1 = setting_boxes[0]
			box2 = setting_boxes[1]

			#box collisions
			if mouse_x > box1.box_x and mouse_x < box1.box1_width and mouse_y > box1.box1_y and mouse_y < box1.box1_y + 20:
				toggle_tab(1)

			if mouse_x > box2.box_x and mouse_x < box2.box2_width and mouse_y > box2.box2_y and mouse_y < box2.box2_y + 20:
				toggle_tab(2)

	if timer == 20 * 60 * frames_per_second:
		create_fitest_animal()
		timer = 0

	if delete_timer == 10 * 60 * frames_per_second:
		delete_timer = 0
		clear_fitest_animals()


	carnivores = []
	herbivores = []

	for animal in living_animals_array:
		if animal.protein_metabolism == 1:
			carnivores.append(animal)
		if animal.protein_metabolism == 0:
			herbivores.append(animal)

	if len(carnivores) < 3 and time > 60 * 60 * 60:
		all_carnivores = []

		for animal in dead_animals_array:
			if animal.protein_metabolism == 1:
				all_carnivores.append(animal)

		best_carnivore = my_max_by_weight(all_carnivores)
		copy_respawn(best_carnivore)
		print('Best carnivore recreated')


	if stat_timer == 60 * 60 * frames_per_second:


		#minute += 30
		#herb_stats.append((minute, len(herbivores)))
		#carn_stats.append((minute, len(carnivores)))
		save_fitest()
		stat_timer = 0

	timer += 1
	stat_timer += 1
	delete_timer += 1
	plant_timer += 1
	time += 1
	loops = 0

	pygame.display.update()

	clock.tick(frames_per_second)


pygame.quit()
quit()
#bigg peepee code Gustav 2018
