import math
import random
import pygame
import numpy
from Settings import *
vec = pygame.math.Vector2
import copy

pygame.init()

class Earth:
	def __init__(self, x, y, sizeRadius):
		self.pos = vec(x,y)
		self.sizeRadius = sizeRadius

	def draw_earth(self):
		pygame.draw.circle(Simulation_display, (53, 40, 28), (int(self.pos.x + camera_offset[0]), int(self.pos.y + camera_offset[1])), int(self.sizeRadius))

def create_earth(x,y,sizeRadius):
	earth = Earth(x, y, sizeRadius)
	earthArray.append(earth)

class Corpse:
	def __init__(self, x, y, sizeRadius, energy, name):
		self.pos = vec(x,y)
		self.sizeRadius = sizeRadius
		self.energy = pow(sizeRadius, 2) * 3.14 
		self.age = 0
		self.name = name

	def draw_corpse(self):
		pygame.draw.circle(Simulation_display, (138,7,7), (int(self.pos.x + camera_offset[0]), int(self.pos.y + camera_offset[1])), int(self.sizeRadius))
		self.age += 1
		if self.age > 180 * 30:
			corpseArray.remove(self)

def create_corpse(x,y,sizeRadius, energy, name):
	corpse = Corpse(x, y, sizeRadius, energy, name)
	corpseArray.append(corpse)

def sigmoid(x):
	return (1/(1 + numpy.exp( 1.5 - 2*x )))

def mutate_organ(organ, division_factor, minVal, maxVal):
	mutation = 0
	if random.randint(0, 7) == 1:
		mutation = (random.randint(-3,3))

	if random.randint(0, 14) == 1:
		mutation = (random.randint(-9,9)) 

	mutated_organ = organ + (mutation / division_factor)

	#if mutation is too large or small return no mutation
	if mutated_organ <= minVal or mutated_organ > maxVal:
		return organ
	else:
		return mutated_organ


def mutate_neuralnetwork(self, c1, c2, weights, rate):
	new_weights = weights
	if random.randint(0,1) == 1:
		self.mutations += 1
		for row in range(0, c1):
			for number in range(0, c2):

				#change all with very small value
				if new_weights[row][number] > -3:
					new_weights[row][number] = new_weights[row][number] + (random.randint(-100, 0) / 2000) 
				if new_weights[row][number] < 3:
					new_weights[row][number] = new_weights[row][number] + (random.randint(0, 100) / 2000) 

				#change 10 % completely
				if random.randint(0, rate) == 0:
					new_weights[row][number] = numpy.random.randn()

	if random.randint(0,14) == 1:
		self.mutations += 1
		for row in range(0, c1):
			for number in range(0, c2):
				if random.randint(0, 4) == 0:
					new_weights[row][number] = numpy.random.randn()

	return new_weights
	

def mutate_metabolism(metabolism):
	if metabolism == 1:
		if random.randint(0,2) == 0:
			metabolism = 0
	if metabolism == 0:
		if random.randint(0,2) == 0:
			metabolism = 1
	return metabolism

class Animal:

	def __init__(self, x, y, color, name, sizeRadius, hidden_sizes, weights, remove_synapse_rate, eye_rot, FOV, view_distance, build_chance, protein_metabolism, gen, mutation_rate, parents, mutations):
		self.rot = 0
		self.pos = vec(x,y)
		self.vel = vec(0,0)
		self.acc = vec(0,0)
		self.fric = -0.2
		self.acc_factor = 0
		self.deacc_factor = 0
		self.rot_factor = 10
		self.rot_speed_left = 0
		self.rot_speed_right = 0
		self.color = color

		self.age = 0
		self.death_age = 0
		self.birth_timer = 0
		self.parents = parents
		self.birth_fitness = 0

		self.gen = gen
		self.mutation_rate = mutation_rate
		self.birthed_kin = 0
		self.birth_p = 0
		self.protein_metabolism = protein_metabolism
		self.birth_timer_max = 80
		self.sizeRadius = mutate_organ(sizeRadius, 1, 6, 12)
		self.energy = (pow(self.sizeRadius, 2) * 3.14) / 2
		self.health = pow(self.sizeRadius, 2) * 3.14
		self.pain = 0
		self.alive = True
		self.balls_eaten = 0
		self.h_A_out = 0
		self.h_B_out = 0
		self.h_A_in = 0
		self.h_B_in = 0

		self.build_intensity = 0
		self.build_chance = build_chance
		self.plant_p = 0

		self.name = name

		self.view_distance = mutate_organ(view_distance, 1, 10, 200)
		
		self.selected = False

		#eyes
		self.eye_rot = mutate_organ(eye_rot, 0.4, 1, 180)
		self.left_eye_rot = self.eye_rot
		self.right_eye_rot = self.eye_rot
		self.FOV = mutate_organ(FOV, 0.4, 1, 180)

		self.left_eye_rot_intesity = 0
		self.right_eye_rot_intesity = 0

		self.left_ear = 0
		self.right_ear = 0

		#left eye
		self.left_eye_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot)) * self.sizeRadius
		self.left_eye_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot)) * self.sizeRadius
		self.left_cone1_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot + self.FOV/2)) * self.view_distance
		self.left_cone1_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot + self.FOV/2)) * self.view_distance
		self.left_cone2_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot - self.FOV/2)) * self.view_distance
		self.left_cone2_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot - self.FOV/2)) * self.view_distance
		self.left_eye_plant_intensity = 0
		self.left_eye_kin_intensity = 0
		self.left_eye_predator_intensity = 0
		self.left_eye_herbivore_intensity = 0
		self.left_eye_corpse_intensity = 0

		#right eye
		self.right_eye_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot)) * self.sizeRadius
		self.right_eye_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot)) * self.sizeRadius
		self.right_cone1_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot + self.FOV/2)) * self.view_distance
		self.right_cone1_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot + self.FOV/2)) * self.view_distance
		self.right_cone2_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot - self.FOV/2)) * self.view_distance
		self.right_cone2_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot - self.FOV/2)) * self.view_distance
		self.right_eye_plant_intensity = 0
		self.right_eye_kin_intensity = 0
		self.right_eye_predator_intensity = 0
		self.right_eye_herbivore_intensity = 0
		self.right_eye_corpse_intensity = 0

		#flagellum
		self.flagellum_len = self.sizeRadius + ((self.acc_factor * (self.sizeRadius * 4) + (self.sizeRadius / 3)))
		self.flagellum_left_len = self.sizeRadius + (self.rot_speed_left * (self.sizeRadius) + (self.sizeRadius / 5))
		self.flagellum_right_len = self.sizeRadius + (self.rot_speed_right * (self.sizeRadius) + (self.sizeRadius / 5))
		self.flagellum_width = int((self.sizeRadius / 6) + 1 ) 

		#mouth
		self.mouth_extention = 0
		self.mouth_len = 0
		self.mouth_radius = int(self.sizeRadius/12) 
		self.x_mouth = self.pos.x + math.cos(math.radians(self.rot)) * self.mouth_len
		self.y_mouth = self.pos.y + math.sin(math.radians(self.rot)) * self.mouth_len

		#neural network
		self.think_timer = 0
		self.think_timer_max = 3
		self.input_size = 18
		self.output_size = 8
		self.hidden_sizes = [ 
		hidden_sizes[0], 
		hidden_sizes[1], 
		#hidden_sizes[2] 
		]
		self.remove_synapse_rate = remove_synapse_rate

		#this one is for draw brain
		self.hidden_layer1 = []
		self.hidden_layer2 = []

		self.input_names = [
		'LE_p',
		'RE_p',
		'LE_c',
		'RE_c',
		'LE_he',
		'RE_he',	
		'LE_pr',
		'RE_pr',	
		'LE_k',
		'RE_k',
		'L_ear',
		'R_ear',
		'Pain',
		'Enrgy',
		'Health',
		'B_timer',
		'h_A_in',
		'h_B_in',
		]

		self.output_names = [
		'Acc',
		'Deacc',
		'L_rot',
		'R_rot',
		'M_len',
		'Birth_p',
		'h_A_out',
		'h_B_out',
		]

		self.mutations = mutations
		self.weights = [ 
		mutate_neuralnetwork( self, self.input_size, self.hidden_sizes[0], weights[0], self.mutation_rate), 
		mutate_neuralnetwork( self, self.hidden_sizes[0], self.hidden_sizes[1], weights[1], self.mutation_rate), 
		mutate_neuralnetwork( self, self.hidden_sizes[1], self.output_size, weights[2], self.mutation_rate), 
		#mutate_neuralnetwork( self, self.hidden_sizes[2], self.output_size, weights[3], self.mutation_rate), 
		]

	def eat(self, energy ):
		self.energy += energy

	def die(self):
		create_corpse(self.pos.x, self.pos.y, self.sizeRadius, self.energy, id(self))
		living_animals_array.remove(self)
		if self.selected == True:
			selected_animal.clear()
		self.alive = False
		dead_animals_array.append(self)
		update_settings(self)

	def check_hearing( self, distance, obj, side ):
		obj_deg = math.degrees(math.atan2(obj.pos.y - self.pos.y, obj.pos.x - self.pos.x))
		if obj_deg < 0:
			obj_deg = obj_deg + 360

		if side == 'l':
			if obj_deg > self.rot - 180 and obj_deg < self.rot:
				self.left_ear = ((self.view_distance - distance) / self.view_distance) * 1.5 * abs(obj.acc_factor - obj.deacc_factor)

		if side == 'r':
			if obj_deg > self.rot and obj_deg < self.rot + 180:
				self.right_ear = ((self.view_distance - distance) / self.view_distance) * 1.5 * abs(obj.acc_factor - obj.deacc_factor)

	def check_mouth_collision( self, obj, x0, y0, x1, y1, obj_rad, obj_type, obj_id):
		dx = x1 - x0
		dy = y1 - y0
		distance = math.sqrt(dx * dx + dy * dy)
		if obj_type == 'p':
			if obj_rad + self.mouth_radius >= distance and obj in plantsArray:
				if self.energy < (pow(self.sizeRadius,2) * 3.14) * 3:
					self.eat( ((pow(obj_rad, 2) * 3.14 ) * 1.5) * (1 - self.protein_metabolism))
				#if obj in plantsArray:
				plantsArray.remove(obj)
				self.balls_eaten += 1

		if obj_type == 'c':
			if obj_rad + self.mouth_radius >= distance and self.energy < (pow(self.sizeRadius,2) * 3.14) * 3 and obj in corpseArray:
				if id(self) != obj_id:
					if self.protein_metabolism == 1:
						self.eat((obj.energy * self.protein_metabolism / 1.6))
					else:
						self.health -= obj_rad
					corpseArray.remove(obj)			

	def check_animal_mouth_collision( self, animal, x0, y0, x1, y1, animal_rad):
		dx = x1 - x0
		dy = y1 - y0
		distance = math.sqrt(dx * dx + dy * dy)
		if animal_rad + self.mouth_radius >= distance:

			if self.acc_factor > 0.3 and self.mouth_len > self.sizeRadius:

				if self.protein_metabolism == 1:
					animal.health -= (abs((self.acc_factor - self.deacc_factor)) * self.sizeRadius * 2) + 0.8
					animal.pain = ((pow(animal.sizeRadius, 2) * 3.14) - abs((self.acc_factor - self.deacc_factor))) / (pow(animal.sizeRadius, 2) * 3.14)
				else:
					animal.health -= (abs((self.acc_factor - self.deacc_factor)) * self.sizeRadius )
					animal.pain = ((pow(animal.sizeRadius, 2) * 3.14) - abs((self.acc_factor - self.deacc_factor))) / (pow(animal.sizeRadius, 2) * 3.14)

	def check_eye_collision(self, distance, obj, eye, obj_type):
		obj_deg = math.degrees(math.atan2(obj.pos.y - self.pos.y, obj.pos.x - self.pos.x))
		if obj_deg < 0:
			obj_deg = obj_deg + 360

		if eye == 'l':
			if obj_deg > self.rot - self.left_eye_rot - self.FOV/2 and obj_deg < self.rot - self.left_eye_rot + self.FOV/2:
				if obj_type == 'p':
					self.left_eye_plant_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
				elif obj_type == 'ak':
					if obj.name == self.name:
						self.left_eye_kin_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
				elif obj_type == 'a':
					if obj.name != self.name:
						if obj.protein_metabolism == 1:
							self.left_eye_predator_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
						elif obj.protein_metabolism == 0:
							self.left_eye_herbivore_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
				elif obj_type == 'c':
						self.left_eye_corpse_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2

		if eye == 'r':
			if obj_deg > self.rot + self.right_eye_rot - self.FOV/2 and obj_deg < self.rot + self.right_eye_rot + self.FOV/2:
				if obj_type == 'p':
					self.right_eye_plant_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2 
				elif obj_type == 'ak':
					if obj.name == self.name:
						self.right_eye_kin_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
				elif obj_type == 'a':
					if obj.name != self.name:
						if obj.protein_metabolism == 1:
							self.right_eye_predator_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
						elif obj.protein_metabolism == 0:
							self.right_eye_herbivore_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2
				elif obj_type == 'c':
						self.right_eye_corpse_intensity += ((self.view_distance - distance) / self.view_distance) * 1.5 + 0.2


	#neural network functions
	def think(self):
		inputs = [
		self.left_eye_plant_intensity, 
		self.right_eye_plant_intensity,
		self.left_eye_corpse_intensity, 
		self.right_eye_corpse_intensity,
		self.left_eye_herbivore_intensity,
		self.right_eye_herbivore_intensity,
		self.left_eye_predator_intensity,
		self.right_eye_predator_intensity,
		self.left_eye_kin_intensity,
		self.right_eye_kin_intensity,
		self.left_ear,
		self.right_ear,
		self.pain,
		(self.energy / (pow(self.sizeRadius, 2) * 3.14) * 3), #a percent of how much energy the animal has lost
		(self.health / (pow(self.sizeRadius, 2) * 3.14)),
		sigmoid((self.birth_timer / frames_per_second) / self.birth_timer_max),
		self.h_A_in,
		self.h_B_in,
		]
		
		#z = sigmoid(numpy.dot(inputs, self.weights[0]))
		z = numpy.dot(inputs, self.weights[0])
		self.hidden_layer1 = sigmoid(z)

		z2 = numpy.dot(z, self.weights[1])
		z3 = sigmoid(z2)
		#self.hidden_layer2 = z3
		#z4 = numpy.dot(z2, self.weights[2])
		#outputs = sigmoid(z4)
		outputs = z3

		if outputs[0] <= 0.8:
			self.acc_factor = pow(outputs[0]*1.3 ,2)
		else:
			self.acc_factor = pow(outputs[0]*1.8 ,2)
		self.deacc_factor = outputs[1]  
		self.rot_speed_left = outputs[2] * 2
		self.rot_speed_right = outputs[3] * 2
		self.mouth_extention = outputs[4] * self.sizeRadius 
		self.birth_p = outputs[5]
		self.h_A_out = outputs[6]
		self.h_B_out = outputs[7]

	def update(self):

		self.think_timer += 1
		if self.think_timer > self.think_timer_max:
			self.think_timer = 0


				###INPUTS###
		#Animal movement
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a]:
			#Left output
			self.rot -= 10
			if self.rot_speed_left > 2:
				self.rot_speed_left += 0.2
		if keys[pygame.K_d]:
			#Right output
			self.rot += 10
			if self.rot_speed_right > 2:
				self.rot_speed_right += 0.2
		if keys[pygame.K_w]:
			#Forward output
			if self.acc_factor < 1:
				self.acc_factor += 1
		if keys[pygame.K_s]:
			#Forward output
			if self.acc_factor > 0.1:
				self.acc_factor -= 1

				###OUTPUTS###
		#rotation
		self.rot += ((self.rot_speed_right * self.rot_factor) - (self.rot_speed_left * self.rot_factor))
		if self.rot > 360:
			self.rot = 0 + self.rot_speed_left
		if self.rot < 0:
			self.rot = 360 - self.rot_speed_right
		
		#forward/backward movement
		self.acc.x = math.cos(math.radians(self.rot)) * ((self.acc_factor - self.deacc_factor)) / 2
		self.acc.y = math.sin(math.radians(self.rot)) * ((self.acc_factor - self.deacc_factor)) / 2
		self.acc += self.vel * self.fric
		self.vel += self.acc
		self.pos += self.vel + ((self.acc_factor - self.deacc_factor)) * self.acc

		###Updating limbs###

		#mouth
		self.mouth_len = ((self.mouth_extention + self.sizeRadius) - (self.sizeRadius/2)) * 1.5
		self.x_mouth = self.pos.x + math.cos(math.radians(self.rot)) * self.mouth_len
		self.y_mouth = self.pos.y + math.sin(math.radians(self.rot)) * self.mouth_len


		if self.selected == True:
			self.left_cone1_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot + self.FOV/2)) * self.view_distance
			self.left_cone1_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot + self.FOV/2)) * self.view_distance
			self.left_cone2_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot - self.FOV/2)) * self.view_distance
			self.left_cone2_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot - self.FOV/2)) * self.view_distance

			self.right_cone1_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot + self.FOV/2)) * self.view_distance
			self.right_cone1_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot + self.FOV/2)) * self.view_distance
			self.right_cone2_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot - self.FOV/2)) * self.view_distance
			self.right_cone2_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot - self.FOV/2)) * self.view_distance
		
		#asexual reproduction
		if self.energy > (pow(self.sizeRadius, 2) * 3.14 )/2 and self.birth_timer > (frames_per_second * self.birth_timer_max) and self.birth_p > 0.3:
			self.birthed_kin += 1
			self.energy -= (pow(self.sizeRadius, 2) * 3.14 ) / 1.5
			self.birth_timer = 0

			self.copy_animal()

		#hormone A, so if h_A_out is greater than a certain value, it gets fed into inputs as h_A_in
		if self.h_A_out > 0.7 and self.h_A_in < 1:
			self.h_A_in += 0.1
		self.h_A_in -= 0.01

		#hormone B
		if self.h_B_out > 0.7 and self.h_B_in < 1:
			self.h_B_in += 0.1
		self.h_B_in -= 0.003

		#energy
		if self.energy > 0:
			if self.health < (pow(self.sizeRadius, 2) * 3.14):
				self.health += 0.03

			if self.acc_factor > pow(0.8*1.8 ,2):
				self.energy -= 0.6
			
			if self.protein_metabolism == 1:
				self.energy += (-0.02 * abs(pow((self.acc_factor - self.deacc_factor) , 2))) + (-0.04 * abs(pow((self.rot_speed_left - self.rot_speed_right), 2))) - ((pow(self.sizeRadius, 2) * 3.14) / 18000) 
			else:
				self.energy += (-0.02 * abs(pow((self.acc_factor - self.deacc_factor) , 2))) + (-0.04 * abs(pow((self.rot_speed_left - self.rot_speed_right), 2))) - ((pow(self.sizeRadius, 2) * 3.14) / 14000) 

		
		#staveation
		if self.energy <= 1:
			self.health += -0.4

		#if self.energy >= (pow(self.sizeRadius, 2) * 3.14 * 3):
			#self.health += -0.4

		#Health
		if(self.health <= 0) and self.alive == True:
			self.die()

		#ageing they all live to 600
		#if self.age > (500 * frames_per_second ) and self.alive == True:
			#self.health += -0.4

		#Gets older and birth timer, pain goes down
		if self.alive == True:
			self.age += 1
			self.birth_timer += 1

		if self.pain > 0: 
			self.pain -= 0.002
		else:
			self.pain = 0

	def draw_animal(self):

		#left eye
		self.left_eye_x = self.pos.x + math.cos(math.radians(self.rot - self.left_eye_rot)) * self.sizeRadius
		self.left_eye_y = self.pos.y + math.sin(math.radians(self.rot - self.left_eye_rot)) * self.sizeRadius

		#right eye
		self.right_eye_x = self.pos.x + math.cos(math.radians(self.rot + self.right_eye_rot)) * self.sizeRadius
		self.right_eye_y = self.pos.y + math.sin(math.radians(self.rot + self.right_eye_rot)) * self.sizeRadius

		#flagella
		self.flagellum_len = self.sizeRadius + (((self.acc_factor - self.deacc_factor) * (self.sizeRadius / 2) + (self.sizeRadius / 14)))
		self.flagellum_left_len = self.sizeRadius + (self.rot_speed_left * (self.sizeRadius / 2) + (self.sizeRadius / 6))
		self.flagellum_right_len = self.sizeRadius + (self.rot_speed_right * (self.sizeRadius / 2) + (self.sizeRadius / 6))
		
		self.flagellum_x = self.pos.x + math.cos(math.radians(self.rot + 180)) * self.flagellum_len
		self.flagellum_y = self.pos.y + math.sin(math.radians(self.rot + 180)) * self.flagellum_len

		#left
		self.flagellum_left_x = self.pos.x + math.cos(math.radians(self.rot - 90)) * self.flagellum_left_len
		self.flagellum_left_y = self.pos.y + math.sin(math.radians(self.rot - 90)) * self.flagellum_left_len

		#right
		self.flagellum_right_x = self.pos.x + math.cos(math.radians(self.rot + 90)) * self.flagellum_right_len
		self.flagellum_right_y = self.pos.y + math.sin(math.radians(self.rot + 90)) * self.flagellum_right_len

		if self.selected:
			#left eye
			pygame.draw.line(Simulation_display, (250,160,160), (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.left_cone1_x + camera_offset[0], self.left_cone1_y + camera_offset[1]), 1 )
			pygame.draw.line(Simulation_display, (250,160,160), (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.left_cone2_x + camera_offset[0], self.left_cone2_y + camera_offset[1]), 1 )

			#right eye
			pygame.draw.line(Simulation_display, (160,160,250), (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.right_cone1_x + camera_offset[0], self.right_cone1_y + camera_offset[1]), 1 )
			pygame.draw.line(Simulation_display, (160,160,250), (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.right_cone2_x + camera_offset[0], self.right_cone2_y + camera_offset[1]), 1 )

			name = font.render(self.name, True, settings_color)
			Simulation_display.blit(name, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 10))

			energy_text = smallfont.render( 'Energy: ' + str(int(self.energy)), True, settings_color)
			Simulation_display.blit(energy_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 30))

			health_text = smallfont.render( 'Health: ' + str(int(self.health)), True, settings_color)
			Simulation_display.blit(health_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 50))

			age_text = smallfont.render( 'Age: ' + str(int(self.age / frames_per_second )) + ' seconds', True, settings_color)
			Simulation_display.blit(age_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 70))

			gen_text = smallfont.render( 'Gen: ' + str(int(self.gen)), True, settings_color)
			Simulation_display.blit(gen_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 90))

			if( self.protein_metabolism == 1 ):
				metabolism_font = 'Carnivore'
			if( self.protein_metabolism == 0 ):
				metabolism_font = 'Herbivore'

			metabolism_text = smallfont.render( metabolism_font, True, settings_color)
			Simulation_display.blit(metabolism_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 110))

			_text = smallfont.render( 'Birthed kin: ' + str(int(self.birthed_kin)), True, settings_color)
			Simulation_display.blit(_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 130))

			mutations_text = smallfont.render( 'Amount of mutations: ' + str(self.mutations), True, settings_color)
			Simulation_display.blit(mutations_text, (self.pos.x + self.sizeRadius + camera_offset[0] + 10, self.pos.y + self.sizeRadius + camera_offset[1] + 150))


		pygame.draw.line(Simulation_display, self.color, (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.x_mouth + camera_offset[0], self.y_mouth + camera_offset[1]), int(self.flagellum_width * camera_zoom) )
		pygame.draw.circle(Simulation_display, self.color, (int(self.x_mouth + camera_offset[0]), int(self.y_mouth + camera_offset[1])), int((self.mouth_radius + 2) * camera_zoom))

		#flagellums
		pygame.draw.line(Simulation_display, self.color, (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.flagellum_x + camera_offset[0], self.flagellum_y + camera_offset[1]), int(self.flagellum_width * camera_zoom) )
		pygame.draw.line(Simulation_display, self.color, (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.flagellum_left_x + camera_offset[0], self.flagellum_left_y + camera_offset[1]), int(self.flagellum_width * camera_zoom) )
		pygame.draw.line(Simulation_display, self.color, (self.pos.x + camera_offset[0], self.pos.y + camera_offset[1]), (self.flagellum_right_x + camera_offset[0], self.flagellum_right_y + camera_offset[1]), int(self.flagellum_width * camera_zoom) )

		pygame.draw.circle(Simulation_display, self.color, (int(self.pos.x + camera_offset[0]), int(self.pos.y + camera_offset[1])), int(self.sizeRadius * camera_zoom))

		#eyes
		pygame.draw.circle(Simulation_display, (self.color[0] / 1.6, self.color[1] / 1.6, self.color[2] / 1.6), (int(self.left_eye_x + camera_offset[0]), int(self.left_eye_y + camera_offset[1])), int(((self.view_distance/50) + 1) * camera_zoom))
		pygame.draw.circle(Simulation_display, (self.color[0] / 1.6, self.color[1] / 1.6, self.color[2] / 1.6), (int(self.right_eye_x + camera_offset[0]), int(self.right_eye_y + camera_offset[1])), int(((self.view_distance/50) + 1) * camera_zoom))


	def copy_animal(self):
		### COPY ANIMAL ###
		copied_animal = copy.deepcopy(self)
		parents_id = copy.deepcopy(id(self))
		
		### POSSIBLE MUTATIONS###
		copied_animal.parents.append(parents_id)
		copied_animal.gen += 1
		new_name = copied_animal.name
		new_color = copied_animal.color
		new_gen = copied_animal.gen + 1

		#chance that the child becomes a different specie
		if copied_animal.gen > 6 and random.randint(0, 6) == 0:
			new_gen = 1
			new_name = random_name()
			new_color = (random.randint(50,160), random.randint(50,160), random.randint(50,160)) #color
			#reset parents if new specie
			copied_animal.parents = []
			copied_animal.protein_metabolism = mutate_metabolism(copied_animal.protein_metabolism)

		### CHANGE THAT ANIMAL ###
		copied_animal.gen = new_gen
		copied_animal.name = new_name
		copied_animal.color = new_color

		copied_animal.selected = False

		copied_animal.age = 0
		copied_animal.birth_timer = 0
		copied_animal.birth_fitness = 0

		copied_animal.birthed_kin = 0
		copied_animal.sizeRadius = mutate_organ(copied_animal.sizeRadius, 1, 6, 12)
		copied_animal.energy = (pow(copied_animal.sizeRadius, 2) * 3.14) / 2
		copied_animal.health = pow(copied_animal.sizeRadius, 2) * 3.14
		copied_animal.pain = 0
		copied_animal.alive = True
		copied_animal.balls_eaten = 0

		copied_animal.view_distance = mutate_organ(copied_animal.view_distance, 1, 10, 200)

		#eyes
		copied_animal.eye_rot = mutate_organ(copied_animal.eye_rot, 0.4, 1, 180)
		copied_animal.FOV = mutate_organ(copied_animal.FOV, 0.4, 1, 180)

		copied_animal.mutations = copied_animal.mutations + 1
		copied_animal.weights = [ 
		mutate_neuralnetwork( copied_animal, copied_animal.input_size, copied_animal.hidden_sizes[0], copied_animal.weights[0], copied_animal.mutation_rate), 
		mutate_neuralnetwork( copied_animal, copied_animal.hidden_sizes[0], copied_animal.hidden_sizes[1], copied_animal.weights[1], copied_animal.mutation_rate), 
		mutate_neuralnetwork( copied_animal, copied_animal.hidden_sizes[1], copied_animal.output_size, copied_animal.weights[2], copied_animal.mutation_rate), 
		]

		living_animals_array.append(copied_animal)
