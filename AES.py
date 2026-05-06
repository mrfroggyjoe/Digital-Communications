import numpy as np
import math
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
	if isinstance(bitString, int):
		for i in range(len(bitString)):
			bitString[i] = format(bitString[i],'0128b')

	bits = "".join(bitString)

	bitToIm(bits,shape,d,name)

img = imToBit()
bitToIm(img[0],img[1],img[2],"test2.tif")


def xtime(x, c):
	a = 0
	if x & 1:
		a = c
	x = x >> 1
	while x > 0:
		c = c << 1
		if c & 0x100:
			c = (c & 0xFF) ^ 27 
		if x & 1:
			a = a ^ c
		x = x >> 1
	return a

def AddRoundKey(state, w):
	state ^= w 
	return state

def SubBytes(state):
	sbox_hex = (
		'637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0'
		'b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275'
		'09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf'
		'd0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2'
		'cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb'
		'e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08'
		'ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e'
		'e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16'
	)
	sbox = np.array([int(sbox_hex[i:i+2], 16) for i in range(0, len(sbox_hex), 2)], dtype=int)
	return sbox[state] 

def InvSubBytes(state):
	inv_sbox_hex = (
		'52096ad53036a538bf40a39e81f3d7fb'
      '7ce339829b2fff87348e4344c4dee9cb'
      '547b9432a6c2233dee4c950b42fac34e'
      '082ea16628d924b2765ba2496d8bd125'
      '72f8f66486689816d4a45ccc5d65b692'
      '6c704850fdedb9da5e154657a78d9d84'
      '90d8ab008cbcd30af7e45805b8b34506'
      'd02c1e8fca3f0f02c1afbd0301138a6b'
      '3a9111414f67dcea97f2cfcef0b4e673'
      '96ac7422e7ad3585e2f937e81c75df6e'
      '47f11a711d29c5896fb7620eaa18be1b'
      'fc563e4bc6d279209adbc0fe78cd5af4'
      '1fdda8338807c731b11210592780ec5f'
      '60517fa919b54a0d2de57a9f93c99cef'
      'a0e03b4dae2af5b0c8ebbb3c83539961'
      '172b047eba77d626e169146355210c7d'
	)
	inv_sbox = np.array([int(inv_sbox_hex[i:i+2], 16) for i in range(0, len(inv_sbox_hex), 2)], dtype=int)
	return inv_sbox[state]

def MixColumns(state):
	s_out = np.zeros(16, dtype=int)
	s = state.flatten('F')
	for a in range(0, 16, 4):
		s_out[a]   = xtime(2, s[a]) ^ xtime(3, s[a+1]) ^ s[a+2] ^ s[a+3]
		s_out[a+1] = xtime(2, s[a+1]) ^ xtime(3, s[a+2]) ^ s[a] ^ s[a+3]
		s_out[a+2] = xtime(2, s[a+2]) ^ xtime(3, s[a+3]) ^ s[a] ^ s[a+1]
		s_out[a+3] = xtime(2, s[a+3]) ^ xtime(3, s[a]) ^ s[a+1] ^ s[a+2]
	return s_out.reshape((4, 4), order='F')

def InvMixColumns(state):
	s_out = np.zeros(16, dtype=int)
	s = state.flatten('F')
	for a in range(0, 16, 4):
		s_out[a]   = xtime(14, s[a]) ^ xtime(11, s[a+1]) ^ xtime(13, s[a+2]) ^ xtime(9, s[a+3])
		s_out[a+1] = xtime(9, s[a]) ^ xtime(14, s[a+1]) ^ xtime(11, s[a+2]) ^ xtime(13, s[a+3])
		s_out[a+2] = xtime(13, s[a]) ^ xtime(9, s[a+1]) ^ xtime(14, s[a+2]) ^ xtime(11, s[a+3])
		s_out[a+3] = xtime(11, s[a]) ^ xtime(13, s[a+1]) ^ xtime(9, s[a+2]) ^ xtime(14, s[a+3])
	return s_out.reshape((4, 4), order='F')

def KeyExpansion(key, Nk):
	key_dec = [int(key[i:i+2], 16) for i in range(0, len(key), 2)]
	w = np.zeros((4, 4 * (Nk + 7)), dtype=int)
	w[:, :Nk] = np.array(key_dec).reshape((4, Nk), order='F')
	
	for i in range(Nk, 4 * (Nk + 7)):
		temp = w[:, i-1].copy()
		if i % Nk == 0:
			temp = SubBytes(np.roll(temp, -1))
			n, m = 1, 0
			while m < (i // Nk) - 1:
				n = xtime(2, n)
				m += 1
			temp[0] ^= n
		elif Nk > 6 and i % 8 == 4:
			temp = SubBytes(temp)
		w[:, i] = w[:, i - Nk] ^ temp
	return w

def Cipher(key, In):
	Nk = len(key) // 8
	In_dec = [int(In[i:i+2], 16) for i in range(0, len(In), 2)]
	w = KeyExpansion(key, Nk)
	state = np.array(In_dec).reshape((4, 4), order='F')
	
	state = AddRoundKey(state, w[:, :4])
	
	for k in range(2, Nk + 7):
		state = SubBytes(state)
		state[1, :] = np.roll(state[1, :], -1)
		state[2, :] = np.roll(state[2, :], -2)
		state[3, :] = np.roll(state[3, :], -3)
		state = MixColumns(state)
		state = AddRoundKey(state, w[:, 4*(k-1):4*k])
		
	state = SubBytes(state)
	state[1, :] = np.roll(state[1, :], -1)
	state[2, :] = np.roll(state[2, :], -2)
	state[3, :] = np.roll(state[3, :], -3)
	state = AddRoundKey(state, w[:, 4*(Nk+6):4*(Nk+7)])
	
	return "".join([format(x, '02x') for x in state.flatten('F')])

def InvCipher(key, In):
	Nk = len(key) // 8
	In_dec = [int(In[i:i+2], 16) for i in range(0, len(In), 2)]
	w = KeyExpansion(key, Nk)
	state = np.array(In_dec).reshape((4, 4), order='F')
	
	state = AddRoundKey(state, w[:, 4*(Nk+6):4*(Nk+7)])
	
	for k in range(Nk + 6, 1, -1):
		state[1, :] = np.roll(state[1, :], 1)
		state[2, :] = np.roll(state[2, :], 2)
		state[3, :] = np.roll(state[3, :], 3)
		state = InvSubBytes(state)
		state = AddRoundKey(state, w[:, 4*(k-1):4*k])
		state = InvMixColumns(state) 
		
	state[1, :] = np.roll(state[1, :], 1)
	state[2, :] = np.roll(state[2, :], 2)
	state[3, :] = np.roll(state[3, :], 3)
	state = InvSubBytes(state)
	state = AddRoundKey(state, w[:, :4])
	
	return "".join([format(x, '02x') for x in state.flatten('F')])
data = img[0]

padding_needed = (128 - (len(data) % 128)) % 128
data += '0' * padding_needed

data = [data[i:i + 128] for i in range(0, len(data), 128)]
data = [img[0][i:i + 128] for i in range(0, len(img[0]), 128)]
key = "1234567890abcdefabcdef1234567890"

def bit_to_hex(bit_string):
	hex_len = math.ceil(len(bit_string) / 4)
	return format(int(bit_string, 2), f'0{hex_len}x')

def hex_to_bit(hex_string):
	bit_len = len(hex_string) * 4
	return format(int(hex_string, 16), f'0{bit_len}b')

def imageEnc():
	for i in range(len(data)):
		data[i] = bit_to_hex(data[i])
		data[i] = Cipher(key,data[i])

	for i in range(len(data)):
		data[i] = hex_to_bit(data[i])

	toIm(data,img[1],img[2],"AES_encrypted.tif")

	for i in range(len(data)):
		data[i] = bit_to_hex(data[i])
		data[i] = InvCipher(key,data[i])

	for i in range(len(data)):
		data[i] = hex_to_bit(data[i])

	toIm(data,img[1],img[2],"AES_decrypted.tif")

imageEnc()

#-- -- --- -- wav -- -- -- -- -- - - -- -- 

def bitToWav(bitString,name):
	if isinstance(bitString, int):
		for i in range(len(bitString)):
			bitString[i] = format(bitString[i],'0128b')

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

padding_needed = (128 - (len(bit_stream) % 128)) % 128
bit_stream += '0' * padding_needed

data = [bit_stream[i:i + 128] for i in range(0, len(bit_stream), 128)]

def waveEnc():
	for i in range(len(data)):
		data[i] = bit_to_hex(data[i])
		data[i] = Cipher(key,data[i])

	for i in range(len(data)):
		data[i] = hex_to_bit(data[i])

	bitToWav(data,"AES_encrypted.wav")

	for i in range(len(data)):
		data[i] = bit_to_hex(data[i])
		data[i] = InvCipher(key,data[i])

	for i in range(len(data)):
		data[i] = hex_to_bit(data[i])

	bitToWav(data,"AES_recovered.wav")

waveEnc()