from pathlib import Path 
import ast, sys, argparse, math

parser = argparse.ArgumentParser(description='Creates color-compressed image. Requires PIL')
parser.add_argument('source', help="filename (relative to path)")
parser.add_argument('newWidth', type=int, help="new width")
parser.add_argument('newHeight', type=int, help="new height")
args = parser.parse_args()

p = Path(args.source)

ogWidth  = 0;
ogHeight = 0;
newWidth = args.newWidth;
newHeight = args.newHeight;
wCurr = 0;
hCurr = 0;
ogContent =  [];
newContent = [""];

# get original width and height
with p.open() as f:
	for line in f:
		ogContent.append(line);
		ogWidth = max(ogWidth, len(line))
		ogHeight += 1

ogWidth -= 1

# get pixel steps of original and new resolutions (based on ratio)
wStep = ogWidth  / newWidth;
hStep = ogHeight / newHeight;

while hCurr < ogHeight:
	while wCurr < ogWidth:
		pixel = math.floor(wCurr)
		newContent[-1] += ogContent[math.floor(hCurr)][pixel]
		wCurr += wStep;
	wCurr = 0;
	hCurr += hStep;
	newContent.append("");

for c in newContent:
	print(c)
