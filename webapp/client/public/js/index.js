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

new Vue({
	el: '#triggerPanel',
	data() {
		return {
			responseMessage: "",
			running: false,
			startTime: null,
			originalSpinnerParentClass: "col-sm-6 col-xl-4",
			spinnerParentClass: this.originalSpinnerParentClass
		}
	},
	methods: {
		runInvestmentBalancer: function (){
			console.log("runInvestmentBalancer called.")
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
	let dataLength;

	//assert all the lists in the data dict are the same length

	for(let i = 0; i < dataKeys.length; i++)
	{
		if(!dataLength)
		{
			dataLength = data[dataKeys[i]].length; // init dataLength
			continue;
		}

		currentDataItemLength = data[dataKeys[i]].length
		if(currentDataItemLength != dataLength);
		console.log(`Data is not uniform, one list has ${dataLength} elements, another has ${currentDataItemLength} elements`)
		return true;
	}
	return false;
}

// translate this function to be vue compatible
function buildChart(data){

	const ctx = document.getElementById('performanceChart');
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

	const graphData = {
		labels: labels,
		datasets: [{
			label: 'Current holdings',
			data: Object.values(data["CurrentHoldings"]),
			fill: false,
			borderColor: 'rgb(0, 255, 0)',
			tension: 0.1
		},
		{
			label: 'SPY 500',
			data: Object.values(data["SPY500"]),
			fill: false,
			borderColor: 'rgb(255, 0, 0)',
			tension: 0.1
		},
		{
			label: 'Portfolio',
			data: Object.values(data["PortfolioPerformance"]),
			fill: false,
			borderColor: 'rgb(0, 0, 255)',
			tension: 0.1
		}]
	};

	const config = {
		type: 'line',
		data: graphData,
	};

	new Chart(ctx, config);
}

getData();