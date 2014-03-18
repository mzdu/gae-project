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
		$("#defBtn").remove();
		$("#buttons").html("Definition is being submitted. If you are not redirected within 10 seconds <a href='/terms'>click here</a>.");
		$.post(postUrl, json, function(){window.location = postUrl});
		
	}
}