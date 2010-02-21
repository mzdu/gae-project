//jquery autocomplete plugin
$(document).ready(function() {
    $('#query').autocomplete({ serviceUrl:'/api?method=getSuggestions',
   							   deferRequestBy: 400,  
   							   width:200,
   							   onSelect: function(value, data){showSelectedTerm(value) }
   	});
   	
	$("#loading").ajaxStart(function(){
		$(this).show();
 	});
 	$("#loading").ajaxStop(function(){
		$(this).hide();
 	});
   	 $("#loading").hide();
   	 
   	 $('#query').keypress(function(e) {
        if(e.which == 13) {
            $('#search').focus().click();
        }
    });
   	 
   	 
 });
 
function searchBtnClicked(){
	showSelectedTerm($('#query').val());

}

function showSelectedTerm(value){
	$.getJSON("/api?method=getTermDefinitions&term="+value,
			   function(json){
			     if(json.stat == 'fail'){
			     	$(".oneColumn .header").html('');
			     	$("#searchResult").html('Term not found');
			     }
			     else{
					slug = json.term.replace(' ', '-');
	  			  	$(".oneColumn .header").html("<a href='/terms/"+slug+"'>"+json.term+"</a>");
	  			  	$("#searchResult").html('');
	  			  	var tempArray = new Array();
	  			  	for(var i = 0; i < json.definitions.length; i++){
	  			  		if($("#" + json.definitions[i].func).val() != ''){
	  			  			$("#searchResult").append(json.definitions[i].func + "<div id='" + json.definitions[i].func + "'><ol></ol></div>")
	  			  		}
	  			  		$("#" + json.definitions[i].func + " ol").append('<li>'+json.definitions[i].definition+'</li>');
	  			  		//$("#searchResult").append(json.definitions[i].definition);
	  			  		
	  			  	}
	  			  }		  	   		  			  	   			  	 
  			   }
  			 );
}
