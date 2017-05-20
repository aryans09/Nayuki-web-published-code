# 
# Linear congruential generator (LCG) with fast skipping and backward iteration (Python)
# 
# Copyright (c) 2016 Project Nayuki
# All rights reserved. Contact Nayuki for licensing.
# https://www.nayuki.io/page/fast-skipping-in-a-linear-congruential-generator
# 


import numbers, random, sys, time
if sys.version_info.major == 2:
	range = xrange


# Random number generator class (implements most functionality of random.Random)
class LcgRandom(random.Random):
	
	def __new__(cls, *args, **kwargs):  # Magic because the superclass doesn't cooperate
		return random.Random.__new__(cls, random.random())
	
	
	def __init__(self, a, b, m, seed):
		assert isinstance(a, numbers.Integral) and a > 0
		assert isinstance(b, numbers.Integral) and b >= 0
		assert isinstance(m, numbers.Integral) and m > 0
		assert isinstance(seed, numbers.Integral) and 0 <= seed < m
		
		self.a = a     # Multiplier
		self.ainv = LcgRandom.reciprocal_mod(a, m)
		self.b = b     # Increment
		self.m = m     # Modulus
		self.x = seed  # State
	
	
	# Returns the raw state, with 0 <= x < m. To get a pseudorandom number
	# with a certain distribution, the value needs to be further processed.
	def get_state(self):
		return self.x
	
	
	# Advances the state by one iteration.
	def next(self):
		self.x = (self.x * self.a + self.b) % self.m
	
	
	# Rewinds the state by one iteration.
	def previous(self):
		# The intermediate result after subtracting 'b' may be negative, but the modular arithmetic is correct
		self.x = (self.x - self.b) * self.ainv % self.m
	
	
	# Advances/rewinds the state by the given number of iterations.
	def skip(self, n):
		if n >= 0:
			a = self.a
			b = self.b
		else:
			a = self.ainv
			b = -self.ainv * self.b
			n = -n
		a1 = a - 1
		ma = a1 * self.m
		y = (pow(a, n, ma) - 1) // a1 * b
		z = pow(a, n, self.m) * self.x
		self.x = (y + z) % self.m
	
	
	# Quite inefficient, but accommodates arbitrarily small or big moduli, and moduli that are not powers of 2
	def randbit(self):
		self.next()
		return self.x >= (self.m >> 1)
	
	
	# Implements a method in class random.Random.
	def getrandbits(self, k):
		result = 0
		for i in range(k):
			result = (result << 1) | self.randbit()
		return result
	
	
	# Implements a method in class random.Random.
	def random(self):
		return self.getrandbits(52) / float(1 << 52)
	
	
	@staticmethod
	def reciprocal_mod(x, mod):
		# Based on a simplification of the extended Euclidean algorithm
		assert mod > 0 and 0 <= x < mod
		y = x
		x = mod
		a = 0
		b = 1
		while y != 0:
			a, b = b, a - x // y * b
			x, y = y, x % y
		if x == 1:
			return a % mod
		else:
			raise ValueError("Reciprocal does not exist")



# Demo main program, which runs a correctness check
if __name__ == "__main__":
	# Use the parameters from Java's LCG RNG
	A = 25214903917
	B = 11
	M = 1 << 48
	
	# Choose seed and create LCG RNG
	seed = int(time.time() * 1000)
	randslow = LcgRandom(A, B, M, seed)
	
	# Start testing
	N = 1000
	
	# Check that skipping forward is correct
	for i in range(N):
		randfast = LcgRandom(A, B, M, seed)
		randfast.skip(i)
		if randslow.get_state() != randfast.get_state():
			raise AssertionError()
		randslow.next()
	
	# Check that backward iteration is correct
	for i in reversed(range(N)):
		randslow.previous()
		randfast = LcgRandom(A, B, M, seed)
		randfast.skip(i)
		if randslow.get_state() != randfast.get_state():
			raise AssertionError()
	
	# Check that backward skipping is correct
	for i in range(N):
		randfast = LcgRandom(A, B, M, seed)
		randfast.skip(-i)
		if randslow.get_state() != randfast.get_state():
			raise AssertionError()
		randslow.previous()
	
	print("Test passed (n={})".format(N))
