$(document).ready(function() {

	$("#allModulesLoading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#allModulesLoading").ajaxStop(function(){
		$(this).hide();
 	});

   	init();
});

function getCurrentModules(id) {
	if(id.charAt(0) != '#') id = "#" + id;
	$.getJSON("/api?method=getCurrentModules",
		function(json) {
			if(json.stat == 'ok') {
				var tableRows = "<thead><tr><th>Title</th><th>Date Submitted</th><th>Last Update</th><th>Current Version</th><th></th><th></th></tr></thead><tbody>";
				for(var i = 0; i < json.title.length; i++){
//	  				tableRows += "<tr><td><span style='cursor:pointer;' onclick=featureModule(" + json.uid[i] + ")>Feature</span></td>";
					tableRows += "<td><a href='/modules/" + json.uid[i] + "' target='_blank'>" + json.title[i] + "</a></td>";
					tableRows += "<td>" + json.date_submitted[i] + "</td>";
					tableRows += "<td>" + json.last_update[i] + "</td>";

					tableRows += "<td><center>" + json.current_version[i] + "</center></td>";
//					tableRows += "<td><span style='cursor:pointer;' onclick='getPastModules(" + json.uid[i] + ")'>View Versions</span></td>";
					tableRows += "<td><span style='cursor:pointer;' onclick=removeModule(" + json.uid[i] + ")><b>X</b></span></td></tr>";
					tableRows += "<tr><td></td><td colspan='6'><div style='display:none;' id='module_" + json.uid[i] + "'></div></td></tr>";
	  			}
				$(id).append(tableRows + "</tbody>");
			}
			else {
				$(id).append("<span>" + json.message + "</span>");
			}
		});
}

function getPastModules(uid) {
	$("#module_" + uid).toggle("fast");
	$.getJSON("/api?method=getPastModules&module=" + uid,
		function(json) {
			if(json.stat == 'ok') {
				var tableRows = "<table><thead><tr><th>Title</th><th>Date Submitted</th><th>Version</th></tr></thead><tbody>";
				for(var i = 0; i < json.title.length; i++){
					tableRows += "<tr><td><a href='/modules/" + json.uid[i] + "/" + json.version[i] + "'>" + json.title[i] + "</a></td>";
					tableRows += "<td>" + json.date_submitted[i] + "</td>";
					tableRows += "<td>" + json.version[i] + "</td>";
					tableRows += "<td><span style='cursor:pointer;' onclick='setCurrentVersion(" + json.uid[i] + "," + json.version[i] + ")'>Set as Current Version</span></td>";
	  			}
				$("#module_" + uid).append(tableRows + "</tbody></table>");
			}
			else {
				$("#module_" + uid).append("<span>" + json.message + "</span>");
			}
		});
	$("#module_" + uid).find("table").remove();
	$("#module_" + uid).find("span").remove();
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
 
function getFeaturedModule() {
	$.getJSON("/api?method=getFeaturedModule",
		function(json) {
			if(json.stat == 'ok') {
				$("#featuredAdminContentFound").append("<span><b>Featured: </b><a href='/modules/" + json.uid + "'>" + json.title + "</a></span>");
			}
			else {
				$("#featuredAdminContentFound").append("<span><b>Unable to load featured module!</b></span>");
			}
		});
}

function getPendingModules() {
	$.getJSON("/api?method=getPendingModule",
		function(json) {
			if(json.stat == 'ok') {
				$("#featuredAdminContentFound").append("<span><b>Pending: </b><a href='/modules/" + json.uid + "'>" + json.title + "</a></span>");
			}
			else {
				$("#featuredAdminContentFound").append("<span><b>Unable to load pending module!</b></span>");
			}
		});
}


function featureModule(module) {
	$.getJSON("/api?method=featureModule&module=" + module,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert("unable to feature module!");
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
	$("#tblModules").find("tr").remove();
	getCurrentModules("#tblModules");
//	getFeaturedModule();
}
