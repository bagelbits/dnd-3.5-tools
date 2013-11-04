<?php
/* Formatting:
  description = description.split("\n");
  for(i=0; i<description.length; i++){
    if (!description[i].startsWith("    ")) {
      description[i] = "    ".concat(description[i]);
    }
  }
  description = description.join("\n");
  email_contents = email_contents.concat(description);
*/

function add_spell_mail_out($form_data){
  $spell_name = $form_data['spell_name'];
  
  $from_email = $form_data['from_email'];
  $email_subject = "Add spell: " . $spell_name;
  $headers = 'From: ' . $from_email . "\r\n" .
    'Reply-To: ' . $from_email . "\r\n" .
    'X-Mailer: PHP/' . phpversion();
  
  $email_contents = "    " . $spell_name . " [" . $form_data['books'] . "]\n";
  $email_contents .= $form_data['school'];
  
  if (array_key_exists('subschool', $form_data)) {
    $email_contents .= " (" . $form_data['subschool'] . ")";
  }
  if (array_key_exists('descriptor', $form_data)) {
    $email_contents .= " [" . $form_data['descriptor'] . "]";
  }

  $email_contents .= "\nLevel: " . $form_data['class'] . "\n";
  $email_contents .= "Components: " . $form_data['components'] . "\n";

  if (array_key_exists('casting_time', $form_data)) {
    $email_contents .= "Casting Time: " . $form_data['casting_time'] . "\n";
  }

  if (array_key_exists('range', $form_data)) {
    $email_contents .= "Range: " . $form_data['range'] . "\n";
  }

  if (array_key_exists('target', $form_data)) {
    $email_contents .= "Target: " . $form_data['target'] . "\n";
  }

  if (array_key_exists('effect', $form_data)) {
    $email_contents .= "Effect: " . $form_data['effect'] . "\n";
  }

  if (array_key_exists('area', $form_data)) {
    $email_contents .= "Area: " . $form_data['area'] . "\n";
  }

  if (array_key_exists('duration', $form_data)) {
    $email_contents .= "Duration: " . $form_data['duration'] . "\n";
  }

  if (array_key_exists('saving_throw', $form_data)) {
    $email_contents .= "Saving Throw: " . $form_data['saving_throw'] . "\n";
  }

  if (array_key_exists('spell_resistance', $form_data)) {
    $email_contents .= "Spell Resistance: " . $form_data['spell_resistance'] . "\n";
  }

  $email_contents .= $form_data['description'];

  mail("spells@fuzzybyt.es", $email_subject, $email_contents, $headers);

}

function update_spell_mail_out($form_data){
  $spell_name = $form_data['spell_name'];
  
  $from_email = $form_data['from_email'];
  $email_subject = "Update spell: " . $spell_name;
  $headers = 'From: ' . $from_email . "\r\n" .
    'Reply-To: ' . $from_email . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

  unset($form_data['spell_name']);
  unset($form_data['from_email']);
  unset($form_data['crud_type']);

  $email_contents = "Update:" . ucwords($form_data['update_type']) . "\n";
  unset($form_data['update_type']);
  $email_contents .= $spell_name . "\n";
  
  foreach ($form_data as $key => $value) {
    $email_contents .= ucwords($key) . ": " . $value . "\n";
  }

  mail("spells@fuzzybyt.es", $email_subject, $email_contents, $headers);
}

function remove_spell_mail_out($form_data){
  $spell_name = $form_data['spell_name'];
  
  $from_email = $form_data['from_email'];
  $email_subject = "Remove spell: " . $spell_name;
  $headers = 'From: ' . $from_email . "\r\n" .
    'Reply-To: ' . $from_email . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

  $email_contents = $form_data['removal_reason'];

  mail("spells@fuzzybyt.es", $email_subject, $email_contents, $headers);
}

function mail_that_shit_out($from_email, $email_subject, $email_contents){
  $to_email = "spells@fuzzybyt.es";
}

//echo(var_dump($_POST));


$form_data = json_decode(file_get_contents('php://input'), true);
if ($form_data["crud_type"] == 'add') {
  add_spell_mail_out($form_data);
} elseif ($form_data["crud_type"] == 'update') {
  update_spell_mail_out($form_data);
} elseif ($form_data["crud_type"] == 'remove') {
  remove_spell_mail_out($form_data);
} else {
  echo "Go away!";
}


/* All form fields are automatically passed to the PHP script through the array $_POST. */
/*
$to_email = "spells@fuzzybyt.es";
$from_email = "From: " + $_POST['from'] + "\r\n";
$subject = $_POST['subject'];
$message = $_POST['message'];

file_put_contents ("test", $to_email + "\n");
file_put_contents ("test", $from_email + "\n", FILE_APPEND);
file_put_contents ("test", $subject + "\n", FILE_APPEND);
file_put_contents ("test", $message + "\n", FILE_APPEND);

if (mail($to_email, $subject, $message, $from_email)) {
  echo "<h4>Thank you for sending email</h4>";
} else {
  echo "<h4>Can't send email to $email</h4>";
}*/

?>