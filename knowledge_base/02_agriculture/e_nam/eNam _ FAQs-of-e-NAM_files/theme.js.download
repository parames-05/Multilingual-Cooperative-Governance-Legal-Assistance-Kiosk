jQuery(document).ready(function(){
	var baseUrl = $('#base_url').val();
	$(document).on('click','.green-box',function(){
	$.ajax({
			type:"POST",
			url:baseUrl+'Theme_ctrl/theme_session',
			data:{'theme':'green-theme'},
			dataType:'json',
			beforeSend:function(){},
			success:function(response){
				if(response.status == 200){
					location.reload();
				}
			},
		});
});

$(document).on('click','.red-box',function(){
	$.ajax({
			type:"POST",
			url:baseUrl+'Theme_ctrl/theme_session',
			data:{'theme':'red-theme'},
			dataType:'json',
			beforeSend:function(){},
			success:function(response){
				location.reload();
				if(response.status == 200){
					location.reload();
				}
			},
		});
});

$(document).on('click','.blue-box',function(){
	$.ajax({
			type:"POST",
			url:baseUrl+'Theme_ctrl/theme_session',
			data:{'theme':'blue-theme'},
			dataType:'json',
			beforeSend:function(){},
			success:function(response){
				if(response.status == 200){
					location.reload();
				}
			},
		});
});

$(document).on('click','.orange-box',function(){
	$.ajax({
			type:"POST",
			url:baseUrl+'Theme_ctrl/theme_session',
			data:{'theme':'orange-theme'},
			dataType:'json',
			beforeSend:function(){},
			success:function(response){
				if(response.status == 200){
					location.reload();
				}
			},
		});
});
	
	
	
	
	
	
	 var timerId = 0;
	 timerId = setInterval(function(){ 
	var blink =$("#blink").attr('class');
	if(blink=="blink")
	{
		$("#blink").addClass("blink1").removeClass("blink");
	}
	else
	{
		$("#blink").addClass("blink").removeClass("blink1");
	}
	}, 800);
	
	$("#blink").hover(function(){
	clearInterval(timerId);
	});
	
	$("#blink").mouseout(function(){
	timerId = setInterval(function(){ 
	var blink =$("#blink").attr('class');
	if(blink=="blink")
	{
		$("#blink").addClass("blink1").removeClass("blink");
	}
	else
	{
		$("#blink").addClass("blink").removeClass("blink1");
	}
	}, 800);
	});
	
});
		
		
 jQuery(document).keypress(function(e) {
  if (e.keyCode == 27) {
   
   jQuery(".close").click();
  }
 });
