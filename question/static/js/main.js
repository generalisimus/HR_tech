$(document).ready(function(){
	$('.add').click(function(){
		$('#answer_clone').clone(true).appendTo('#answer')
	});

});