$(document).ready(function() {

	$("#allModulesLoading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#allModulesLoading").ajaxStop(function(){
		$(this).hide();
 	});

   	init();
});

function getPendingModules(id) {
	if(id.charAt(0) != '#') id = "#" + id;
	$.getJSON("/api?method=getPendingModules",
		function(json) {
			if(json.stat == 'ok') {
				var tableRows = "<thead><tr><th>Title</th><th>Date Submitted</th><th>Date Updated</th><th>Version</th><th></th><th></th></tr></thead><tbody>";
				for(var i = 0; i < json.title.length; i++){
//	  				tableRows += "<tr><td><span style='cursor:pointer;' onclick=featureModule(" + json.uid[i] + ")>Feature</span></td>";
					tableRows += "<td><a href='/modules/" + json.uid[i] + "/" + json.current_version[i] + "' target='_blank'>" + json.title[i] + "</a></td>";
					tableRows += "<td>" + json.date_submitted[i] + "</td>";
					tableRows += "<td>" + json.last_update[i] + "</td>";
					tableRows += "<td><center>" + json.current_version[i] + "</center></td>";
					
					tableRows += "<td><span style='cursor:pointer;' onclick=acceptModule(" + json.uid[i] + ")><b>✓</b></span></td>";
					tableRows += "<td><span style='cursor:pointer;' onclick=rejectModule(" + json.uid[i] + ")><b>X</b></span></td> </tr>";	
					
					tableRows += "<tr><td></td><td colspan='6'><div style='display:none;' id='module_" + json.uid[i] + "'></div></td></tr>";
	  			}
				$(id).append(tableRows + "</tbody>");
			}
			else {
				$(id).append("<span>" + json.message + "</span>");
			}
		});
}


function acceptModule(uid) {
	alert('accept it');
}


function rejectModule(uid) {
	alert('reject it');
}


function setCurrentVersion(uid, version) {
	$.getJSON("/api?method=setCurrentVersion&module=" + uid + "&version=" + version,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert(json.message);
			}
		});
	init();
}
 




function removeModule(module) {
	$.getJSON("/api?method=removeModule&module=" + module,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert("unable to remove module!");
			}
		});
	init();
}

function init() {
	$("#featuredAdminContentFound").find("span").remove();
	$("#pendingModules").find("tr").remove();
	getPendingModules("#pendingModules");
//	getFeaturedModule();
}
