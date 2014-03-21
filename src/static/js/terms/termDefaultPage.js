//jquery autocomplete plugin
$(document).ready(function() {
	$.ajax({
		url: '/terms/get',
		type:"get",
		dataType: 'json',
		success: function(data){
			$.each(data, function(key, value){
			    $( "#termlist" ).autocomplete({
			        source: value,
			        select: function(e, ui){showSelectedTerm(e, ui);},
			      });
			});
		},
		
		statusCode: {
			405: function(){
				alert('termlist not found');
			}
		}
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

function replaceAll(find, replace, str) {
	  return str.replace(new RegExp(find, 'g'), replace);
}

function showSelectedTerm(e, ui){
	selectedValue = ui.item.value;
	slug = replaceAll(' ','-',selectedValue)
	$.getJSON("/api?method=getTermDefinitions&term="+selectedValue,
			   function(json){
			     if(json.stat == 'fail'){
			     	$(".oneColumn .header").html('');
			     	$("#searchResult").html('Term not found');
			     }
			     else{
	  			  	$(".oneColumn .header").html("<a href='/terms/"+slug+"'>"+selectedValue+"</a>");
	  			  	$("#searchResult").html('');
	  			  	var tempArray = new Array();
	  			  	for(var i = 0; i < json.definitions.length; i++){
	  			  		if($("#" + json.definitions[i].func).val() != ''){
	  			  			$("#searchResult").append("<strong><a href='/terms/" + slug + "'>" + selectedValue + "</a></strong>" + "<div id='" + json.definitions[i].func + "'><ol></ol></div>")
	  			  		}
	  			  		$("#" + json.definitions[i].func + " ol").append('<li>'+json.definitions[i].definition+'</li>');
	  			  		//$("#searchResult").append(json.definitions[i].definition);
	  			  		
	  			  	}
	  			  }		  	   		  			  	   			  	 
  			   }
  			 );
}
