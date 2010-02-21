$(document).ready(function() {

	$("#allTermsLoading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#allTermsLoading").ajaxStop(function(){
		$(this).hide();
 	});

   	init();
});

function getTerms(id) {
	if(id.charAt(0) != '#') id = "#" + id;
	$.getJSON("/api?method=getTerms",
		function(json) {
			if(json.stat == 'ok') {
				var tableRows = "<thead><tr><th>Term</th><th>Date Submitted</th><th>Popularity</th><th></th></tr></thead><tbody>";
				for(var i = 0; i < json.uid.length; i++){
					tableRows += "<td><a href='/terms/" + json.slug[i] + "'>" + json.word[i] + "</a></td>";
					tableRows += "<td>" + json.date_submitted[i] + "</td>";
					tableRows += "<td>" + json.popularity[i] + "</td>";
					tableRows += "<td><span style='cursor:pointer;' onclick=removeTerm(" + json.uid[i] + ")><b>X</b></span></td></tr>";
	  			}
				$(id).append(tableRows + "</tbody>");
			}
			else {
				$(id).append("<span>" + json.message + "</span>");
			}
		});
}

function removeTerm(term) {
	$.getJSON("/api?method=removeTerm&term=" + term,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert("unable to remove term!");
			}
		});
	init();
}

function init() {
	$("#tblTerms").find("tr").remove();
	getTerms("#tblTerms");
}
