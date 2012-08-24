$(document).ready(function() {

	$("#allArticlesLoading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#allArticlesLoading").ajaxStop(function(){
		$(this).hide();
 	});

   	init();
});

function getArticles(id) {
	if(id.charAt(0) != '#') id = "#" + id;
	$.getJSON("/api?method=getArticles",
		function(json) {
			if(json.stat == 'ok') {
				var tableRows = "<thead><tr><th></th><th>Title</th><th>Date Published</th><th></th><th></th></tr></thead><tbody>";
				for(var i = 0; i < json.title.length; i++){
	  				tableRows += "<tr><td><span style='cursor:pointer;' onclick=featureArticle(" + json.uid[i] + ")>Feature</span></td>";
					tableRows += "<td><a href='/articles/" + json.uid[i] + "'>" + json.title[i] + "</a></td>";
					tableRows += "<td>" + json.date_pub[i] + "</td>";
					tableRows += "<td><span style='cursor:pointer;' onclick=removeArticle(" + json.uid[i] + ")><b>X</b></span></td></tr>";
	  			}
				$(id).append(tableRows + "</tbody>");
			}
			else {
				$(id).append("Failed to load Articles!");
			}
		});
}

function getFeaturedArticle() {
	$.getJSON("/api?method=getFeaturedArticle",
		function(json) {
			if(json.stat == 'ok') {
				$("#featuredAdminContentFound").append("<span><b>Featured: </b><a href='/articles/" + json.uid + "'>" + json.title + "</a></span>");
			}
			else {
				$("#featuredAdminContentFound").append("<span><b>Unable to load featured article!</b></span>");
			}
		});
}

function featureArticle(article) {
	$.getJSON("/api?method=featureArticle&article=" + article,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert("unable to feature article!");
			}
		});
		init();
}

function removeArticle(article) {
	$.getJSON("/api?method=removeArticle&article=" + article,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
				alert("unable to remove article!");
			}
		});
	init();
}

function init() {
	$("#featuredAdminContentFound").find("span").remove();
	$("#tblArticles").find("tr").remove();
	getArticles("#tblArticles");
	getFeaturedArticle();
}
