<?php

#-- Upload immagine --
$target_dir = "uploads/";


$filename = shell_exec("python get_filename.py --dir " . $target_dir);
$filename = trim($filename);
$imageFileType = strtolower(pathinfo(basename($_FILES["file"]["name"]),PATHINFO_EXTENSION));
$target_file = $target_dir . $filename . "." . $imageFileType;
$uploadOk = 1;
$errore = "";


// Check if image file is a actual image or fake image
$check = getimagesize($_FILES["file"]["tmp_name"]);
if($check !== false) {
  #echo "File is an image - " . $check["mime"] . ".";
  $uploadOk = 1;
} else {
  $errore = "Errore: il file passato non è un'immagine.";
  $uploadOk = 0;
}

// Check if file already exists
if (file_exists($target_file)) {
  $errore = $errore . "\nErrore: file già esistente nel server.";
  $uploadOk = 0;
}

// Check file size --> MAX: 10 Mb
if ($_FILES["file"]["size"] > 10000000) {
  $errore = $errore . "\nErrore: file troppo grande (max 10 MB).";
  $uploadOk = 0;
}

// Allow certain file formats
if($imageFileType != "jpg" && $imageFileType != "jpeg") {
  $errore = $errore . "\nErrore: si accettano solo immagini .jpg / .jpeg.";
  $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
  echo $errore;
// if everything is ok, try to upload file
} else {

  $a = move_uploaded_file($_FILES["file"]["tmp_name"], $target_file);
  if ($a) {

    //-- Esecuzione python DBR --
    $command = "python3 /var/www/html/DBR/predict.py --fn /var/www/html/" . $target_file;
    $out = shell_exec($command);
    echo $out;

    //-- Elimina foto dal server --
    unlink($target_file);
  } else {
    echo "Errore: caricamento dell'immagine fallito.";
  }

}

?>
