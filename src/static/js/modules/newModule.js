//bind ajax for showTermSearch when documented is loaded
$(document).ready(function(){
	
		$.ajax({
			url: '/terms/get',
			type:"get",
			dataType: 'json',
			success: function(data){
				$.each(data, function(key, value){
				    $( "#termlist" ).autocomplete({
				        source: value,
				        select: function(e, ui){getDefinition(e, ui);},
				    	response: function(){showHint();}
				      });
				});
			},
			
			statusCode: {
				405: function(){
					alert('termlist not found');
				}
			}
		});
	
		$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
		});
		$(".removeProposition").bind("click", function(e){
			$(this).parent().remove();
		});
		$(".removeScope").bind("click", function(e){
			$(this).parent().remove();
		});
		$(".removeDerivation").bind("click", function(e){
			$(this).parent().remove();
		});
});


function addScope(){
	$("#scope").append("<li><input class='scopeItem' size='80px'/> <button class='removeScope'>X</button></li>");
	$(".removeScope").bind("click", function(e){
			$(this).parent().remove();
		});
		
}

function addProposition(){
	$("#proposition").append("<li><input class='propositionItem' size='80px'/> <button class='removeProposition'>X</button></li>");
	$(".removeProposition").bind("click", function(e){
			$(this).parent().remove();
		});
}

function addDerivation(){
	$("#derivation").append("<li><input class='derivationItem' size='80px'/> <button class='removeDerivation'>X</button></li>");
	$(".removeDerivation").bind("click", function(e){
			$(this).parent().remove();
		});
}

//adds a previously defined term to the list of terms that will be associated with this module when the user submits the module.
function addTerm(term,def){
	$("#termList").append("<li><span class='term'>"+ term +"</span> - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});

	$("#termResults").html('');
	$("#query").val('');
}

function getDefinition(e,ui){
	selectedValue = ui.item.value;
	console.log = selectedValue;
	$.ajax({
		url: '/api?method=getTermDefinitions&term=' + selectedValue,
		type: 'get',
		dataType: 'json',
		success: function(json){
			if(json.stat == 'fail'){
				alert('json stat error');
			}
			else{
				slug = json.term.replace(' ', '-');
  				var tempHTML = '';
  				for(var i = 0; i < json.definitions.length; i++){
  					tempHTML += '<li><button type="button" onclick="addTerm(\''+ json.term  +'\',\''+ json.definitions[i].definition + '\')">-></button>' + json.definitions[i].definition + '</li>';
  				}
  				$("#termResults").html('<p>Choose an existing definition or add a new definition.</p><ul>' + tempHTML + '</ul><input id="defineInput" type="text" size="80"/>'+'<button type="button" onclick="defineExistingTerm(\''+ json.term +'\')">Add and Use This New Definition</button>');
			}
		}
	});

}

function addTerm(term,def){
	$("#termList").append("<li><span class='term'>"+ term +"</span> - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});

	$("#termResults").html('');
	$("#termlist").val('');
}


function showHint(){
	$("#hint").html('Choose a predefined term from the drop-down list or <a href="javascript: void(0)" onclick="showDef()">ADD A NEW TERM</a>')
}

//Adds a term with a new definition to the list
function defineExistingTerm(term){
	var def = $("#defineInput").val();
	$("#termList").append("<li><span class='term'>"+ term +"</span> - <span class='definition'>" + def + "</span> <button class='removeTerm'>X</button></li>");
	$(".removeTerm").bind("click", function(e){
			$(this).parent().remove();
	});
	
	$("#termResults").html('');
	$("#termlist").val('');
	$("#termBuilder").html('');
	showTermSearch();
}

function showDef(){
	$("#termResults").html('Definition: <input type="text" id="termDefinition" /> <button type="button" onclick="addNewTerm()">Add</button>');
}

function addNewTerm(){
	term = $("#termlist").val();
	def = $('#termDefinition').val();
	addTerm(term, def);
	
}


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
	var derivations = [];
	var terms = [];
	var definitions = [];
	var evidence = $("#evidence").val();

	var title = $("#title").val();
	var keywords = $("#keywords").val();
	
	if(title == ''){
		alert('Please include a title');
		return;
	}
	$(".scopeItem").each(function() { scopes.push($(this).val()) });
	$(".propositionItem").each(function() { propositions.push($(this).val()) });
	$(".derivationItem").each(function() { derivations.push($(this).val()) });
	
	$(".term").each(function() { terms.push($(this).html()) });
	$(".definition").each(function() { definitions.push($(this).html()) });
	
	
	
	json = {
			"title" : title,
			"keywords" : keywords,
			"markdown" : $('#wmd-input').val(),
			"terms" : terms,
			"definitions" : definitions,
			"propositions" : propositions,
			"scopes" : scopes,
			"derivations" : derivations,
			"evidence" : evidence,
			
			"published" : publishBool,
			
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

//limit the number of characters at metatheory
function limitText(limitField, limitCount, limitNum) {
	if (limitField.value.length > limitNum) {
		limitField.value = limitField.value.substring(0, limitNum);
	} else {
		limitCount.value = limitNum - limitField.value.length;
	}
}
