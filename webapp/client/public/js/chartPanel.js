//////////////////////////////////////////////////////////////////////
//
// filename: chartPanel.js
// author: Tom Connolly
// description: Contains chartPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////

// const vars
var charts = [];

// vanilla javascript to destroy charts on page close/reload
window.addEventListener("beforeunload", function(e){
	for(let chartIndex = 0; chartIndex < charts.length; chartIndex++)
		charts[chartIndex].destroy();
	charts = [];
 });



new Vue({
	el: '#chartPanel',
	data() {
		return {
			monthPerformanceChartDataPanelMessages: [],
			yearPerformanceChartDataPanelMessages: [],
			chartColourList:[
				'rgb(255, 0, 0)',
				'rgb(0, 255, 0)',
				'rgb(0, 0, 255)',
				'rgb(255, 255, 0)',
				'rgb(0, 255, 255)',
				'rgb(255, 0, 255)',
				'rgb(255, 255, 255)',
			]
		}
	},
	methods: {
		dataIsMalformed: function(dataKey, data) // perform very basic data validation, return number of values for later
		{
			// example data
			// {
			//		"currentValue": null,
			//		"oneMonthPrevValue": 30.5,
			//		"oneYearPrevValue": 0,
			//		"values": {
			// 			"2025-03-01": 0.99375,
			// 			"2025-03-02": 1.0,
			// 			"2025-03-03": null,
			// 			"2025-03-04": null
			// 			}
			// }

			let dataKeys = Object.keys(data);
			if(dataKeys.length == 0)
			{
				console.error(`Data is malformed, no values found in ${JSON.stringify(data)}.`)
				return 0;
			}

			if(!dataKeys.includes("currentValue") && !dataKeys.includes("oneMonthPrevValue") && !dataKeys.includes("oneYearPrevValue") && !dataKeys.includes("values"))
			{
				console.error(`Data is malformed, at least one data key in ${dataKeys} is missing from in ${JSON.stringify(data)}.`)
				return 0;
			}

			
			return false;
		},
		getValuesOrderedByKeys: function(obj)
		{
			orderedValues = []
			Object.keys(obj).sort()
				.forEach(function(v, i) {
					orderedValues.push(obj[v])
				});
			return orderedValues;
		},
		getAYearOfDates: function()
		{
			Date.prototype.addDays = function(days) {
				var date = new Date(this.valueOf());
				date.setDate(date.getDate() + days);
				return date;
			}
			
			function getDates(latestDate, earliestDate) {
				var dateArray = new Array();
				var currentDate = earliestDate;
				while (currentDate <= latestDate) {
					let dateStringParts = new Date (currentDate).toLocaleDateString("en-GB").split("/");
					dateArray.push(`${dateStringParts[2]}-${dateStringParts[1]}-${dateStringParts[0]}`);
					currentDate = currentDate.addDays(1);
				}
				return dateArray;
			}

			var dateOneYearAgo = new Date();
			dateOneYearAgo.setDate(dateOneYearAgo.getDate() - 365);

			return getDates(new Date(), dateOneYearAgo);
		},
		buildChart: function(data)
		{
			const vueComponent = this;
			const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
			const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
			const labels = [];
			const dataKeys = Object.keys(data);
			const dates = this.getAYearOfDates();

			for(let i = 0; i < 365; i++)
			{
				let date = dates[i];
				labels.push(date);

				// use the date to add empty fields to our data sets
				dataKeys.forEach(dataKey => {
					if(!(date in data[dataKey]["values"]))
						data[dataKey]["values"][date] = null;
				});
			}

			const yearGraphData = {
				labels: labels,
				datasets: []
			};

			const monthGraphData = {
				labels: vueComponent.getFinalThirtyEntries(labels),
				datasets: []
			};

			dataKeyIndex = 0;

			dataKeys.forEach(dataKey => {

				const dataKeyColour = vueComponent.chartColourList[dataKeyIndex % vueComponent.chartColourList.length];

				yearGraphData.datasets.push(
					vueComponent.formatGraphData(
						dataKey,
						this.getValuesOrderedByKeys(data[dataKey]["values"]),
						dataKeyColour
					)
				)

				monthGraphData.datasets.push(
					vueComponent.formatGraphData(
						dataKey,
						vueComponent.getFinalThirtyEntries(this.getValuesOrderedByKeys(data[dataKey]["values"])),
						dataKeyColour
					)
				)
				dataKeyIndex++;
			});

			const yearConfig = {
				type: 'line',
				data: yearGraphData,
				options: {
					spanGaps: true,
					response: true
				}
			};
			
			const monthConfig = {
				type: 'line',
				data: monthGraphData,
				options: {
					spanGaps: true,
					response: true
				}
			};

			for(let chartIndex = 0; chartIndex < charts.length; chartIndex++)
				charts[chartIndex].destroy();

			charts = [];
			charts.push(new Chart(yearPerformanceChartContainer, yearConfig));
			charts.push(new Chart(monthPerformanceChartContainer, monthConfig));
		},
		getFinalThirtyEntries: function(list){
			return list.slice(list.length-30, list.length);
		},		
		formatGraphData: function(label, data, borderColor)
		{
			return {
				label: label,
				data: data,
				fill: false,
				borderColor:borderColor,
				tension: 0.1
			};
		},
		formatDataPanelString: function(label, prevValue, currentValue)
		{
			let change = ((currentValue/prevValue * 100) - 100).toFixed(1);
			if(change >= 0)
				change = `+${change}%`;
			else if(change < 0)
				change = `-${change}%`;
			else
				change = "N/A";

			return `${label} - Start: ${prevValue}, End: ${currentValue}, Change: ${change}.`
		},
		preProcessAndValidateData(data)
		{
			let dataItemValuesLengths = []
			let InternalPaperTradingId = "InternalPaperTrading";
			
			// validate each non InternalPaperTrading data object
			for (let recognisedDataKey of Object.keys(data)) {

				if(recognisedDataKey == InternalPaperTradingId)
					continue;
				
				if(this.dataIsMalformed(recognisedDataKey, data[recognisedDataKey]))
				{
					console.error(`data is malformed key=${recognisedDataKey}`);
					continue;
				}
				dataItemValuesLengths.push(data[recognisedDataKey]["values"].length);
			};

			// validate each InternalPaperTrading data object and flatten the data structure
			let internalPaperTradingData = data[InternalPaperTradingId];
			let internalPaperTradingDataKeys = Object.keys(internalPaperTradingData);
			
			for (let internalPaperTradingDataKey of internalPaperTradingDataKeys) {

				let newDataKey = `InternalPaperTrading_strategy_${internalPaperTradingDataKey}`;

				if(this.dataIsMalformed(newDataKey, internalPaperTradingData[internalPaperTradingDataKey]))
				{
					console.error(`data is malformed key=InternalPaperTrading strategy=${internalPaperTradingDataKey}`);
					continue;
				}
				dataItemValuesLengths.push(internalPaperTradingData[internalPaperTradingDataKey]["values"].length);
				data[newDataKey] = internalPaperTradingData[internalPaperTradingDataKey];
			};

			// assert values field all have the same length
			if(!dataItemValuesLengths.every((val, i, arr) => val === arr[0]))
			{
				console.error(`data is malformed data values are not all of equal value`);
				return;
			}

			// remove now unnecessary InternalPaperTrading field
			delete data[InternalPaperTradingId];
			return data;
		},
		writeGraphLabels(data)
		{
			for (const [key, value] of Object.entries(data)) {
				let currentValue = value.currentValue ? (value.currentValue).toFixed(1) : "N/A";
				let oneMonthPrevValue = value.oneMonthPrevValue ? (value.oneMonthPrevValue).toFixed(1) : "N/A";
				let oneYearPrevValue = value.oneYearPrevValue ? (value.oneYearPrevValue).toFixed(1) : "N/A";
				
				this.monthPerformanceChartDataPanelMessages.push(
					this.formatDataPanelString(
						key, 
						oneMonthPrevValue, 
						currentValue
					)
				);

				this.yearPerformanceChartDataPanelMessages.push(
					this.formatDataPanelString(
						key, 
						oneYearPrevValue, 
						currentValue
					)
				);
			}
		}
	},
	beforeMount() {
		const vueComponent = this;
		axios.get(`/getInvestmentPerformanceData`).then((response) => {

			// example data:
			// {
			// 	"InternalPaperTrading": {
			// 		"1": {
			// 			"currentValue": null,
			// 			"oneMonthPrevValue": 30.5,
			// 			"oneYearPrevValue": 0,
			// 			"values": {
			// 				"2025-03-01": 0.99375,
			// 				"2025-03-02": 1.0,
			// 				"2025-03-03": null,
			// 				"2025-03-04": null
			// 			}
			// 		}
			// 	},
			// 	"PortfolioPerformance": {
			// 		"currentValue": null,
			// 		"oneMonthPrevValue": 5586.38,
			// 		"oneYearPrevValue": 0,
			// 		"values": {
			// 			"2025-03-01": 0.9612093114100239,
			// 			"2025-03-02": 0.9617335793623462,
			// 			"2025-03-03": null,
			// 			"2025-03-04": null
			// 		}
			// 	},
			// 	"SPY500": {
			// 		"currentValue": 583.77001953125,
			// 		"oneMonthPrevValue": 591.6400146484375,
			// 		"oneYearPrevValue": 562.8400268554688,
			// 		"values": {
			// 			"2025-02-26": 0.9699965495763149,
			// 			"2025-02-27": 0.9545135574764407,
			// 			"2025-02-28": 0.9694092307048872,
			// 			"2025-03-03": 0.9524252794071445
			// 		}
			// 	}
			// }

			let data = vueComponent.preProcessAndValidateData(response.data);

			// draw graph
			vueComponent.buildChart(data);

			// write labels for graph
			vueComponent.writeGraphLabels(data);
		});
	}
});
