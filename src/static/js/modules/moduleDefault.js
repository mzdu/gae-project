$(document).ready(function(){
	$("#browse").hide();
	
});

function showSearch(){
	$("#browse").show("fast");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="closeSearch()"><a href="javascript:void(0)">Close Search</a>');
  	$('#modulesearch').keypress(function(e) {
        if(e.which == 13) {
        	$('#startSearch').focus().click();
        }
      });	
	
}

function closeSearch(){
	$("#browse").hide("fast");
	$("#searchswitch").replaceWith('<li id="searchswitch" onclick="showSearch()"><a href="javascript:void(0)">Search Modules</a>');
}

function clearSearchResult(){
	$("#searchresult").replaceWith('<div id="searchresult"></div>');
}


function startSearch(){
	clearSearchResult();
	count = 0;
	
	var query = $("#modulesearch").val();
	$.ajax({
		url: '/api?method=searchModules&query=' + query,
		type: 'get',
		dataType: 'json',
		success: function(json){
			if(json.stat == 'ok'){
				if(json.num_results == 0){
					$('#searchresult').replaceWith('<div id="searchresult">No modules found.</div>');
				}
				else{
					$('#searchresult').replaceWith('<div id="searchresult">' + json.num_results + ' closest modules were found.<br/></div>');
					
					while(count<json.num_results){
						
						jsonObj = json.results[count];
						
						html = "<span class='searchTh'>Title : </span>" + jsonObj.title + "<br/>"
							 + "<span class='searchTh'>Keywords: </span>" + jsonObj.keywords + "<br/>"
							 + "<span class='searchTh'>Metatheory: </span>" + jsonObj.metatheory + "<br/>"
							 + "<span class='searchTh'>Terms: </span>" + jsonObj.terms + "<br/>"
							 + "<span class='searchTh'>Propositions: </span>" + jsonObj.propositions + "<br/>" 
						     + "<a href = '/modules/" + jsonObj.docID.toString() + "'>View module details</a><br/><br/>";
						$('#searchresult').append(html)
						
						count = count + 1;
					}
				}
				
			}
				
			
			else{
				alert('json data error');
			}
				
		}
	});

}