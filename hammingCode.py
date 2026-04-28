import math

message = [1,0,1,1,1,0,1,0,1,1,1]

def matricize(data):
	dataIndex = 0
	width = math.ceil(math.log2(len(data)))
	matrix = [[0 for _ in range(width)] for _ in range(width)]
	for i in range(4):
		for j in range(4):
			if (i == 0):
				if (j == 0):
					matrix[i][j] = -1
					continue
				if (math.log2(j)%1 == 0):
					matrix[i][j] = -1
					continue
			if (j == 0):
				if (math.log2(i)%1 == 0):
					matrix[i][j] = -1
					continue
			matrix[i][j] = data[dataIndex]
			dataIndex = dataIndex + 1
	return matrix

def addParity(matrix):
	level = 1
	while(level < len(mat)):
		lines = []
		for i in range(len(mat)):
			if (math.floor(i / (2 ** (level -1) )) % 2 == 1 ):
				lines.append(i)
		matrix[0][2 ** (level -1)] = checkParity(matrix,False,lines)
		matrix[2 ** (level -1)][0] = checkParity(matrix,True ,lines)
		level = level * 2
	matrix[0][0] = checkParity(matrix,True,range(len(matrix)))

def checkData(matrix):
	P = checkParity(matrix,True,range(len(matrix)))
	errorRow = []
	errorCol = []
	for rowCol in [True,False]:
		level = 1
		while(level < len(mat)):
			lines = []
			for i in range(len(mat)):
				if (math.floor(i / (2 ** (level -1) )) % 2 == 1 ):
					lines.append(i)
			if (checkParity(matrix,rowCol,lines) == 0):
				lines = list(set(lines) ^ set(range(len(mat))))
			if  rowCol:
				if (len(errorRow) == 0):
					errorRow = lines
				else:
					errorRow = list(set(errorRow) & set(lines))
			else:
				if (len(errorCol) == 0):
					errorCol = lines
				else:
					errorCol = list(set(errorCol) & set(lines))

			level = level * 2
	if P == 0:
		print("No Errors")
		return matrix
	elif (P == 0):
		print("Two Errors - data is must be retransmitted")
		return matrix
	print("Error at: ", errorRow[0],",",errorCol[0])


def checkParity(matrix,QRows,lines):
	checkSum = 0
	if(QRows):
		for line in lines:
			for i in range(len(matrix)):
				if (matrix[line][i] == -1):
					continue
				checkSum = checkSum + matrix[line][i]
	else :
		for line in lines:
			for i in range(len(matrix)):
				if (matrix[i][line] == -1):
					continue
				checkSum = checkSum + matrix[i][line]
	return checkSum % 2

mat = matricize(message)
addParity(mat)
for row in mat:
    print(*row, sep="\t")

mat[0][3] = 0
checkData(mat)

for row in mat:
    print(*row, sep="\t")
