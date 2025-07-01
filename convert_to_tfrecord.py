import tensorflow as tf
import os
from PIL import Image
import io
import argparse

# Dictionnaire de classes
CLASS_NAMES = {
    'maize_healthy': 0,
    'maize_mildew': 1
}

def create_example(image_bytes, label):
    feature = {
        'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_bytes])),
        'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[label]))
    }
    return tf.train.Example(features=tf.train.Features(feature=feature))

def convert_directory_to_tfrecord(data_dir, output_path):
    num_samples = 0
    with tf.io.TFRecordWriter(output_path) as writer:
        for class_name, label in CLASS_NAMES.items():
            class_path = os.path.join(data_dir, class_name)
            if not os.path.exists(class_path):
                print(f"🔸 Dossier absent : {class_path}")
                continue
            for fname in os.listdir(class_path):
                img_path = os.path.join(class_path, fname)
                try:
                    with Image.open(img_path) as img:
                        img = img.convert('RGB')
                        image_bytes = io.BytesIO()
                        img.save(image_bytes, format='JPEG')
                        image_bytes = image_bytes.getvalue()
                        example = create_example(image_bytes, label)
                        writer.write(example.SerializeToString())
                        num_samples += 1
                except Exception as e:
                    print(f"⚠️ Fichier ignoré ({fname}): {e}")
    print(f"✅ TFRecord généré : {output_path} ({num_samples} exemples)")

# Exécution via CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="Chemin du dossier train ou val")
    parser.add_argument("--output_path", required=True, help="Chemin du fichier de sortie .tfrecord")
    args = parser.parse_args()

    convert_directory_to_tfrecord(args.input_dir, args.output_path)
