$(document).ready(function(){

	var search_field_val=0;

	$(".on-show").hover( function(){
		$(this).css("background","#ccc");
		$(this).css("opacity","1")
	}, function(){
		var list= $(".list-container");
		if ( list.css('display')=='none' ){
			$(this).css("background","#efeff4");
			$(this).css("opacity","1")
		}
	});


	var toggle=0;

	$(document).on("click",".on-show", function(){

		if (toggle==0) {
			$(".on-show").css("background", "#ccc");
			toggle=1;
		} else {
			$(".on-show").css("background", "#efeff4");
			toggle=0;
		}
		var list= $(".list-container");

		if ( list.css('display')=='none' ){
			$(".list-container").show();

		} else {
			$(".list-container").hide();
		}

	});



	$(document).on("click",".litem", function(){

		var litem=$("#"+this.id.toString())[0].innerHTML;
		
		if (litem=="Keyword"){  search_field_val=0;}
		else if (litem=="ProjectX ID"){search_field_val=1;}
		else if (litem=="Title"){search_field_val=2;}

		var element = document.getElementById('on-show-id');
		for (var i=0; i<element.childNodes.length; ++i) {
		    if (element.childNodes[i].nodeType === 3) {
		        element.childNodes[i].textContent=litem;
		    }
		}

		$(".list-container").hide();
		$(".on-show").css("background", "#efeff4");
		toggle=0;


	});



	$(document).mouseup(function (e){

	    var dropdown = $(".dropdown-container");
	    var list= $(".list-container");

	    if (!dropdown.is(e.target) && dropdown.has(e.target).length == 0) {
	        list.hide();
	        $(".on-show").css("background", "#efeff4");
			toggle=0;
	    }
	});

});