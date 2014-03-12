//Provides all Javascript functionality for creating a new module.

//HTML constants
var termSearchBoxHTML = '<input type="text" name="q" id="query" autocomplete="off"/> <input id="search" name="searchBtn" type="button" value="Add" onclick="searchBtnClicked()" /> <img src="/static/images/ajax-loader.gif" id="loading" /><br />'

	
	
	var functionGroup = "<select name='function' id='function'><optgroup label='Function'><option>verb</option><option>pronoun</option>"
	+"<option>adjective</option><option>adverb</option><option>preposition</option><option>conjunction</option><option>interjection</option>"
	+"</optgroup><option disabled>——————————</option><optgroup label='Phrase'><option>nounPhrase</option><option>verbPhrase</option>"
	+"<option>prepositionalPhrase</option><option>adjectivalPhrase</option><option>adverbialPhrase</option></select>"


//bind ajax for showTermSearch when documented is loaded
$(document).ready(function(){
		showTermSearch();
		$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});
	$(".removeProposition").bind("click", function(e){
			$(this).parent().remove();
		});
		$(".removeScope").bind("click", function(e){
			$(this).parent().remove();
		});
});

//limit the number of characters
function limitText(limitField, limitCount, limitNum) {
	if (limitField.value.length > limitNum) {
		limitField.value = limitField.value.substring(0, limitNum);
	} else {
		limitCount.value = limitNum - limitField.value.length;
	}
}

function addScope(){
	$("#scope").append("<li><input class='scopeItem' size='100%'/> <button class='removeScope'>X</button></li>");
	$(".removeScope").bind("click", function(e){
			$(this).parent().remove();
		});
		
}

function addProposition(){
	$("#proposition").append("<li><input class='propositionItem' size='100%'/> <button class='removeProposition'>X</button></li>");
	$(".removeProposition").bind("click", function(e){
			$(this).parent().remove();
		});
}

//adds a previously defined term to the list of terms that will be associated with this module when the user submits the module.
function addTerm(term,def,func){
	$("#termList").append("<li><span class='term'>"+ term +"</span> (<span class='termFunction'>" + func + "</span>) - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});

	$("#termResults").html('');
	$("#query").val('');
}

//Adds a previously undefined term and its new definition to the module list
function addNewTerm(){
	var term = $("#query").val();
	var def = $("#defineInput").val();
	var func = $("#function").val();
	$("#termList").append("<li><span class='term'>"+ term +"</span> (<span class='termFunction'>" + func + "</span>) - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});
	
	$("#termResults").html('');
	$("#query").val('');
	$("#termBuilder").html('');
	showTermSearch();
}

//Adds a term with a new definition to the list
function defineExistingTerm(term){
	var def = $("#defineInput").val();
	var func = $("#function").val();
	$("#termList").append("<li><span class='term'>"+ term +"</span> (<span class='termFunction'>" + func + "</span>) - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});
	
	$("#termResults").html('');
	$("#query").val('');
	$("#termBuilder").html('');
	showTermSearch();
}


 
//***********************************************************************START TERM FUNCTIONS

//Called when the 'add' button is clicked in the Term section
function searchBtnClicked(){
	termBuilder($('#query').val());
}
 
function showTermSearch(){
	$('#termBuilder').html(termSearchBoxHTML);
    $('#query').autocomplete({ serviceUrl:'/api?method=getSuggestions',
   							   deferRequestBy: 400,  
   							   width:200,
   							   onSelect: function(value, data){termBuilder(value) 
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
}

//Called when the user attempts to add a term to the list.

//New term cannot be added.termBuilder can be triggered. Function JSON failed to run.

function termBuilder(value){
	$.getJSON("/api?method=getTermDefinitions&term="+value,
			function(json){
				if(json.stat == 'fail'){
					var newTerm = $("#query").val();
					
				    $("#termBuilder").html('<h2>"'+newTerm+'"</h2><input type="hidden" id="query" value = "'+newTerm+'" />Term not defined. Please define this term to begin using it.'+
				    						'<br /> <input id="defineInput" type="text" size="100"/>'+functionGroup+'<button type="button" onclick="addNewTerm()">Define</button><button type="button" onclick="showTermSearch()">Cancel</button>');
					$("#termResults").html('');
				}
				//If the search is successful show the defintion options for the searched term.
				else{
					slug = json.term.replace(' ', '-');
	  				var tempHTML = '';
	  				for(var i = 0; i < json.definitions.length; i++){
	  					tempHTML += '<li><button type="button" onclick="addTerm(\''+ json.term  +'\',\''+ json.definitions[i].definition +'\',\''+ json.definitions[i].func +'\')">-></button>' + json.definitions[i].definition + ' (' + json.definitions[i].func + ') </li>';
	  				}
	  				$("#termResults").html('<p>Choose an existing definition or add a new definition.</p><ul>' + tempHTML + '</ul><input id="defineInput" type="text" size="100"/>'+functionGroup+'<button type="button" onclick="defineExistingTerm(\''+ json.term +'\')">Define</button>')
	  				
	  			}			  	 
			}
	  	);
}
//**************************************************************************END TERM FUNCTIONS

//Enables the submit button after the user clicks 'Ready?'
function enableSubmit(){
	$("#submitBtn").removeAttr("disabled");
	$("#publishBtn").removeAttr("disabled");
	$("#readyBtn").remove();
} 

//Adds hidden input fields for all data that must be posted.
function submitForm(publishBool,action){
	var scopes = [];
	var propositions = [];
	var terms = [];
	var definitions = [];
	var functions = [];
	var title = $("#title").val();
	if(title == ''){
		alert('Please include a title');
		return;
	}
	$(".scopeItem").each(function() { scopes.push($(this).val()) });
	$(".propositionItem").each(function() { propositions.push($(this).val()) });
	$(".term").each(function() { terms.push($(this).html()) });
	$(".definition").each(function() { definitions.push($(this).html()) });
	$(".termFunction").each(function() { functions.push($(this).html()) });
	
	json = {
			"terms" : terms,
			"definitions" : definitions,
			"functions" : functions,
			"meta_theory" : $('#meta_theory').val(),
			"markdown" : $('#wmd-input').val(),
			"propositions" : propositions,
			"scopes" : scopes,
			"published" : publishBool,
			"title" : title,
			"discipline" : $("#discipline").val(),
			"uid" : $("#uid").val()
	}
	$("#submitBtn").remove();
	$("#publishBtn").remove();
	$("#buttons").html("Module is being submitted. If you are not redirected within 10 seconds <a href='/modules'>click here</a>.");
	if(action == "new")
	{
		$.post("/module/new",json,function(){window.location = "/modules"});
	}
	else
	{
		$.post("/module/edit",json,function(){window.location = "/modules"});
	}
}

