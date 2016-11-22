import numpy as np
import matplotlib.pyplot as plt

decayFunction = float(1000)
numEpochs = 100

with open('./digitdata/trainingimages') as f:
    trainingImages = f.readlines()
    trainingImages = [list(line) for line in trainingImages]
trainingImages = np.asarray(trainingImages)
trainingImages[trainingImages == ' '] = 0
trainingImages[trainingImages == '+'] = 1
trainingImages[trainingImages == '#'] = 1
with open('./digitdata/traininglabels') as f:
    trainingLabels = f.readlines()

tempImage = np.empty((5000, (28**2)+1), dtype=np.uint8)
actualClass = np.empty(5000, dtype=np.uint8)
perceptron = np.zeros((10,(28**2)+1))


confusionMatrix = np.zeros((10, 10), dtype=np.uint16)


for i in range(5000): #loop through every training image
    actualClass[i] = int(trainingLabels[i]) #get the actual class

    for j in range(28): #loop through every line of a training image and copy into a temp
        tempImage[i,j*28:(j+1)*28] = trainingImages[28*i+j][0:28]


trainingCurve = np.empty(numEpochs)
np.random.seed(0)

for thisEpoch in range(numEpochs):
    correctness = 5000
    for k in np.random.permutation(5000):
        thisImage = tempImage[k]
        thisClass = actualClass[k]

        classGuess = np.argmax(np.dot(perceptron, thisImage))

        if(thisClass != classGuess):
            correctness -= 1
            perceptron[thisClass] += (decayFunction/(decayFunction+thisEpoch))*thisImage
            perceptron[classGuess] -= (decayFunction/(decayFunction+thisEpoch))*thisImage

    trainingCurve[thisEpoch] = correctness
    print(correctness)

trainingCurve = trainingCurve / 5000

plt.plot(trainingCurve)

with open('./digitdata/testimages') as f:
    testImages = f.readlines()
    testImages = [list(line) for line in testImages]
testImages = np.asarray(testImages)
testImages[testImages == ' '] = 0
testImages[testImages == '+'] = 1
testImages[testImages == '#'] = 1
with open('./digitdata/testlabels') as f:
    testLabels = f.readlines()

for i in range(1000): #loop through all the test images
    actualClassTest = int(testLabels[i]) #get the actual class

    for j in range(28): #loop through each line of an image
        thisImage[j*28:(j+1)*28] = testImages[28*i+j][0:28] #copy into tempImage

    chosenClass = np.argmax(np.dot(perceptron,thisImage)) #get the maximum, most accurate class
    confusionMatrix[actualClassTest, chosenClass] += 1 #10x10 matrix whose entry in row r and column c is the percentage of test images from class r that are classified as class c.

classificationRate = np.divide(np.diag(confusionMatrix).astype(np.float), np.sum(confusionMatrix, axis=1))
print(confusionMatrix)
print(classificationRate)

plt.show()
