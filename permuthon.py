import sys
import bdb
import linecache
import random
import string
import argparse
import ast
import time

class Permuthon(bdb.Bdb):
	GOOD_NAMES = list(string.ascii_lowercase)
	ALLOWED_BUILTINS = ['print', 'range', 'len', 'chr', 'ord', 'sleep']

	def __init__(self):
		super().__init__()
		self.permutation_cache = [list(range(len(self.GOOD_NAMES)))]
		random.seed(13371337)
		for i in range(1000): #TODO
			a = self.permutation_cache[-1].copy()
			random.shuffle(a)
			self.permutation_cache.append(a)
		self.set_step()
		self.debug = False
	
	def run_program(self, filename):
		self.mainfile = self.canonic(filename)
		self.last_permutation = self.permutation_cache[0].copy()
		self.locals = {
			'__builtins__': {}
		}
		for a in self.ALLOWED_BUILTINS:
			if a == "sleep":
				self.locals['__builtins__']['sleep'] = time.sleep
			else:
				self.locals['__builtins__'][a] = __builtins__.__dict__[a]
		for a in self.GOOD_NAMES:
			self.locals[a] = None
		fp = open(filename, "rb")
		rootnode = ast.parse(fp.read(), self.mainfile)
		used_lines = set()
		for node in ast.walk(rootnode):
			if isinstance(node, ast.Name):
				if node.id not in self.GOOD_NAMES and node.id not in self.ALLOWED_BUILTINS:
					raise Exception("Disallowed name: "+node.id)
			if isinstance(node, ast.FunctionDef):
				raise Exception("Functions are not allowed! (until I fix permutations of locals)")
				if node.name not in self.GOOD_NAMES and node.name not in self.ALLOWED_BUILTINS:
					raise Exception("Disallowed name: "+node.name)
				for arg in node.args.args:
					if arg.arg not in self.GOOD_NAMES and arg.arg not in self.ALLOWED_BUILTINS:
						raise Exception("Disallowed name: "+arg.arg)
			if isinstance(node, ast.Assign) or isinstance(node, ast.Expr):
				if node.lineno in used_lines:
					raise Exception("Multiple commands on line: "+str(node.lineno))
				used_lines.add(node.lineno)
		code = compile(rootnode, self.mainfile, 'exec')
		self.run("exec(code, loc)", {'code': code, 'loc': self.locals})

	def user_line(self, frame):
		filename = self.canonic(frame.f_code.co_filename)
		if filename != self.mainfile:
			return
		line = linecache.getline(filename, frame.f_lineno, frame.f_globals)
		
		oldlocals = self.locals.copy()
		perm = self.permutation_cache[frame.f_lineno]
		for a in range(len(self.GOOD_NAMES)):
			self.locals[self.GOOD_NAMES[perm[a]]] = oldlocals[self.GOOD_NAMES[self.last_permutation[a]]]
		self.last_permutation = perm
		
		if self.debug:
			print("\033[1;30m%d: [%s]: %s\033[0m" % (frame.f_lineno, "".join(map(lambda x: self.GOOD_NAMES[x], self.last_permutation)), line.strip()))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Interpreter of the Permuthon language')
	parser.add_argument('program')
	parser.add_argument('--debug', dest='debug', action='store_true')
	parser.add_argument('--ide', dest='ide', action='store_true')
	args = parser.parse_args()

	lang = Permuthon()
	lang.debug = args.debug
	if not args.ide:
		lang.run_program(args.program)
	else:
		code = open(args.program, "r").read()
		lines = code.split("\n")

		used_names = [set() for _ in range(len(lines)+1)]
		rootnode = ast.parse(code, args.program)
		#print(ast.dump(rootnode))
		for node in ast.walk(rootnode):
			if isinstance(node, ast.Name):
				used_names[node.lineno].add(node.id)
			if isinstance(node, ast.FunctionDef):
				used_names[node.lineno].add(node.name)
				for arg in node.args.args:
					used_names[node.lineno].add(arg.arg)

		for lineno, line in enumerate(lines, 1):
			print("\033[1;30m% 3d: [%s]:\033[0m %s" % (lineno, "".join(map(lambda x: ("\033[1;31m" if lang.GOOD_NAMES[x] in used_names[lineno] else "")+lang.GOOD_NAMES[x]+("\033[1;30m" if lang.GOOD_NAMES[x] in used_names[lineno] else ""), lang.permutation_cache[lineno])), line.rstrip("\n")))
#		lel = int(sys.argv[1])
#		xd = lang.GOOD_NAMES.index(sys.argv[2])
#		kek = lang.permutation_cache[lel].index(xd)
#		for a in range(1, 45):
#			print(str(a).rjust(2), "".join(map(lambda x: ("\033[1;31m" if a >= lel and lang.permutation_cache[a].index(x) == kek else "")+lang.GOOD_NAMES[x]+"\033[0m", lang.permutation_cache[a])))
