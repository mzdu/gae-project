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

function clearSearchResult(){
	$("#searchresult").replaceWith('<div id="searchresult"></div>');
}


function startSearch(){
	var query = $("#modulesearch").val();
	$.ajax({
		url: '/api?method=searchModules&query=' + query,
		type: 'get',
		dataType: 'json',
		success: function(json){
			if(json.stat == 'fail'){
				alert('json stat error');
			}
			else{
				slug = json.term.replace(' ', '-');
  				var tempHTML = '';
  				for(var i = 0; i < json.definitions.length; i++){
  					tempHTML += '<li><button type="button" onclick="addTerm(\''+ json.term  +'\',\''+ json.definitions[i].definition + '\')">-></button>' + json.definitions[i].definition + '</li>';
  				}
  				$("#termResults").html('<p>Choose an existing definition or add a new definition.</p><ul>' + tempHTML + '</ul><input id="defineInput" type="text" size="80"/>'+'<button type="button" onclick="defineExistingTerm(\''+ json.term +'\')">Add and Use This New Definition</button>');
			}
		}
	});

}