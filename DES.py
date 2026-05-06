import numpy as np
from PIL import Image
import wave

def imToBit():
	img = Image.open("cameraman.tif")
	img_array = np.array(img)

	shape = img_array.shape
	dtype = img_array.dtype
    
	b = ''.join(format(byte, '08b') for byte in img_array.tobytes())
    
	return b, shape, dtype

def bitToIm(b, shape,d,name):
	byte_list = [int(b[i:i+8], 2) for i in range(0, len(b), 8)]
	byte_array = bytes(byte_list)
    
	recon_array = np.frombuffer(byte_array, dtype=d).reshape(shape)
    
	new_img = Image.fromarray(recon_array)
	new_img.save(name)

def toIm(bitString,shape,d,name):
	if (type(bitString) ==  'int'):
		for i in range(len(bitString)):
			bitString[i] = format(bitString[i],'064b')

	bits = "".join(bitString)

	bitToIm(bits,shape,d,name)

img = imToBit()
bitToIm(img[0],img[1],img[2],"test.tif")

key = ''.join(format(byte, '08b') for byte in "8bytekey".encode('ascii'))

data = [img[0][i:i + 64] for i in range(0, len(img[0]), 64)]
for i in range(len(data)):
	i = i

def F(right_half, subkey):
	P_Box = [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10,2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]
	S= [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7, 0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8, 4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0, 15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],  [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10, 3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5, 0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15, 13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],  [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8, 13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1, 13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7, 1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],  [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15, 13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9, 10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4, 3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],  [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9, 14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6, 4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14, 11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],  [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11, 10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8, 9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6, 4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],  [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1, 13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6, 1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2, 6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],  [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7, 1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2, 7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8, 2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]  ]
	Expn = [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 16, 17, 18, 19, 20, 21, 20, 21, 22, 23, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]
	
	expanded = "".join(right_half[i - 1] for i in Expn)
	xor_res = int(expanded, 2) ^ subkey
	xor_str = format(xor_res, '048b')

	s_output = ""
	for i in range(8):
		block = xor_str[i*6 : i*6 + 6]
		row = int(block[0] + block[5], 2)
		col = int(block[1:5], 2)
		val = S[i][row * 16 + col]
		s_output += format(val, '04b')

	final_output = "".join(s_output[i - 1] for i in P_Box)
	return int(final_output, 2)



def keyShedule(k):
	Left_Shift=[1, 1, 2 ,2 ,2, 2, 2 ,2 ,1, 2, 2, 2, 2, 2, 2, 1];
	PC1C=[57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36]
	PC1D=[63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4]
	PC2=[14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]

	def permute(bits, table):
		return "".join(bits[i - 1] for i in table)

	def left_circular_shift(bits, n):
		return bits[n:] + bits[:n]

	C = permute(k, PC1C)
	D = permute(k, PC1D)

	subkeys = []

	for shift_amount in Left_Shift:
		C = left_circular_shift(C, shift_amount)
		D = left_circular_shift(D, shift_amount)
        
		combined = C + D
        
		round_key_bin = permute(combined, PC2)
        
		subkeys.append(int(round_key_bin, 2))

	return subkeys



def DES(m,k,mode):
	keys = keyShedule(k)
	if (mode == "DECRYPT"):
		keys.reverse()

	def permute(bits, table):
		return "".join(bits[i - 1] for i in table)

	IP=[58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
	InvIP = [ 40, 8,48,16,56,24,64,32 ,39, 7,47,15,55,23,63,31 ,38, 6,46,14,54,22,62,30 ,37, 5,45,13,53,21,61,29 ,36, 4,44,12,52,20,60,28 ,35, 3,43,11,51,19,59,27 ,34, 2,42,10,50,18,58,26 ,33, 1,41, 9,49,17,57,25  ]
	m = permute(m,IP)

	left = int(m[:32],2)
	right = int(m[32:],2)
	for i in range(16):
		temp = right
		right = left ^ F(format(right,'032b'),keys[i])
		left = temp

	m = format(right,'032b') + format(left,'032b')
	m = permute(m,InvIP)

	return m

def encryptImage(data):
	data = [img[0][i:i + 64] for i in range(0, len(img[0]), 64)]

	for i in range(len(data)):
		data[i] = DES(data[i],key,'ENCRYPT')

	toIm(data,img[1],img[2],"encrypted.tif")

	for i in range(len(data)):
		data[i] = DES(data[i],key,'DECRYPT')

	toIm(data,img[1],img[2],"decrypted.tif")

#-- -- --- -- wav -- -- -- -- -- - - -- -- 

def bitToWav(bitString,name):
	if (type(bitString[0]) ==  'int'):
		for i in range(len(bitString)):
			bitString[i] = format(bitString[i],'064b')

	bits = "".join(bitString)
	byte = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

	with wave.open(name, 'wb') as out_wav:

	    out_wav.setnchannels(2)
	    out_wav.setsampwidth(2)
	    out_wav.setframerate(44100)
	    
	    out_wav.writeframes(byte)

with wave.open('speech.wav', 'rb') as wav_file:
	params = wav_file.getparams()
	print(params)
	raw_bytes = wav_file.readframes(wav_file.getnframes())

bit_stream = ''.join(format(byte, '08b') for byte in raw_bytes)

data = [bit_stream[i:i + 64] for i in range(0, len(bit_stream), 64)]

bitToWav(data,'test.wav')

def encryptAudio(data):

	for i in range(len(data)):
		data[i] = DES(data[i],key,'ENCRYPT')

	bitToWav(data,'des_encrypted.wav')

	for i in range(len(data)):
		data[i] = DES(data[i],key,'DECRYPT')

	bitToWav(data,'des_recovered.wav')


encryptAudio(data)