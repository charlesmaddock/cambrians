import pygame
import random
from Settings import *

class Rectangle:
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

#Question: If it bad to pass the whole animal object efficiency-wise?
	def contains(self, obj):
		#return true or false
		return obj.pos.x > self.x and obj.pos.x < self.x + self.w and obj.pos.y > self.y and obj.pos.y < self.y + self.h 

	def intersects(self, quad_boundry): 

		#defining the top right and bottom left of each rectangle
		range_top_right_y = self.y
		range_top_right_x = self.x + self.w

		range_bottom_left_y = self.y + self.h
		range_bottom_left_x = self.x 

		quad_top_right_y = quad_boundry.y
		quad_top_right_x = quad_boundry.x + quad_boundry.w

		quad_bottom_left_y = quad_boundry.y + quad_boundry.h
		quad_bottom_left_x = quad_boundry.x 

		#if this is true, they are not intersecting
		if range_top_right_x < quad_bottom_left_x or range_bottom_left_x > quad_top_right_x:
			return False

		#if this is true, they are not intersecting
		if range_top_right_y > quad_bottom_left_y or range_bottom_left_y < quad_top_right_y:	
			return False

		#Is intersecting
		return True

class Quadtree:
	def __init__(self, boundry, n):
		self.boundry = boundry
		self.capacity = n
		self.objects = []
		self.divided = False
		self.highlight = False

	def subdivide(self):
		x = self.boundry.x
		y = self.boundry.y
		w = self.boundry.w
		h = self.boundry.h

		ne_boundry = Rectangle(x + w/2, y, w/2, h/2)
		self.northeast = Quadtree(ne_boundry, self.capacity)

		nw_boundry = Rectangle(x, y, w/2, h/2)	
		self.northwest = Quadtree(nw_boundry, self.capacity)

		se_boundry = Rectangle(x + w/2, y + h/2, w/2, h/2)
		self.southeast = Quadtree(se_boundry, self.capacity)

		sw_boundry = Rectangle(x, y + h/2, w/2, h/2)
		self.southwest = Quadtree(sw_boundry, self.capacity)

		self.divided = True


	def insert(self, obj):

		#Only do this if the obj is within the quadtree
		if self.boundry.contains(obj) == False:
			return

		if len(self.objects) < self.capacity:
			self.objects.append(obj)
		else:
			#If we already divided, dont do it again.
			if self.divided == False:
				self.subdivide()

			#Add to all our child quadtrees and check inside insert() if they belong to it 
			#(recursive, since it is in the beginning of the same function we are in right now)
			self.northeast.insert(obj)
			self.northwest.insert(obj)
			self.southeast.insert(obj)
			self.southwest.insert(obj)


	def query(self, scope, found):

		#if our scope rectangle has NOT intersected with a quadtree rectange, (self.boundry)
		if not scope.intersects(self.boundry):
			return found

		#highlight if an animal is within range of a quadtree
		self.highlight = True

		for obj in self.objects:
			if scope.contains(obj):
				found.append(obj)

		if self.divided:
			self.northwest.query(scope, found)
			self.northeast.query(scope, found)
			self.southwest.query(scope, found)
			self.southeast.query(scope, found)

		return found

	def draw(self):
		
		quad_color = (100)
		if self.highlight == True:
			pygame.draw.rect(Simulation_display, quad_color, (self.boundry.x + camera_offset[0], self.boundry.y + camera_offset[1], self.boundry.w , self.boundry.h), 4)
		else:
			pygame.draw.rect(Simulation_display, quad_color, (self.boundry.x + camera_offset[0], self.boundry.y + camera_offset[1], self.boundry.w , self.boundry.h), 1)

		if self.divided:
			self.northeast.draw()
			self.northwest.draw()
			self.southeast.draw()
			self.southwest.draw()

class Circle:
	def __init__(self, x, y, r):
		self.x = x
		self.y = y
		self.r = r
		self.rSquared = self.r * self.r

	def contains(self, obj):
		d = pow((obj.pos.x - self.x), 2) + pow((obj.pos.y - self.y), 2)
		return d <= self.rSquared
	

	def intersects(self, scope):
		xDist = abs(scope.x - self.x)
		yDist = abs(scope.y - self.y)

		r = self.r

		w = scope.w
		h = scope.h

		edges = pow((xDist - w), 2) + pow((yDist - h), 2)

		if (xDist > (r + w) or yDist > (r + h)):
			return False

		if (xDist <= w or yDist <= h):
			return True

		return edges <= self.rSquared;


