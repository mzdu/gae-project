
function submitArticle(){
	$("#submitBtn").remove();
	$("#buttons").html("Article is being submitted. If you are not redirected within 10 seconds <a href='/articles'>click here</a>.");
	
	json = {
			"body" : $('#wmd-input').val(),
			"title" : $('#title').val()
	}
	$.post("/article/new",json,function(){window.location = "/articles"});
}