$(document).ready(function() {

	$("#allCommentsLoading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#allCommentsLoading").ajaxStop(function(){
		$(this).hide();
 	});
   	pathArray = window.location.pathname.split( '/' );
   	init();
});

function addArticleComment(article, comment) {
	$.getJSON("/api?method=addArticleComment&article=" + article + "&comment=" + comment,
		function(json) {
			if(json.stat == 'ok') {
				
			}
			else {
						
			}
	});
	init();
}

function getArticleComments(article) {
	$.getJSON("/api?method=getArticleComments&article=" + article,
		function(json) {
			if(json.stat == "ok") {
				for(var i = 0; i < json.user.length; i++){
	  				$("#allCommentsDiv").append("<div class=\"rounded\"><blockquote>"+ json.comment[i] + "</blockquote><cite><strong>  " + json.user[i] + "</strong>  " + json.comment_date[i] + "</cite></div>");
	  			}
			}
			else {
	  			
			}
	});
}

function init() {	     
	$("#allCommentsDiv").find("div").remove();
	$("#allCommentsDiv").find("blockquote").remove();
	$("#allCommentsDiv").find("cite").remove();
	$("#addCommentBox").val('Add new comment');
	getArticleComments(pathArray[2]);
}
