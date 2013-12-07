$("#add, #remove").submit(function(event){
  var crud_type = $(this).attr('id');
  var spell_form_data = {"crud_type": $(this).attr('id')};

  $("input." + crud_type + ", textarea." + crud_type).each(function(index){
    if($(this).val() !== ""){
      spell_form_data[$(this).attr('id')] = $(this).val();
    }
  });

  
  $.post( "php/mail_out.php", JSON.stringify(spell_form_data));
  
  alert("Thank you for submitting!");
  $("input." + crud_type + ", textarea." + crud_type).val("");
  event.preventDefault();
  event.stopPropagation();
});

$("#update").submit(function(event){
  var update_type = $("input.update:checked").val();

  if(! update_type) {
    alert("Please select an update type.");
    event.preventDefault();
    return;
  }

  var update_spell_form_data = {"crud_type": "update",
                             "update_type": update_type,
                             "spell_name": $("input.update#spell_name").val(),
                             "from_email": $("input.update#from_email").val()};

  $("li." + update_type + " input, li." + update_type + " textarea").each(function(index){
    if($(this).val() !== ""){
      update_spell_form_data[$(this).attr('id')] = $(this).val();
    }
  });

  $.post( "php/mail_out.php", JSON.stringify(update_spell_form_data));

  alert("Thank you for submitting!");

  $("input, textarea").val("");
  event.preventDefault();
  event.stopPropagation();
});
