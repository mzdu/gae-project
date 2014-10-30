function cleanSearchIndex(){
	json = {}
	$.post("/administration/support/",json,function(result){window.location = "/administration/"});
}