$(document).ready(function(){
	$("#browse").hide();
});

function showSearch(){
	
	
	$("#browse").show("fast");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="closeSearch()"><a href="#">Close Search</a>');
	
}

function closeSearch(){
	$("#browse").hide("fast");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="showSearch()"><a href="#">Search Modules</a>');
}

function startSearch(){
	alert("hellosearch");
}

function clearSearchResult(){
	$("#searchresult").replaceWith('<div id="searchresult"></div>');
}