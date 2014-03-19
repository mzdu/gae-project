// html controls the content of prezi
	function openPrompt(o){
		if (o.prezi==1){
			var statesdemo = {
				state0: {
					title: 'Wikitheoria 101',
					html:'<iframe src="http://prezi.com/embed/otq-ohhdxcfs/?bgcolor=ffffff&amp;lock_to_path=0&amp;autoplay=0&amp;autohide_ctrls=0&amp;features=undefined&amp;disabled_features=undefined" width="550" height="400" frameBorder="0"></iframe>',
					buttons: { Close: false}

				}
			
			};	
		}
		else if (o.prezi==2){
			var statesdemo = {
				state0: {
					title: 'How To Build a Theory Module',
					html:'<iframe src="http://prezi.com/embed/wnzvks_0hzzq/?bgcolor=ffffff&amp;lock_to_path=0&amp;autoplay=0&amp;autohide_ctrls=0&amp;features=undefined&amp;disabled_features=undefined" width="550" height="400" frameBorder="0"></iframe>',
					buttons: { Close: false}

				}
				
			};				
		}

		else if (o.prezi==3){
			var statesdemo = {
				state0: {
					title: 'How To Build a Theory Module',
					html:'<iframe src="http://prezi.com/embed/wnzvks_0hzzq/?bgcolor=ffffff&amp;lock_to_path=0&amp;autoplay=0&amp;autohide_ctrls=0&amp;features=undefined&amp;disabled_features=undefined" width="550" height="400" frameBorder="0"></iframe>',
					buttons: { Close: false}

				}
				
			};				
		}

		else if (o.prezi==4){
			var statesdemo = {
				state0: {
					title: 'How To Build a Theory Module',
					html:'<iframe src="http://prezi.com/embed/wnzvks_0hzzq/?bgcolor=ffffff&amp;lock_to_path=0&amp;autoplay=0&amp;autohide_ctrls=0&amp;features=undefined&amp;disabled_features=undefined" width="550" height="400" frameBorder="0"></iframe>',
					buttons: { Close: false}

				}
				
			};				
		}				
		
		else{
		}
	
		
		$.prompt(statesdemo);
		$('div.jqi').css('width','585px');
		

	}
