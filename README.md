# Tryduck - Image Shuffler and Restorer with Encryption

Tryduck is a Python tool to shuffle and restore images with added encryption. This utility allows you to split an image into blocks, shuffle them randomly, and encrypt the shuffle pattern. You can later restore the image using the provided password.
<p align=center>
<img src="./test_shuffled_image.jpg">
</p>

## Features

- **Shuffle Images:** Split an image into a grid of blocks, shuffle the blocks, and save the shuffled image.
- **Encrypt Shuffle Pattern:** Secure the shuffle pattern using a password with PBKDF2 and AES encryption.
- **Restore Images:** Decrypt and reconstruct the original image using the correct password.
- **Support for Local and URL Images:** Shuffle images from local files or directly from URLs.

## Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/tryduck.git
cd tryduck
```
2. Install the dependencies:
```bash
pip install -r requirements.txt
```


#### Testing
- To test the restoration functionality, a sample shuffled image is provided with this repository.
- The password for the provided image is: 123
- You can use the following command to restore the test image
```bash
python tryduck.py restore -i test_shuffled_image.jpg -o restored_test_image.jpg -p 123
```

## Usage
- The script provides two main commands: shuffle and restore.

> [!IMPORTANT]
> - When the file gets edited, secure contents of the file are lost.
> - There is no recovery option if you forget the password.

#### Shuffle Command
- Split an image into blocks, shuffle them, and save the encrypted shuffled image.

#### Example:
```bash
python tryduck.py shuffle -i image.jpg -o shuffled_image.jpg -p mypassword -r 30 -c 30
```

#### Arguments:

```bash
python tryduck.py shuffle -i <input_image_path> -o <output_image_path> -p <password> [-u <image_url>] [-r <rows>] [-c <columns>]
```

- `-i`  Path to the input image (required).
- `-u` URL of the image (optional, overrides -i).
- `-o` Path to save the shuffled image (required).
- `-p` Password for encryption (required).
- `-r` Number of rows to split the image (default: 50).
- `-c` Number of columns to split the image (default: 50).

#### Restore Command
- Decrypt and restore the original image from a shuffled image.

#### Example:
```bash
python tryduck.py restore -i shuffled_image.jpg -o restored_image.jpg -p mypassword
```

#### Arguments:
```bash
python tryduck.py restore -i <shuffled_image_path> -o <output_image_path> -p <password>
```

- `-i` Path to the shuffled image (required).
- `-o` Path to save the restored image (required).
- `-p` Password to decrypt the shuffle order (required).