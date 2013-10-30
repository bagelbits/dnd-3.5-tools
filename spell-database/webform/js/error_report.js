$("#add_spell").submit(function(event){
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
  var email = $("input#email.add").val();

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


  alert(email_contents);

  event.preventDefault();
});