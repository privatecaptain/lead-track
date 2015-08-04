
$(function () {


	
	function get_chart(unit){

		var chart_data;

		$.ajax({
			url: '/charts?unit='+unit,
			async: false,
			success: function (data) {
				
				chart_data = JSON.parse(data).chart_data;
				// console.log(chart_data);
			}
		});
		return chart_data
	}


	$("#month").click(function () {
			$.plot("#linechart", [get_chart('month')], {
				xaxis: {mode: "time",
				minTickSize: [1,"month"],
				// min: (new Date(2015, 0, 1)).getTime(),
				// 	max: (new Date(2016, 0, 1)).getTime()

		}
			});
		});
	$("#week").click(function () {
			$.plot("#linechart", [get_chart('hour')], {
				xaxis: {mode: "time",
				minTickSize: [1,"hour"],
				twelveHourClock: true,
				min: (new Date(2015, 6,24)).getTime(),
					max: (new Date(2015, 6, 25)).getTime()

		}
			});
		});
	$("#quarter").click(function () {
			$.plot("#linechart", [get_chart('quarter')], {
				xaxis: {mode: "time",
				minTickSize: [1,"quarter"],
				min: (new Date(2015, 0, 1)).getTime(),
					max: (new Date(2016, 0, 1)).getTime()

		}
			});
		});
	$("#year").click(function () {
			$.plot("#linechart", [get_chart('year')], {
				xaxis: {mode: "time",
				minTickSize: [1,"year"],
				// min: (new Date(2015, 0, 1)).getTime(),
				// 	max: (new Date(2016, 0, 1)).getTime()

		}
			});
			});
	$("#day").click(function () {
				$.plot("#linechart", [get_chart('day')], {
					xaxis: {mode: "time",
					minTickSize: [1,"day"],
					// min: (new Date(2015, 6, 4)).getTime(),
					// 	max: (new Date(2015, 6, 11)).getTime()

			}
				});
			});


	$.plot($('#linechart'),[get_chart("day")],{
		xaxis: {
			mode: "time"
		}
	});


});