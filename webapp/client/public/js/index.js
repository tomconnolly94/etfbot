//////////////////////////////////////////////////////////////////////
//
// filename: index.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////

// create bus for communication between vue instances
Vue.prototype.$bus = new Vue();


// const vars
var homeUrl = "/"
var charts = [];

new Vue({
	el: '#triggerPanel',
	data() {
		return {
			responseMessage: "",
			outputLogs: [],
			running: false,
			startTime: null,
			originalSpinnerParentClass: "col-sm-6 col-xl-4",
			spinnerParentClass: this.originalSpinnerParentClass
		}
	},
	methods: {
		runInvestmentBalancer: function (){
			console.log("runInvestmentBalancer called.")

			if (this.running){
				return;
			}

			this.running = true;
			this.startTime = new Date().toLocaleString();
			this.spinnerParentClass = "col-sm-8"
			this.responseMessage = "";
			this.outputLogs = [];
			vueComponent = this;

			axios.get(`/runInvestmentBalancer`).then((response) => {
				vueComponent.cleanUpInvestmentAppRun(true, response);
			}).catch(function(error){
				vueComponent.cleanUpInvestmentAppRun(false, error);
			});
		},
		cleanUpInvestmentAppRun: function(success, response){
			var successStr = success ? "successfully" : "unsuccessfully";
			console.log(`runInvestmentApp finished ${successStr}.`);
			this.responseMessage = `InvestmentApp run ${successStr} at ${vueComponent.startTime}`
			this.running = false;
			this.spinnerParentClass = this.originalSpinnerParentClass;
			if(response.data && response.data.logs)
				this.outputLogs = response.data.logs;
			if(success)
				getData();
		}
	}
});

function getData(){
	axios.get(`/getInvestmentPerformanceData`).then((response) => {
		buildChart(response.data);
	})
}


// perform very basic data validation
function dataIsMalformed(data)
{
	let dataKeys = Object.keys(data);
	if(dataKeys.length == 0)
	{
		console.log(`Data is malformed, no object keys found in ${JSON.stringify(data)}.`)
		return true;
	}
	let dataSetsLengths = [];

	//assert all the lists in the data dict are the same length

	for(let i = 0; i < dataKeys.length; i++)
	{
		if(data[dataKeys[i] != null])
			dataSetsLengths.push(data[dataKeys[i]].length);
	}

	let prevDataSetLength = dataSetsLengths[0];
	for(let i = 0; i < dataSetsLengths.length; i++)
	{
		if(prevDataSetLength != dataSetsLengths[i])
		{
			console.log(`Data is not uniform, some datasets in ${JSON.stringify(data)} were not the same length.`)
			return true;
		}
	}

	return false;
}

function getFinalThirtyEntries(list){
	return list.slice(list.length-30, list.length);
}

function formatGraphData(label, data, dataFunction, fill, borderColor, tension)
{
	return {
		label: label,
		data: dataFunction ? dataFunction(data) : data,
		fill: fill,
		borderColor:borderColor,
		tension: tension
	};
}

// translate this function to be vue compatible
function buildChart(data){

	const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
	const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
	const labels = [];
	const dataKeys = Object.keys(data["SPY500"]);

	if(dataIsMalformed(data))
		return;
	
	for(let i = 0; i < dataKeys.length; i++)
	{
		let dateParts = new Date(dataKeys[i]*1000).toUTCString().split(" ");
		let date = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]}`
		labels.push(date);
	}
	const yearGraphData = {
		labels: labels,
		datasets: [
			data["CurrentHoldings"] ? formatGraphData('Current holdings', Object.values(data["CurrentHoldings"]), null, false, 'rgb(0, 255, 0)', 0.1) : {},
			data["SPY500"] ? formatGraphData('SPY 500', Object.values(data["SPY500"]), null, false, 'rgb(255, 0, 0)', 0.1) : {},
			data["PortfolioPerformance"] ? formatGraphData('Portfolio', Object.values(data["PortfolioPerformance"]), null, false, 'rgb(0, 0, 255)', 0.1) : {}
		]
	};

	const monthGraphData = {
		labels: getFinalThirtyEntries(labels),
		datasets: [
			data["CurrentHoldings"] ? formatGraphData('Current holdings', Object.values(data["CurrentHoldings"]), getFinalThirtyEntries, false, 'rgb(0, 255, 0)', 0.1) : {},
			data["SPY500"] ? formatGraphData('SPY 500', Object.values(data["SPY500"]), getFinalThirtyEntries, false, 'rgb(255, 0, 0)', 0.1) : {},
			data["PortfolioPerformance"] ? formatGraphData('Portfolio', Object.values(data["PortfolioPerformance"]), getFinalThirtyEntries, false, 'rgb(0, 0, 255)', 0.1) : {}
		]
	};

	const yearConfig = {
		type: 'line',
		data: yearGraphData,
	};
	const monthConfig = {
		type: 'line',
		data: monthGraphData,
	};


	charts.forEach(function(chart){
		chart.destroy();
	});    

	charts.push(new Chart(yearPerformanceChartContainer, yearConfig));
	charts.push(new Chart(monthPerformanceChartContainer, monthConfig));
}

getData();