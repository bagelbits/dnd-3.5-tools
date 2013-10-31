$("#add").submit(function(event){
  var spell_name = $("input#spell_name.add").val();
  var books = $("input#books.add").val();
  var school = $("input#school.add").val();
  var subschool = $("input#subschool.add").val();
  var descriptor = $("input#descriptor.add").val();
  var levels = $("input#class.add").val();
  var components = $("input#components.add").val();
  var casting_time = $("input#casting_time.add").val();
  var range = $("input#range.add").val();
  var target = $("input#target.add").val();
  var effect = $("input#effect.add").val();
  var area = $("input#area.add").val();
  var duration = $("input#duration.add").val();
  var saving_throw = $("input#saving_throw.add").val();
  var spell_resistance = $("input#spell_resistance.add").val();
  var description = $("textarea#description.add").val();
  
  var from_email = $("input[type=\"email\"].add").val();
  var email_subject = "Add spell: " + spell_name;

  var email_contents = "    " + spell_name + " [" + books + "]\n";
  email_contents = email_contents.concat(school);
  if (subschool !== "") {
    email_contents = email_contents.concat(" (" + subschool + ")");
  }
  if (descriptor !== "") {
    email_contents = email_contents.concat(" [" + descriptor + "]");
  }
  email_contents = email_contents.concat("\nLevel: " + levels + "\n");
  email_contents = email_contents.concat("Components: " + components + "\n");
  if (casting_time !== "") {
    email_contents = email_contents.concat("Casting Time: " + casting_time + "\n");
  }
  if (range !== "") {
    email_contents = email_contents.concat("Range: " + range + "\n");
  }
  if (target !== "") {
    email_contents = email_contents.concat("Target: " + target + "\n");
  }
  if (effect !== "") {
    email_contents = email_contents.concat("Effect: " + effect + "\n");
  }
  if (area !== "") {
    email_contents = email_contents.concat("Area: " + area + "\n");
  }
  if (duration !== "") {
    email_contents = email_contents.concat("Duration: " + duration + "\n");
  }
  if (saving_throw !== "") {
    email_contents = email_contents.concat("Saving Throw: " + saving_throw + "\n");
  }
  if (spell_resistance !== "") {
    email_contents = email_contents.concat("Spell Resistance: " + spell_resistance + "\n");
  }
  description = description.split("\n");
  for(i=0; i<description.length; i++){
    if (!description[i].startsWith("    ")) {
      description[i] = "    ".concat(description[i]);
    }
  }
  description = description.join("\n");

  email_contents = email_contents.concat(description);

  alert(from_email);
  alert(email_subject);
  alert(email_contents);

  event.preventDefault();
});

$("#update").submit(function(event){
  var update_type = $("input.update:checked").val();

  if(! update_type) {
    alert("Please select an update type.");
    event.preventDefault();
    return;
  }

  var from_email = $("input[type=\"email\"].update").val();
  var spell_name = $("input#spell_name.update").val();
  var email_subject = "Add spell: " + spell_name;

  var email_contents = "Update:" + capitalize_first_letter(update_type) + "\n";
  email_contents = email_contents.concat(spell_name + "\n");

  $("li." + update_type + " input").each(function(index){
    if($(this).val() !== ""){
      email_contents = email_contents.concat(capitalize_first_letter($(this).attr('id')) + ": ");
      email_contents = email_contents.concat($(this).val() + "\n");
    }
  });

  alert(from_email);
  alert(email_subject);
  alert(email_contents);

  event.preventDefault();
});

$("#remove").submit(function(event){
  var from_email = $("input[type=\"email\"].remove").val();
  var spell_name = $("input#spell_name.remove").val();
  var email_subject = "Add spell: " + spell_name;
  var email_contents = $("textarea#removal_reason.remove").val();

  alert(from_email);
  alert(email_subject);
  alert(email_contents);

  event.preventDefault();
});

function capitalize_first_letter (word) {
  word = word.charAt(0).toUpperCase() + word.slice(1);
  return word;
}