from abaqus import *
from abaqusConstants import *
import random
import math

# create model
if "Model-1" in mdb.models.keys():
    myModel = mdb.models["Model-1"]
else:
    myModel = mdb.Model(name="Model-1", modelType=STANDARD_EXPLICIT)

# initial variable
# information of base
height = 40  # Height of the cylinder
radius = 40  # Radius of the cylinder base

# create base - solid cylinder
myPart = myModel.Part(name="Part-base", dimensionality=THREE_D, type=DEFORMABLE_BODY)
mySketch = myModel.ConstrainedSketch(name="sketch-1", sheetSize=200)

# Creating a circle for the cylinder base
mySketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(radius, 0.0))
myPart.BaseSolidExtrude(sketch=mySketch, depth=height)

# information of solid fibre
fibre_length_solid = 6
fibre_radius_solid = 0.007
fibre_num_solid = 50

# create solid fibre
myPart3 = myModel.Part(name="Part-fibre-solid", dimensionality=THREE_D, type=DEFORMABLE_BODY)
mySketch3 = myModel.ConstrainedSketch(name="sketch-3", sheetSize=200)
mySketch3.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(fibre_radius_solid, 0.0))
myPart3.BaseSolidExtrude(sketch=mySketch3, depth=fibre_length_solid)


# save trans and rotate information
fibre = []
points = []

# Adjusted to check if a point is within the cylinder base
def is_point_in_cylinder(x, y, radius):
    return x**2 + y**2 <= radius**2

# caculate the movement and rotation of fibre
# interact of judgement
for num in range(fibre_num_solid):
    # Ensure the fiber starts within the cylinder base
    while True:
        x = random.uniform(-radius, radius)
        y = random.uniform(-radius, radius)
        if is_point_in_cylinder(x, y, radius):
            break
    
    z = random.uniform(0, height)
    angle_y = random.uniform(0, 360)
    angle_z = random.uniform(0, 360)

    z2 = z + fibre_length_solid * math.cos(math.radians(angle_y))
    x2 = x + fibre_length_solid * math.sin(math.radians(angle_y)) * math.cos(math.radians(angle_z))
    y2 = y + fibre_length_solid * math.sin(math.radians(angle_y)) * math.sin(math.radians(angle_z))

    point = ((x, y, z), (x2, y2, z2))
    # Simplified as we're not checking interactions in this snippet
    fibre.append([x, y, z, angle_y, angle_z])

# create in Abaqus
myAssembly = myModel.rootAssembly
for num, (x, y, z, angle_y, angle_z) in enumerate(fibre):
    myAssembly.Instance(name='Part-fibre-solid-{}'.format(num), part=myPart3, dependent=ON)
    myAssembly.rotate(instanceList=('Part-fibre-solid-{}'.format(num),), axisPoint=(0, 0, 0), axisDirection=(0, 1, 0), angle=angle_y)
    myAssembly.rotate(instanceList=('Part-fibre-solid-{}'.format(num),), axisPoint=(0, 0, 0), axisDirection=(0, 0, 1), angle=angle_z)
    myAssembly.translate(instanceList=('Part-fibre-solid-{}'.format(num),), vector=(x, y, z))

# merge assembly to Part
instances = [ins for ins in myAssembly.instances.values()]
myAssembly.InstanceFromBooleanMerge(name='Part-fibre-all', instances=tuple(instances), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
