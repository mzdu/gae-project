function submitForm()
{
	var newdef = $("#newdef").val().toString();
	var myslug = $("#myslug").text().toString();
	var postUrl = "/terms/"+ myslug; 
	if(newdef == "")
	{
		alert("Empty Definition, please add your definition");
	}
	else{
		json = {
				"slug" : myslug,
				"definition" : newdef
				}
		$("#buttons").html("Definition is being submitted. If you are not redirected within 10 seconds <a href='/terms'>click here</a>.");
		$('ol').append('<li>' + newdef + '</li>')
		$.post(postUrl, json, function(){});
		
	}
}