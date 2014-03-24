var titleSort = 0;
var contributorSort = 0;
var dateSort = 0;
var offset = 0;
var limit = 10;

$(document).ready(function(){
	$("#browse").hide();
});

function showSearch(){
	
	
	$("#browse").show("fast");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="closeSearch()"><a href="#">Close Search</a>');
	
}

function closeSearch(){
	$("#browse").hide("slow");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="showSearch()"><a href="#">Search Modules</a>');
}

