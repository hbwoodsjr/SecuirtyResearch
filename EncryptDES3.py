from Crypto.Cipher import DES3
import sha
import binascii

Des3IV   = '\x46\xA7\xE9\x10\x58\xE4\xBF\x32'
Des3Key1 = '\x98\x16\x88\x51\x8F\x64\x98\x4E'
Des3Key2 = '\x97\x1C\x98\xBF\x7D\x8F\x62\xB4'
Des3Key3 = '\x19\x72\x0A\x00\x3E\x60\x52\x20'

hash = sha.new()

key = Des3Key1 + Des3Key2 + Des3Key3

cipher_encrypt = DES3.new(key, DES3.MODE_CBC, Des3IV)

FK = '\x00\x00\x00\xa1\x20\x00\x00\x00\xff\xff\xff\xff\x1b\x20\x00\x00\xff\xff\xff\xff\x32\x30\x31\x38\x30\x39\x32\x34\x31\x38\x33\x39\x33\x37\x46\x4c\x58\x35\x00\x00\x00\x00\x00\x02\x65\xe0\xaa\x47'

FK_CRC = '%08X'%(binascii.crc32(FK) & 0xFFFFFFFF) #000000a120000000ffffffff1b200000ffffffff3230313830393234313833393337464c583500000000000265e0aa47
#print("FK: %8X" %(int(FK, 16)))
#print("FK_CRC: %8X" %(FK_CRC))
#print("FK: ", binascii.hexlify(FK))
#print("FK_CRC: ", binascii.hexlify(FK_CRC)) #'3044383330374432'

hash.update(binascii.hexlify(FK) + binascii.hexlify(FK_CRC))
digest = hash.hexdigest()

encrypted_FK = cipher_encrypt.encrypt(digest)

#hash.update(encrypted_FK)
#digest = hash.hexdigest()
#digest = hash.digest

cipher_decrypt = DES3.new(key, DES3.MODE_CBC, Des3IV)
decrypted_FK = cipher_decrypt.decrypt(encrypted_FK)

print "Encrypted FK: ", binascii.hexlify(encrypted_FK)
print "Digest:       ", digest
print "Decrypted FK: ", decrypted_FK
