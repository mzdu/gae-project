function cleanSearchIndex(){
	json = {}
	json["operation"] = "cleanIndex"
	$.post("/administration/support/",json,function(result){window.location = "/administration/"});
}

function cleanTerms(){
	json = {}
	json["operation"] = "cleanTerms"
	$.post("/administration/support/",json,function(result){window.location = "/administration/"});
}