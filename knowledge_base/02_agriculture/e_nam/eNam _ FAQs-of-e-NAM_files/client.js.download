$(document).ready(function(){
	var baseUrl = $('#base_url').val();


        $(document).on('click','.state_district',function(){	
	    $('#state_click').modal('show'); 
        });
	
        $(document).on('click','.menu_click',function(){	
           window.location.href = $(this).attr('href');
        });

	$(document).on('change','#language_selector',function(){
		var l_id = $(this).val();
		
		$.ajax({
	        type: 'POST',
	        url: baseUrl+'Ajax_ctrl/language_select',
	        dataType: "json",
	        data: {
	        	'l_id'	: l_id
	        },
	        beforeSend: function(){
	        	$('#loader').modal({'show':true});	
	        },
	        complete: function(){},
	        success:function (response) {
	        	$('#loader').modal('toggle');
	        	location.reload();
	        }
		});

                $(document).on('keyup','#site_search',function(event) {
	 	    if (event.keyCode === 13) {
	 	    	$('#site_search_form').submit();
	 	    }
	 	});
	});
	
$(document).on('click','.play-img',function(){
		var v_url = $(this).data('v_url');
                var id = $(this).data('pid');
                $('#iframe1_v_'+id).hide();

		var iframe_id = $(this).data('v_id');
		var x = '<iframe width="229px" height="125px" src="'+v_url+'?autoplay=1" frameborder="0" allowfullscreen></iframe>';
		  var id = $(this).data('v_id');
		  $(this).hide();
		  $('#'+iframe_id).html(x).show();
});

	/*$(document).on('click','.rahul_youtube',function(){
		var v_url = $(this).data('v_url');
		var iframe_id = $(this).data('v_id');
		var x = '<iframe width="229px" height="125px" src="'+v_url+'?autoplay=1" frameborder="0" allowfullscreen></iframe>';
		  var id = $(this).data('v_id');
		  $(this).hide();
		  $('#'+iframe_id).html(x).show();
	});*/
	
	$(document).on('change','#elearing_cat_selector',function(){
		var cat = $(this).val();
		window.location.replace(baseUrl+'elearning/'+cat);
	});
	
	$(document).on('keypress','#video_search_learing',function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
			var cat = $('#elearing_cat_selector').val();
			var text = $(this).val();
			$.ajax({
				type: 'POST',
				url: baseUrl+'Elearning_ctrl/video_search_list',
				dataType: "json",
				data: {
					'cat' : cat,
					'text': text
				},
				beforeSend: function(){
					$('#loader').modal('show');
				},
				complete: function(){},
				success:function (response){
					if(response.status == 200){
						$('#loader').modal('toggle');
						var x = '';
						$.each(response.data,function(key,value){
							var fields = value['v_url'].split('/embed/');
							var street = fields[1];
					x = x + '<div class="col-md-3">' +
							'<div class="row elearn-v-box">' +
								'<div class="col-md-12">'+
									'<div class="thum">'+
										'<div style="background:url(http://img.youtube.com/vi/'+ street +'/0.jpg) center no-repeat;cursor:pointer;height:172px;width:280px;background-size:cover;"></div>'+
										'<a href="'+ baseUrl +'elearning/id/'+ value.video_id +'">'+
											'<img alt="" style="width:64px;" data-pid="'+ value['vid'] +'" class="play-img-gallery" src="'+baseUrl+'assest/images/new-theme/icon/play-ico.png"/>'+
										'</a>'+
									'</div>'+
								'</div>'+
								'<div class="col-md-12 video-g-details">'+
									'<h5><b>'+ value['v_title'] +'</b></h5>'+
									'<p>1025 Views - '+value['created_at']+'</p>'+
								'</div>'+
							'</div>'+
						'</div>';
						});
						$('#video_lists').html(x);
					}
					else{		
						
					}
				}
			});
		}
	});
	
	$('#myCarousel').carousel({
		interval: 3000,
		cycle: true
	});
	
	$(document).on('change','#event_category_selector',function(){
		var cat = $(this).val();
		window.location.replace(baseUrl+'events/'+cat);
	});
	
	$(document).on('keyup','#event_search_gallery',function(){
		var cat = $('#event_category_selector').val();
		var text = $(this).val();
		$.ajax({
			type: 'POST',
			url: baseUrl+'Event_ctrl/event_search_list',
			dataType: "json",
			data: {
				'cat' : cat,
				'text': text
			},
			beforeSend: function(){
				$('#loader').modal({'show':true});
			},
			complete: function(){},
			success:function (response){
				if(response.status == 200){
					$('#loader').modal('toggle');
					var x = '';
					$.each(response.data,function(key,value){
						var fields = value['v_url'].split('/embed/');
						var street = fields[1];
				x = x + '<div class="col-md-3">' +
						'<div class="row elearn-v-box">' +
							'<div class="col-md-12">'+
								'<div class="thum">'+
									'<div style="background:url(http://img.youtube.com/vi/'+ street +'/0.jpg) center no-repeat;cursor:pointer;height:172px;width:280px;background-size:cover;"></div>'+
									'<img alt="" style="width:64px;" data-pid="'+ value['vid'] +'" class="play-img-gallery" src="'+baseUrl+'assest/images/new-theme/icon/play-ico.png"/>'+
								'</div>'+
							'</div>'+
							'<div class="col-md-12 video-g-details">'+
								'<h5><b>'+ value['v_title'] +'</b></h5>'+
								'<p>1025 Views - '+value['created_at']+'</p>'+
							'</div>'+
						'</div>'+
					'</div>';
					});		
					$('#video_lists').html(x);
				}
				else{		
					
				}
			}
		});
	});
	
	
	 $(document).on('click','.event_inst',function(){				
		 var event_id = $(this).data('id');
		 var event_category = $("#event_category_selector").val();
		 var sequence_id = $(this).data('sequence');
			$.ajax({
				type: 'post',
				url: baseUrl+'Event_ctrl/event_gallery_data',
				dataType: "json",
				data:{
					'event_id'  :  event_id,
					'event_category' : event_category,
					'sequence_id' :    sequence_id
				},
				beforeSend: function(){
					$('#loader').modal({'show': true});
				},
				complete: function(){},
				success: function (response){
					console.log(response);
					$('#loader').modal('toggle');
					if(response.status == 200){
						  $.each(response.data.result, function(k, v) {
							$('#modal_image').html('<img style="width:100%;" src="'+baseUrl+'Event_gallary/'+ v.event_image +'">');                  

								var decoded = $('#modal_content').html(v.event_content).text();
									
							$('#modal_content').text(v.decoded);
								
						  });
						
						
						$('#event_instance').modal({'show':true,'backdrop':false});
					}
					else{
						
					}
				}
			});
	 });
	 
	 
	 ///////////////////////////training ////////////////////////////////////////////////////
	 $(document).on('change','#training_state',function(){
		 $('#training_apmc').val('0');
		 var s_id = $(this).val();
		 if(s_id == 0){
			 $('#training_apmc').html('<option value="0">Select APMC</option>');
		 }
		 $.ajax({
		        type: 'POST',
		        url: baseUrl+'Ajax_ctrl/get_all_apmcs',
		        dataType: "json",
		        data: {
		        	's_id' : s_id
		        },
		        beforeSend: function(){
		        	//$('#loader').modal({'show':true});	
		        },
		        complete: function(){},
		        success:function (response) {
		        	//$('#loader').modal('toggle');
		        	if(response.status == 200){
		        		var x = '<option value="0">Select APMC</option>';
		        		$.each(response.data,function(key,value){
		        			x = x + '<option value="'+ value.apmc_code +'">'+ value.name +'</option>'; 
		        		});
		        	$('#training_apmc').html(x);
		        	}
		        }
			});
		 
		 	training_ajax_data();
	 	});
	 
	 	$(document).on('change','#training_apmc',function(){
	 		training_ajax_data();
	 	});
	
	 	$(document).on('keyup','#training_apmc_search',function(){
	 		training_ajax_data();
	 	});
	 	
	 	$(document).on('change','#training_date_from,#training_date_to',function(){
	 		training_ajax_data();
	 	});
		
		
		//////////////////////////////commodity
          
 	$(document).on('keypress','#commodity_search',function(event){
 		        var string = $(this).val();
 		        var keycode = event.which;
                if(keycode == '13'){
                	event.preventDefault();
 		$.ajax({
 		        type: 'POST',
 		        url: baseUrl+'Ajax_ctrl/commodity_search',
 		        dataType: "json",
 		        data: {
 		        	'string' : string,
 		        },
 		        beforeSend: function(){
 		        	$('#loader').modal({'show':true});	
 		        },
 		        complete: function(){
                           $('#loader').modal('toggle');
                        },
 		        success:function (response) {
 		        	console.log(response);
 					if(response.status == 200){
 						var x = '';
 						$.each(response.data,function(key,value){
 							x = x + '<div class="col-md-2">'+
										'<div class="comodity-pro-box">'+
											'<h4>'+ value.commodity_name +'</h4>'+
											'<img alt="" src="'+ baseUrl +'/assest/images/commodity-pro/'+ value.image +'">'+ 
											'<a class="commodity_modal" data-id="'+ value.commodity_id +'" href="javascript:void(0);"> View Quality Parameters</a>'+
										'</div>'+
									'</div>';
 						});	
 						
 						$('#commodity-list').html(x);	
 					}
 				}
 		});	
 	}
   }); 




$(document).on('click','.commodity_modal',function(){
	var id = $(this).data('id');
	$.ajax({
	        type: 'POST',
	        url: baseUrl+'Ajax_ctrl/commodity_parameter',
	        dataType: "json",
	        data: {
	        	'id' : id,
	        },
	        beforeSend: function(){
	        	$('#loader').modal({'show':true});	
	        },
	        complete: function(){},
	        success:function (response) {
				if(response.status == 200){
                                        $('#loader').modal('hide');
					$('#commodity_name').html(response.data[0].comm_name);
					$('#commodity_title_image').attr('src',baseUrl+'assest/images/commodity-pro/'+response.data[0].comm_image);
					$('#commodity_title').html(response.data[0].comm_title);
					$('#commodity_desc').html(response.data[0].comm_desc);
					$('#Wheat_gram').modal('show');
				}
			}
	});
});


hook();



});

function hook(){
	var baseUrl = $('#base_url').val();
	$.ajax({
		    type: 'post',
		    url: baseUrl + 'Ajax_ctrl/hooks_fun',
		    dataType: "json",
		    data: {
		    	
		    },
		    beforeSend: function(){
		    	
		    },
		    complete: function(){},
		    success:function (response) { 
		
		    	console.log(response);
		    	
		    	$('#visitors_count').html(parseInt(156000 + parseInt(response.data)));
		    }
		
		}); 
}

function training_ajax_data(){
	var date1 = $('#training_date_from').val();
		var date2 = $('#training_date_to').val();
		var state_id = $('#training_state').val();
		var apmc_id = $('#training_apmc').val();
		var search_text = $('#training_apmc_search').val();
		$.ajax({
	        type: 'POST',
	        url: baseUrl+'Ajax_ctrl/get_all_training_data_date',
	        dataType: "json",
	        data: {
	        	'date1' : date1,
	        	'date2' : date2,
	        	'state_id' : state_id,
	        	'apmc_id' : apmc_id,
	        	'search_text' : search_text
	        },
	        beforeSend: function(){
	        	//$('#loader').modal({'show':true});	
	        },
	        complete: function(){},
	        success:function (response) {
	        	//$('#loader').modal('toggle');
	        	if(response.status == 200){
	        		var x = '';
	        		var counter = 0;
	        		var res_length = response.data.length;
	        		$.each(response.data,function(key,value){
	        			x = x + '<table class="table table-bordered table-striped">'+
		                    		'<thead>'+
		                            	'<tr>'+
		                            		'<th style="width:7%;" colspan="2">'+ value.state_name +'</th>'+
		                            		'<th style="width:10%;" colspan="3">'+ value.apmc_name +'</th>'+
		                            		'<th class="expand-icon" style="width:10%;text-align:center;" colspan="8"><span  data-toggle="collapse" data-target="#demo_'+ counter +'"><i class="fa fa-plus"></i></span></th>'+
		                            	'</tr>'+
		                    		'</thead>';
		                    		if(value.round){
		                    			var y = '<tbody id="demo_'+ counter +'" class="collapse">'+
					                    			'<tr>'+
				                            		'<td>Round</td>'+
				                            		'<td>APMC code</td>'+
				                            		'<td>Vendor</td>'+
				                            		'<td>Training Plan Date</td>'+
				                            		'<td>Training Date</td>'+
				                            		'<td>No. of Farmers Participated</td>'+
				                            		'<td>No. of Traders Participated</td>'+
				                            		'<td>No. of CA Participated</td>'+
				                            		'<td>APMC Staff Participated</td>'+
				                            		'<td>Other Participants</td>'+
				                            		'<td>Total Participants</td>'+
				                            		'<td>Feedback Score</td>'+
				                            	'</tr>';
		                    			$.each(value.round,function(k,v){
		                    				y = y + '<tr>'+
		                            					'<td>'+ k +'</td>'+
					                            		'<td>'+ v.apmc_id +'</td>'+
					                            		'<td>'+ v.vendor +'</td>'+
					                            		'<td>'+ v.training_plan_date +'</td>'+
					                            		'<td>'+ v.training_date +'</td>'+
					                            		'<td>'+ v.no_of_farmer_participated +'</td>'+
					                            		'<td>'+ v.no_of_traders_participated +'</td>'+
					                            		'<td>'+ v.no_of_ca_participated +'</td>'+
					                            		'<td>'+ v.apmc_staff_participated +'</td>'+
					                            		'<td>'+ v.other_participants +'</td>'+
					                            		'<td>'+ v.total_participants +'</td>'+
					                            		'<td>'+ v.feedback_score +'</td>'+
	                            					'</tr>';
		                    			})
		                    		}
		                    		x = x + y;
		                    		x = x + '</tbody>'+
	            				'</table>';
	            				counter++;
	        		});
	        		$('#trainig_cand_list').html(x);
	        	}
	        }
		});
}



/////min_max_model dashboard
 	function get_all_state(){ 
 		$.ajax({
 		    type: 'GET',
 		    url: 'http://enam.gov.in/NamWebSrv/rest/MastersUpdate/getStates',
 		    dataType: "json",
 		    data: {
 		    	'language' : 'en'
 		    },
 		    beforeSend: function(){
 		    	$('#loader').modal({'show':true});	
 		    },
 		    complete: function(){},
 		    success:function (response) {
 		    	console.log(response);
 		    	var x = '<option value="0">All</option>';
 		    	$.each(response.listStates,function(key,value){
 		    		x = x + '<option label="'+ value.stateDescEn +'" value="string:'+ value.stateId +'">'+ value.stateDescEn +'</option>'; 
 		    	});
 		    	$('#min_max_state').html(x);
 		    }
 		});
 	}
	
	setInterval(function(){
	$.ajax({
		    type: 'post',
		    url: baseUrl + 'Ajax_ctrl/hooks_fun',
		    dataType: "json",
		    data: {
		    	
		    },
		    beforeSend: function(){
		    	
		    },
		    complete: function(){},
		    success:function (response) { 
		
		    	console.log(response);
		    	
				$('#visitors_count').html(parseInt(156000 + parseInt(response.data)));
		    }
		
		}); 
	}, 60000);


function dynamic_fpo_table(){
	var x = ['276','100','22','47','32','296','20','26','28','509','385','46','569'];
	
	table = '';
	for(var i = 0; i < x.length; i++){
		$.ajax({	
		    type: 'POST',
		    url: 'http://enam.gov.in/NamWebSrv/rest/NfclWS/getUserRegisterFPOFPCCount',
		    dataType: "json",
		    data: {
		    	'fromDate' : $('#global_previous_date').val(),
		    	'toDate' : $('#global_current_date').val(),
		    	'stateId' : x[i]
		    },
		    async: false,
		    beforeSend: function(){},
		    complete: function(){},
		    success:function (response) {
		    	if(response.statusMsg == 'S'){
		    		var fpocount = 0;
		    		var state_name = '';
		    		$.each(response.listRegistrationCounterFPOFPCCommonModel,function(k,v){
		    			fpocount = parseInt(fpocount) + parseInt(v.count);
		    			state_name = v.stateName
		    		});
		    		table = table + '<tr><td>'+ parseInt(i+1) +'</td>'+
		    							'<td>'+ state_name +'</td>'+
		    							'<td>'+ fpocount +'</td>'+
		    						'</tr>';
		    	}
		    }
		}); 
	}
	$('#dynamic_fpo_table').html(table);


}
$(function(){
  $('#container').masonry({
    // options
    itemSelector : '.mitem',
    //columnWidth : 215,
gutter: '.marginR'
  });
});

