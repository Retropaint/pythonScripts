from PIL import Image, ImageEnhance
import ast, sys, argparse

# command line stuff
parser = argparse.ArgumentParser(description='Creates color-compressed image. Requires PIL')
parser.add_argument('source', help="filename (relative to path)")
parser.add_argument('--dest', '-d', help="filename (relative to path) to save. Include the extension! Default appends 'New' to source")
parser.add_argument('--compress', '-c', type=float, default=100, help="compression level. Higher comprsses more. Default 100")
parser.add_argument('--transparency', '-t', type=float, default=128, help="Transparency cutoff point (8-bit). Default 128")
parser.add_argument('--brightness', '-b', type=float, default=1, help="brightness level, applied after color processing, Default 1")
parser.add_argument('--saturate', '-s', type=float, default=1, help="saturation level, applied before color processing. Default 1")
parser.add_argument('--colors', '-cs', default="(0,0,0),(255,255,255)", help="starting set of colors (8-bit RGB tuple). Default: '(0,0,0),(255,255,255)'")
parser.add_argument('--verbose', '-v', help="show more info during, and after, processing", action="store_true")
parser.add_argument('--log', '-l', help="save outputs to log file as source + 'Log.txt'", action="store_true")
parser.add_argument('--open', '-o', help="opens new image immediately after export", action="store_true")
parser.add_argument('--onlysaturate', '-os', help="stops script at the saturation process, ignoring dest and appending 'Sat' to source", action="store_true")
args = parser.parse_args()

logs = []
def log(msg):
	print(msg)
	logs.append(msg)

colors = ast.literal_eval('[' + args.colors + ']')
# debug only
colorOrigins = []
for c in range(len(colors)):
	colorOrigins.append("initial")

# attempt to open file
im = None
try:
	im = Image.open(args.source)
except OSError:
	log("File doesn't exist! Make sure to include the extension.")
	quit()

def saveImage(im):
	# save new image separately (does not affect source)
	destname = args.dest
	splitName = args.source.split('.')
	if args.onlysaturate:
		destname = splitName[0] + 'Sat.' + splitName[1]
	elif destname == None:
		destname = splitName[0] + 'New.' + splitName[1]	
	log("Saved as " + destname)
	effect = ImageEnhance.Brightness(im)
	im = effect.enhance(args.brightness)
	im.save(destname)
	if args.open: im.show()

# saturate 
effect = ImageEnhance.Color(im)
im = effect.enhance(args.saturate)
if args.onlysaturate:
	saveImage(im)
	quit()
px = im.load()

def isNewColor(x, y):
	p = px[x, y]
	if p[3] < args.transparency: return False 
	for c in colors:
		if p == c: return False 
		offset = [abs(p[0]-c[0]),abs(p[1]-c[1]),abs(p[2]-c[2])] 
		diff = offset[0] + offset[1] + offset[2]
		if(diff < args.compress): 
			return False
	colors.append((p[0], p[1], p[2]))	
	colorOrigins.append((x, y))

# extract colors
log("extracting colors...")
progress=["25%", "50%", "75%"]
milestones = [im.height/4, im.height/2, im.height/(4/3)]
for y in range(im.height):
	for x in range(im.width):
		isNewColor(x, y)

	# verbose progress
	if args.verbose and len(milestones) > 0 and y >= milestones[0]:
		log(progress[0] + ' ' + str(len(colors)) + " colors")
		progress.pop(0)
		milestones.pop(0)

# attempt to 'clean' color array by pitting them up against each other
# currently unused
for cy in colors:
	for idx, cx in enumerate(colors):	
		offset = [abs(cx[0]-cy[0]),abs(cx[1]-cy[1]),abs(cx[2]-cy[2])]
		diff = offset[0] + offset[1] + offset[2]
		#if(diff < 25):
			#colors.pop(idx)

log(str(len(colors)) + " total colors")

def closestColor(p):
	if p[3] < args.transparency: return (255, 255, 255)
	closest = 999;
	chosen = -1;
	for idx, c in enumerate(colors):
		if p == c: return c
		comparison = [abs(p[0]-c[0]),abs(p[1]-c[1]),abs(p[2]-c[2])] 
		diff = comparison[0] + comparison[1] + comparison[2]
		if(diff < closest):
			chosen = idx 
			closest = diff 
	return colors[chosen];

# apply extracted colors across image
log("creating image...")
progress = ["25%", "50%", "75%"]
milestones = [im.height/4, im.height/2, im.height/(4/3)]
for y in range(im.height):
	for x in range(im.width):
	  px[x,y] = closestColor(px[x,y])

	# verbose progress
	if args.verbose and len(milestones) > 0 and y >= milestones[0]:
		log(progress[0])
		milestones.pop(0)
		progress.pop(0)

saveImage(im)

if args.verbose:
	# create prettytable or simple multi-lines
	try:
		from prettytable import PrettyTable 
		table = PrettyTable(['id', 'Color', 'Origin'])
		table.align = 'l'
		for idx, c in enumerate(colors):
			table.add_row([idx, c, colorOrigins[idx]])
		log(str(table))
	except:
		for idx, c in enumerate(colors):
			log("color", c, "origin", colorOrigins[idx])
		log("Install prettytable to get a table of the above!")

if args.log:
	# create log file
	splitName = args.source.split('.')
	logName = splitName[0] + 'Log.txt'
	logFile = open(logName, "w")
	for l in logs:
		logFile.write(l + '\n')
	logFile.close()
	print("Saved as " + logName)
	
