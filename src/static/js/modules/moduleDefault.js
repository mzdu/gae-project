var titleSort = 0;
var contributorSort = 0;
var dateSort = 0;
var offset = 0;
var limit = 10;

$(document).ready(function(){
	$("#browse").hide();
});

function showBrowse(){
	$("#browse").show("fast");
	
	updateBrowseData("newest");
	
}

function updateBrowseData(sort){
	$("#browse").html("<p>Loading...</p>");
	$.getJSON("/api?method=browseModules&limit="+limit+"&offset="+offset+"&sort="+sort,
		function(json){
			if(json.stat == 'ok'){
					var tempHTML = "<table id = 'browseData'><th class='sortable' onclick='sortBrowsing(\"title\")'>Title</th><th>Version</th><th>Discipline</th><th class='sortable' onclick='sortBrowsing(\"contributor\")'>Contributor</th><th class='sortable' onclick='sortBrowsing(\"date\")'>Date Submitted</th>"
					var pageCount = 1;
					var pageHTML = '';
				for(var i = 0; i < json.title.length; i++){
  					tempHTML += '<tr><td>'+ json.title[i]  +'</td><td>'+ json.version[i] +'</td><td>'+ json.discipline[i] +'</td><td>' + json.contributor[i] + '</td><td>' + json.date_submitted[i] + '</td></tr>';
  					
  				}
  				for(var i = 1; i <= Math.ceil(json.total/limit); i++){
  					pageHTML += " <a href='#' onclick='goToPage(\""+i+"\", \""+sort+"\")'>" + i + "</a> "
  				}
  				if(offset == 0 && json.total > 0 && (json.total-offset) > limit){
  					tempHTML += "</table><button disabled>Previous</button>"+pageHTML+"<button onclick='getNextBrowse(\""+sort+"\")'>Next</button>";
  				}
  				else if(offset > 0 && json.total-offset > limit){
  					tempHTML += "</table><button onclick='getPrevBrowse(\""+sort+"\")'>Previous</button>"+pageHTML+"<button onclick='getNextBrowse(\""+sort+"\")>Next</button>";
  				}
  				else if(offset != 0 && json.total-offset <= limit){
  					tempHTML += "</table><button onclick='getPrevBrowse(\""+sort+"\")'>Previous</button>"+pageHTML+"<button disabled>Next</button>";
  				}
  				else{
  					tempHTML += "</table>";
  				}
  				
  				if((json.total-offset) > limit)
  					tempHTML += " "+offset+" - " +(offset+limit) + " of " + json.total +" modules";
  				else if((json.total-offset) < limit)
  					tempHTML += " "+offset+" - " +(json.total) + " of " + json.total +" modules";
  				$("#browse").html(tempHTML);
			}
			else{
				if(offset > 0)
  					$("#browse").html("<p>No more modules <button onclick='getPrevBrowse(\""+sort+"\")>Previous</button></p>");
  				else
  					$("#browse").html("<p>No modules to browse </p>");
  			}			  	 
		}
  	);
}

function sortBrowsing(sort){
	$("#browseData").remove();
	if(sort == "title"){
		if(titleSort == 0){
			titleSort = 1;
			updateBrowseData("titleDesc");
		}
		else{
			titleSort = 0;
			updateBrowseData("titleAsc");
		}
	}
	else if(sort == "contributor"){
		if(contributorSort == 0){
			contributorSort = 1;
			updateBrowseData("contributorDesc");
		}
		else{
			contributorSort = 0;
			updateBrowseData("contributorAsc");
		}
	}
	else if(sort == "date"){
		if(dateSort == 0){
			dateSort = 1;
			updateBrowseData("oldest");
		}
		else{
			dateSort = 0;
			updateBrowseData("newest");
		}
	}
}

function getNextBrowse(sort){
	offset += 10;
	updateBrowseData(sort);
}
function getPrevBrowse(sort){
	offset -= 10;
	updateBrowseData(sort);
}
function goToPage(number, sort){
	offset = (number-1)*limit;
	updateBrowseData(sort);
}