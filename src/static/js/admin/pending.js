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
				var tableRows = "<thead><tr><th>Title</th><th>Date Submitted</th><th>Date Updated</th><th>ID</th><th>Version</th><th colspan='2'>Operations</th><th>Status</th></tr></thead><tbody>";
				var archivedRows = "<thead><tr><th>Archived Contributions</th><th>Date Submitted</th><th>Date Updated</th><th>ID</th><th>Version</th><th>Status</th></tr></thead><tbody>";
				for(var i = 0; i < json.title.length; i++){
//	  				tableRows += "<tr><td><span style='cursor:pointer;' onclick=featureModule(" + json.uid[i] + ")>Feature</span></td>";
//					tableRows += "<td><a href='/modules/" + json.uid[i] + "/" + json.current_version[i] + "' target='_blank'>" + json.title[i] + "</a></td>";
					if(json.status[i]!="archived"){
						tableRows += "<td><a href='/preview/" + json.key[i] + "' target='_blank'>" + json.title[i] + "</a></td>";
						tableRows += "<td>" + json.date_submitted[i] + "</td>";
						tableRows += "<td>" + json.last_update[i] + "</td>";
						tableRows += "<td><center>" + json.uid[i] + "</center></td>";
						tableRows += "<td><center>" + json.current_version[i] + "</center></td>";
						tableRows += "<td><span style='cursor:pointer;' onclick=acceptModule(" + "'" + json.key[i] + "'" + ")><b>✓</b></span></td>";
						tableRows += "<td><span style='cursor:pointer;' onclick=rejectModule(" + "'" + json.key[i] + "'" + ")><b>X</b></span></td>";
						if (json.status[i]==null){
							tableRows += "<td></td></tr>";
							}
						
						else{
							if(json.status[i]=="flag"){
								tableRows += "<td><img src='/static/images/flag.jpg' width='20px'/></td> </tr>";
							}
							else{
								tableRows += "<td>"+ json.status[i] + "</td> </tr>";
							}
						} 
					}
					else{
						archivedRows += "<td><a href='/preview/" + json.key[i] + "' target='_blank'>" + json.title[i] + "</a></td>";
						archivedRows += "<td>" + json.date_submitted[i] + "</td>";
						archivedRows += "<td>" + json.last_update[i] + "</td>";
						archivedRows += "<td><center>" + json.uid[i] + "</center></td>";
						archivedRows += "<td><center>" + json.current_version[i] + "</center></td>";
						archivedRows += "<td>"+ json.status[i] + "</td> </tr>"
					}
					

//					tableRows += "<td><span style='cursor:pointer;' onclick=obsoleteModule(" + "'" + json.key[i] + "'" + ")><b>Obsolte</b></span></td> </tr>";
					
					tableRows += "<tr><td></td><td colspan='6'><div style='display:none;' id='module_" + json.uid[i] + "'></div></td></tr>";
	  			}
				$(id).append(tableRows + "</tbody>" + archivedRows + "</tbody>");
			}
			else {
				$(id).append("<span>" + json.message + "</span>");
			}
		});
}


function openPrompt(o){
	
	title1 = "Reject";
	link1 = "<div>Please enter user feedback here. Why are the contributions being rejected? What changes (if any) would allow the editor to publish the resubmitted contribution? </div>" +
			"<textarea id='sfaArea1' rows='6' cols='50'></textarea>";
	
	title2 = "Accept";
	link2 = "<div>Accept this module may archive other copies, proceeding?</div>";
	
	if (o.message==1){
		var statesdemo = {
			state0: {
				title:title1,
				html:link1,
				buttons: { "Yes, Reject it": true, "No, Lets Wait": false},
				submit: function(e,v,m,f){
					if(v==true){
						$.getJSON("/api?method=getModule&moduleKey=" + o.key,
								function(json) {
									var atitle = json.title1;
									var aemail = json.email;
									var amodKey = json.modKey;
									var amessage = $("#sfaArea1").val();
									console.log(amessage);
									json = {
											"title": atitle,
											"message1" : amessage,
											"email" : aemail,
											"modKey": amodKey
									}
									
									$.post("/notify2",json,function(){window.location = "/administration/pending/"}
									);
								});						
					}
				}
			}
		};	
	}
	else if (o.message==2){
		var statesdemo = {
			state0: {
				title:title2,
				html:link2,
				buttons: { "Yes, Accept it": true, "No, Lets Wait": false},
				submit: function(e,v,m,f){
					if(v==true){
						$.getJSON("/api?method=publishCurrentVersion&module=" + o.key,
								function(json) {
									if(json.stat == 'ok') {
										window.location = "/administration/pending/";
									}
									else {
										alert(json.message);
									}
								});
							init();					
					}
				}
			}
		
		};	
	}	
	else{
	}
	$.prompt(statesdemo);
	$('div.jqi').css('width','430px');
}

function rejectModule(uKey) {
	openPrompt({message:1, key:uKey});
	init();
}

function acceptModule(uKey) {
	openPrompt({message:2, key:uKey});
	init();
}

function obsoleteModule(uKey) {
	alert('Obsolete current module');
}

function sendFeedback(title, email, modKey){
	var title = title;
	var email = email;
	var modKey = modKey;
	var message = prompt("Improve suggestion?");
	
	json = {
			"title": title,
			"message" : message,
			"email" : email,
			"modKey": modKey
	}
	
	$.post("/notify2",json,function(){window.location = "/administration/pending/"}
	
	);
	
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
	$("#pendingModules").find("tr").remove();
	getPendingModules("#pendingModules");
}
