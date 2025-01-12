from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from io import BytesIO
from PIL import Image
import numpy as np
import argparse
import requests
import base64
import random
import json
import os

class Encryptor:
    @staticmethod
    def passwordToKey(password: str):
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                iterations=100000,
                salt=b"Tryduck-salt",
                length=32
            )

            return base64.urlsafe_b64encode(kdf.derive(password.encode()))
        except  Exception as e:
            print(f"Error: Failed to generate encryption key. Details: {e}")
            exit(1)
    

    @staticmethod
    def encrypt(key: bytes, data: bytes):
        try:
            cipher = Fernet(key)
            return cipher.encrypt(data)
        except Exception as e:
            print(f"Error: Encryption failed. Details: {e}")
            exit(1)


    @staticmethod
    def decrypt(key: bytes, data: bytes):
        try:
            cipher = Fernet(key)
            return cipher.decrypt(data)
        except Exception as e:
            print(f"Error: Decryption failed. Details: {e}")
            exit(1)

class Tryduck():
    def __init__(self, imagePath, outputPath, password):
        self.imagePath = imagePath
        self.outputPath = outputPath
        self.password = password
        self.tag = b"--tryduck--"

        if os.path.exists(self.outputPath):
            print(f"Error: Output file '{self.outputPath}' already exists. Choose a different name.")
            exit(1)

    def shuffleImage(self, url, rows, cols):
        try:
            generatedKey = Encryptor.passwordToKey(self.password)

            # Load image from URL or local path
            if url is not None:
                response = requests.get(url)
                response.raise_for_status()
                imageData = response.content
            else:
                with open(self.imagePath, "rb") as f:
                    imageData = f.read()

            img = Image.open(BytesIO(imageData))
            npImageData = np.array(img)

            height, width, channels = npImageData.shape

            # Add padding to make dimensions divisible by rows and cols
            padHeight = (rows - (height % rows)) % rows
            padWidth = (cols - (width % cols)) % cols
            paddedImage = np.pad(
                npImageData,
                ((0, padHeight), (0, padWidth), (0, 0)),
                mode="constant",
                constant_values=0
            )

            paddedHeight, paddedWidth, _ = paddedImage.shape
            blockHeight = paddedHeight // rows
            blockWidth = paddedWidth // cols

            # Split into blocks
            blocks = [
                paddedImage[i * blockHeight:(i + 1) * blockHeight, j * blockWidth:(j + 1) * blockWidth]
                for i in range(rows)
                for j in range(cols)
            ]

            # Shuffle blocks
            randomIndices = list(range(len(blocks)))
            random.shuffle(randomIndices)
            reorderedBlocks = [blocks[i] for i in randomIndices]

            # Reconstruct the shuffled image
            npNewImageData = np.vstack([
                np.hstack(reorderedBlocks[i * cols:(i + 1) * cols])
                for i in range(rows)
            ])

            new_img = Image.fromarray(npNewImageData)
            new_img.save(self.outputPath)

            # Save metadata with encryption
            with open(self.outputPath, "ab") as f:
                f.write(self.tag)
                obj = json.dumps({
                    "rows": rows,
                    "cols": cols,
                    "randomIndices": randomIndices,
                    "originalHeight": height,
                    "originalWidth": width
                }).encode()
                f.write(Encryptor.encrypt(generatedKey, obj))

            print(f"Success: Shuffled image saved to '{self.outputPath}'.")

        except Exception as e:
            print(f"Error: Failed to shuffle image. Details: {e}")
            exit(1)

    def restoreImage(self):
        try:
            with open(self.imagePath, "rb") as f:
                imageData = f.read()

            if self.tag not in imageData:
                print("Error: The image was not shuffled by Tryduck.")
                exit(1)

            generatedKey = Encryptor.passwordToKey(self.password)
            imageData, encryptedObj = imageData.split(self.tag)

            # Decrypt metadata
            obj = Encryptor.decrypt(generatedKey, encryptedObj)
            obj = json.loads(obj.decode())

            shufflePattern = obj["randomIndices"]
            rows = int(obj["rows"])
            cols = int(obj["cols"])
            originalHeight = obj["originalHeight"]
            originalWidth = obj["originalWidth"]

            image = Image.open(BytesIO(imageData))
            reorderedImageData = np.array(image)

            height, width, channels = reorderedImageData.shape
            blockHeight = height // rows
            blockWidth = width // cols

            # Split into blocks
            blocks = [
                reorderedImageData[i * blockHeight:(i + 1) * blockHeight, j * blockWidth:(j + 1) * blockWidth]
                for i in range(rows)
                for j in range(cols)
            ]

            # Restore original order
            originalBlocks = [None] * len(blocks)
            for i, idx in enumerate(shufflePattern):
                originalBlocks[idx] = blocks[i]

            # Reconstruct original image
            restoredImgData = np.vstack([
                np.hstack(originalBlocks[i * cols:(i + 1) * cols])
                for i in range(rows)
            ])

            # Crop to original dimensions
            restoredImgData = restoredImgData[:originalHeight, :originalWidth]

            restored_img = Image.fromarray(restoredImgData)
            restored_img.save(self.outputPath)

            print(f"Success: Restored image saved to '{self.outputPath}'.")

        except Exception as e:
            print(f"Error: Failed to restore image. Details: {e}")
            exit(1)
            

def main():
    parser = argparse.ArgumentParser(description="Shuffle and restore images with encryption.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Shuffle command
    shuffleParser = subparsers.add_parser("shuffle", help="Shuffle an image")
    shuffleParser.add_argument("-i", type=str, required=True, help="Path to the input image")
    shuffleParser.add_argument("-u", type=str, help="Url of the image.")
    shuffleParser.add_argument("-r", type=int, default=50, help="Number of rows to split the image")
    shuffleParser.add_argument("-c", type=int, default=50, help="Number of columns to split the image")
    shuffleParser.add_argument("-p", type=str, required=True, help="Password to encrypt the shuffle order")
    shuffleParser.add_argument("-o", type=str, required=True, help="Path to save the shuffled image")

    # Restore command
    restoreParser = subparsers.add_parser("restore", help="Restore a shuffled image")
    restoreParser.add_argument("-i", type=str, required=True, help="Path to the shuffled image")
    restoreParser.add_argument("-p", required=True, type=str, help="Password to decrypt the shuffle order")
    restoreParser.add_argument("-o", type=str, required=True, help="Path to save the restored image")

    args = parser.parse_args()
    tryduck = Tryduck(
        args.i,
        args.o,
        args.p
    )

    if args.command == "shuffle":
        try:
            tryduck.shuffleImage(
                args.u,
                args.r,
                args.c
            )
        except Exception as e:
            print(f"Error: Failed to shuffle image. Details: {e}")
            exit(1)
    elif args.command == "restore":
        try:
            tryduck.restoreImage()
        except Exception as e:
            print(f"Error: Failed to restore image. Details: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()