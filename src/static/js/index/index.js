// html controls the content of prezi

	function openPrompt(o){
		
		title1 = $("#title_1").text();
		link1 = '<' + $("#link_1").text();
		
		title2 = $("#title_2").text();
		link2 = '<' + $("#link_2").text();
		
		title3 = $("#title_3").text();
		link3 = '<' + $("#link_3").text();
		
		title4 = $("#title_4").text();
		link4 = '<' + $("#link_4").text();
		
		if (o.prezi==1){
			var statesdemo = {
				state0: {
					title:title1,
					html:link1,
					buttons: { Close: false}

				}
			
			};	
		}
		else if (o.prezi==2){
			var statesdemo = {
				state0: {
					title: title2,
					html:link2,
					buttons: { Close: false}

				}
				
			};				
		}

		else if (o.prezi==3){
			var statesdemo = {
				state0: {
					title: title3,
					html:link3,
					buttons: { Close: false}

				}
			
			};				
		}

		else if (o.prezi==4){
			var statesdemo = {
				state0: {
					title: title4,
					html:link4,
					buttons: { Close: false}

				}
				
			};				
		}				
		
		else{
		}
	
		
		$.prompt(statesdemo);
		$('div.jqi').css('width','585px');
		

	}
