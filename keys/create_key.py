import rsa
import pickle

if __name__ == "__main__":
	### Username to create key for
	username = "taylor"
	
	### Create key
	(s_key_pub, s_key_priv) = rsa.newkeys(512)
	
	### save keys
	with open(username+'_key_pub.pem', mode='wb') as privatefile:
		privatefile.write(rsa.PublicKey.save_pkcs1(s_key_pub))
	with open(username+'_key_priv.pem', mode='wb') as privatefile:
		privatefile.write(rsa.PrivateKey.save_pkcs1(s_key_priv))
