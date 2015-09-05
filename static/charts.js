
$(function () {


	function get_chart(unit,plotter,kpi){

		kpi = kpi || 'all';

		$.ajax({
			url: '/charts?unit='+unit+'&kpi='+kpi,
			success: function (data) {
				
				var chart_data;
				chart_data = JSON.parse(data).chart_data;
				// console.log(chart_data);
				plotter(chart_data);
			}
		});
	}

	

	$("#month").click(function () {


			get_chart('month',function(chart_data) {
				$.plot("#linechart", [chart_data], {
				xaxis: {mode: "time",
				minTickSize: [1,"month"],
				// min: (new Date(2015, 0, 1)).getTime(),
				// 	max: (new Date(2016, 0, 1)).getTime()

		}
			});
			});
		});

	$("#quarter").click(function () {

		get_chart('quarter',function(chart_data) {
			$.plot("#linechart", [chart_data], {
				xaxis: {mode: "time",
				minTickSize: [1,"quarter"],
				min: (new Date(2015, 0, 1)).getTime(),
					max: (new Date(2016, 0, 1)).getTime()

		}
			});
		});
		});

	$("#year").click(function () {
		get_chart('year',function(chart_data) {
			$.plot("#linechart", [chart_data], {
				xaxis: {mode: "time",
				minTickSize: [1,"year"],
				// min: (new Date(2015, 0, 1)).getTime(),
				// 	max: (new Date(2016, 0, 1)).getTime()

		}
			});
		});
			});
	$("#day").click(function () {
		get_chart('day',function(chart_data) {
				$.plot("#linechart", [chart_data], {
					xaxis: {mode: "time",
					minTickSize: [1,"day"],
					// min: (new Date(2015, 6, 4)).getTime(),
					// 	max: (new Date(2015, 6, 11)).getTime()

			}
				});
			});
			});

		get_chart('day',function(chart_data) {
				$.plot("#linechart", [chart_data], {
					xaxis: {mode: "time",
					minTickSize: [1,"day"],
					// min: (new Date(2015, 6, 4)).getTime(),
					// 	max: (new Date(2015, 6, 11)).getTime()

			}
				});
			});


});