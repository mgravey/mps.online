var jobId=0;
var waitingList=0;
var updateDelay=1000;

function init(){
	$('#height').val(200);
	$('#width').val(200);
	$('#imageSizeVisualize').height($('#height').val());
	$('#imageSizeVisualize').width($('#width').val());
	$('#numberOfNeighbors').val(50);
	$('#numberOfNeighborsValue').html($('#numberOfNeighbors').val());
	$('#numberOfCandidates').val(0.2);
	$('#numberOfCandidatesValue').html(Math.round(Math.exp($('#numberOfCandidates').val())*100)/100);
	$('#seed').val(Math.floor(Math.random()*4294967295+1));
	simSizeDisplay();
}

function resetForNewSim(){
	$('#progressBar').show();
	animationS.set(0);
	$('#simDisplay').hide();
}

function simSizeDisplay(){
	$('#simSizeDisplay').html($('#height').val()+' x '+ $('#width').val())
}

$( document ).ready(function(){
	$('#height').on('input change',function(){
		$('#imageSizeVisualize').height($(this).val());
		resetForNewSim();
		simSizeDisplay();
	});
	$('#width').on('input change',function(){
		$('#imageSizeVisualize').width($(this).val());
		resetForNewSim();
		simSizeDisplay();
	})
	$('#numberOfNeighbors').on('input change',function(){
		$('#numberOfNeighborsValue').html($(this).val());
	})
	$('#numberOfCandidates').on('input change',function(){
		$('#numberOfCandidatesValue').html(Math.round(Math.exp($(this).val())*100)/100);
	})
	$('#external-ti').on('change',function(){
		$('#file-ti').prop('required',$('#external-ti').prop('checked'));
	})
	init();

	animationS = new ProgressBar.Path('#fill-S', {
		easing: 'linear',
	});
	resetForNewSim()
})

startTime=0;

function updateProgression(){
	var value={
		jobId:jobId
	}

	$.ajax({
		type: 'POST',
		url: 'qsStatusOrResult',
		data: value,
		success: function(data){
			data=JSON.parse(data);
			progress=data.progress;
			//waitingList=data.WL;
			if ('sim' in data){
				dur=updateDelay*1.5;//((new Date().getTime())-startTime)/progress*(1-progress)*1.5;
				animationS.animate(1.0,{duration: dur},function(){
					$('#progressBar').hide();
					$('#simDisplay').attr('src','data:image/png;base64, '+data.sim);
					$('#simDisplay').show();
				});
			}else{
				animationS.animate(progress/100);
				setTimeout('updateProgression()',updateDelay);
			}
		},
		dataType: 'html'
	});
}

function runSimulation(){
	event.preventDefault();
	resetForNewSim();

	var value = new FormData();
	value.append('uploadedImage',$('#file-ti')[0].files[0]);
	value.append('ti',$("input[name='ti']:checked").val());
	value.append('n',$('#numberOfNeighbors').val()*1);
	value.append('k',Math.round(Math.exp($('#numberOfCandidates').val())*100)/100);
	value.append('h',$('#height').val()*1);
	value.append('w',$('#width').val()*1);
	value.append('s',$('#seed').val()*1);
	value.append('emailAddress',$('#emailAddress').val());

	$.ajax({
		type: 'POST',
		url: 'qsRun',
		data: value,
		processData: false,
		contentType: false,
		success: function(data){
			data=JSON.parse(data);
			if(data.hasOwnProperty('error')){
				alert(data.error);
				return;
			}
			jobId=data.jobId;
			waitingList=data.WL;
			startTime=new Date().getTime();
			setTimeout('updateProgression()',updateDelay);
		},
		dataType: 'html'
	});
}
