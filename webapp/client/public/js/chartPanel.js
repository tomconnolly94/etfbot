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
			yearPerformanceChartDataPanelMessages: []
		}
	},
	methods: {
		dataIsMalformed: function(data) // perform very basic data validation
		{
			let dataKeys = Object.keys(data);
			if(dataKeys.length == 0)
			{
				console.error(`Data is malformed, no object keys found in ${JSON.stringify(data)}.`)
				return true;
			}
			let dataSetsLengths = [];
		
			//assert all the lists in the data dict are the same length
			for(let i = 0; i < dataKeys.length; i++)
			{
				let dataPack = data[dataKeys[i]];
		
				if(typeof dataPack != 'object')
				{
					console.error(`${dataPack} is not an object`)
					return true;
				}
		
				let dataPackValues = data[dataKeys[i]]["values"];
		
				if(typeof dataPackValues != 'object' )
				{
					console.error(`${dataPackValues} is not an object`)
					return true;
				}
		
				if(dataPackValues != null)
					dataSetsLengths.push(dataPackValues.length);
			}
		
			let prevDataSetLength = dataSetsLengths[0];
			for(let i = 0; i < dataSetsLengths.length; i++)
			{
				if(prevDataSetLength != dataSetsLengths[i])
				{
					console.error(`Data is not uniform, some datasets in ${JSON.stringify(data)} were not the same length.`)
					return true;
				}
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
		buildChart: function(data)
		{
			const vueComponent = this;
			const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
			const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
			const labels = [];
			const dates = Object.keys(data["PortfolioPerformance"]["values"]); // SPY500 is the most consistently available data

			for(let i = 0; i < 365; i++)
			{
				let date = dates[i];
				labels.push(date);

				// use the date to add empty fields to our data sets
				if(!(date in data["SPY500"]["values"]))
				{
					data["SPY500"]["values"][date] = null;
				}
				if("CurrentHoldings" in data){
					if(!(date in data["CurrentHoldings"]["values"]))
					{
						data["CurrentHoldings"]["values"][date] = null;
						console.log(`data["CurrentHoldings"]["values"][${date}] = null`)
					}
				}
			}

			const yearGraphData = {
				labels: labels,
				datasets: []
			};

			if("CurrentHoldings" in data) 
				yearGraphData.datasets.push(
					vueComponent.formatGraphData(
						'Current holdings', 
						this.getValuesOrderedByKeys(data["CurrentHoldings"]["values"]), 
						null, 
						false, 
						'rgb(0, 0, 255)', 
						0.1
					)
				)
			if("SPY500" in data) 
				yearGraphData.datasets.push(
					vueComponent.formatGraphData(
						'SPY 500', 
						this.getValuesOrderedByKeys(data["SPY500"]["values"]), 
						null, 
						false, 
						'rgb(0, 255, 0)', 
						0.1
					)
				)
			if("PortfolioPerformance" in data) 
				yearGraphData.datasets.push(
					vueComponent.formatGraphData(
						'Portfolio', 
						this.getValuesOrderedByKeys(data["PortfolioPerformance"]["values"]), 
						null, 
						false, 
						'rgb(255, 0, 0)', 
						0.1
					)
				)
			if("InternalPaperTrading" in data) 
				yearGraphData.datasets.push(
					vueComponent.formatGraphData(
						'InternalPaperTrading', 
						this.getValuesOrderedByKeys(data["InternalPaperTrading"]["values"]), 
						null, 
						false, 
						'rgb(255, 255, 0)', 
						0.1
					)
				)

			const monthGraphData = {
				labels: vueComponent.getFinalThirtyEntries(labels),
				datasets: []
			};
			
			if("CurrentHoldings" in data) 
				monthGraphData.datasets.push(
					vueComponent.formatGraphData(
						'Current holdings', 
						this.getValuesOrderedByKeys(data["CurrentHoldings"]["values"]), 
						vueComponent.getFinalThirtyEntries, 
						false, 
						'rgb(0, 0, 255)', 0.1
					)
				)
			if("SPY500" in data)
				monthGraphData.datasets.push(
					vueComponent.formatGraphData(
						'SPY 500', 
						this.getValuesOrderedByKeys(data["SPY500"]["values"]), 
						vueComponent.getFinalThirtyEntries, 
						false, 
						'rgb(0, 255, 0)', 
						0.1
					)
				)
			if("PortfolioPerformance" in data)
				monthGraphData.datasets.push(
					vueComponent.formatGraphData(
						'Portfolio', 
						this.getValuesOrderedByKeys(data["PortfolioPerformance"]["values"]),
						vueComponent.getFinalThirtyEntries,
						false, 
						'rgb(255, 0, 0)', 
						0.1
					)
				)
			if("InternalPaperTrading" in data) 
				monthGraphData.datasets.push(
					vueComponent.formatGraphData(
						'InternalPaperTrading', 
						this.getValuesOrderedByKeys(data["InternalPaperTrading"]["values"]),
						vueComponent.getFinalThirtyEntries,
						false, 
						'rgb(255, 255, 0)', 
						0.1
					)
				)

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
		formatGraphData: function(label, data, dataFunction, fill, borderColor, tension)
		{
			return {
				label: label,
				data: dataFunction ? dataFunction(data) : data,
				fill: fill,
				borderColor:borderColor,
				tension: tension
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
	},
	beforeMount() {
		const vueComponent = this;
		axios.get(`/getInvestmentPerformanceData`).then((response) => {

			let data = response.data;

			if(vueComponent.dataIsMalformed(data))
				//return;
				console.error("data is malformed");

			vueComponent.buildChart(data);


			vueComponent.monthPerformanceChartDataPanelMessages = [];

			let SPY500CurrentValue = data["SPY500"].currentValue ? (data["SPY500"].currentValue).toFixed(1) : "N/A";
			let SPY500OneMonthPrevValue = data["SPY500"].oneMonthPrevValue ? (data["SPY500"].oneMonthPrevValue).toFixed(1) : "N/A";
			vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("SPY500", SPY500OneMonthPrevValue, SPY500CurrentValue));

			let currentHoldingsCurrentValue;
			let currentHoldingsOneMonthPrevValue;

			if("CurrentHoldings" in data){
				currentHoldingsCurrentValue = data["CurrentHoldings"].currentValue ? (data["CurrentHoldings"].currentValue).toFixed(1) : "N/A";
				currentHoldingsOneMonthPrevValue = data["CurrentHoldings"].oneMonthPrevValue ? (data["CurrentHoldings"].oneMonthPrevValue).toFixed(1) : "N/A";
				vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("CurrentHoldings", currentHoldingsOneMonthPrevValue, currentHoldingsCurrentValue));
			}

			let portfolioPerformanceCurrentValue = data["PortfolioPerformance"].currentValue ? (data["PortfolioPerformance"].currentValue).toFixed(1) : "N/A";
			let portfolioPerformanceOneMonthPrevValue = data["PortfolioPerformance"].oneMonthPrevValue ? (data["PortfolioPerformance"].oneMonthPrevValue).toFixed(1) : "N/A";
			vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("Portfolio", portfolioPerformanceOneMonthPrevValue, portfolioPerformanceCurrentValue));

			vueComponent.yearPerformanceChartDataPanelMessages = [];			

			let SPY500OneYearPrevValue = data["SPY500"].oneYearPrevValue ? (data["SPY500"].oneYearPrevValue).toFixed(1) : "N/A";
			vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("SPY500", SPY500OneYearPrevValue, SPY500CurrentValue));

			if("CurrentHoldings" in data){
				let currentHoldingsOneYearPrevValue = data["CurrentHoldings"].oneYearPrevValue ? (data["CurrentHoldings"].oneYearPrevValue).toFixed(1) : "N/A";
				vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("CurrentHoldings", currentHoldingsOneYearPrevValue, currentHoldingsCurrentValue));
			}
			let portfolioPerformanceOneYearPrevValue = data["PortfolioPerformance"].oneYearPrevValue ? (data["PortfolioPerformance"].oneYearPrevValue).toFixed(1) : "N/A";
			vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("Portfolio", portfolioPerformanceOneYearPrevValue, portfolioPerformanceCurrentValue));
		});
	}
});
