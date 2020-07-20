$(document).ready(function(){
	$('.add').click(function(){
		$('#answer_clone').clone(true).appendTo('#answer')
	});

	$('#add-answer').click(function(){
		$('#add_answer').clone(true,true).appendTo('#add_answer')
	});
/*	$('#show-answer').click(function() {
		$('.form-answer').removeClass('form-answer');
	});*/

});