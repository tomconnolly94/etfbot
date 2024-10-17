//////////////////////////////////////////////////////////////////////
//
// filename: index.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////

// const vars
var charts = [];


new Vue({
	el: '#displayPanel',
	data() {
		return {
			monthPerformanceChartDataPanelMessages: [],
			yearPerformanceChartDataPanelMessages: [],
			orderData: [],
			orderDataProfitLossMessages: [],
			orderDataSelectedSymbol: "all",
			stockBuySellChart: null,
			symbols: [],
			totalCapitalGainsLiability: 0,
			dateRangeModel: "2024-04-01",
			availableTaxYears: [],
			availableTaxYearDates: {},
			earliestYearForCGT: null,
			latestYearForCGT: null
		}
	},
	methods: {
		dataIsMalformed: function(data) // perform very basic data validation
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
				let dataPack = data[dataKeys[i]];
		
				if(typeof dataPack != 'object')
				{
					console.log(`${dataPack} is not an object`)
					return true;
				}
		
				let dataPackValues = data[dataKeys[i]]["values"];
		
				if(typeof dataPackValues != 'object' )
				{
					console.log(`${dataPackValues} is not an object`)
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
					console.log(`Data is not uniform, some datasets in ${JSON.stringify(data)} were not the same length.`)
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
			vueComponent = this;
			const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
			const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
			const labels = [];
			const dates = Object.keys(data["PortfolioPerformance"]["values"]); // SPY500 is the most consistently available data

			for(let i = 0; i < 365; i++)
			{
				// let dateParts = new Date(dataKeys[i]*1000).toUTCString().split(" ");
				// let date = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]}`
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

			const yearConfig = {
				type: 'line',
				data: yearGraphData,
				options: {
					spanGaps: true
				}
			};
			const monthConfig = {
				type: 'line',
				data: monthGraphData,
				options: {
					spanGaps: true
				}
			};


			charts.forEach(function(chart){
				chart.destroy();
			});

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
		updateOrderDataSelectedSymbol: function(event)
		{
			this.orderDataSelectedSymbol = event.target.options[event.target.options.selectedIndex].text
			this.getOrderData();
		},
		createMessagesFromOrderData: async function(symbols)
		{
			let totalPL = 0;
			let allOrders = [];

			for(let symbolIndex = 0; symbolIndex < symbols.length; symbolIndex++)
			{
				let symbol = symbols[symbolIndex];
				let orders = this.orderData[symbol];
				allOrders.concat(orders);
				const finalOrder = orders[orders.length - 1];

				// if the final order is a BUY, get the current value of the stock
				if(finalOrder["orderType"] == "BUY"){
					const ownedQuantity = finalOrder["quantity"]
					// if we still own the stock we make a request to get its current value
					let response = await axios.get(`/currentPrice/${symbol}`);

					const stockData = response.data;
						
					orders.push({
						"symbol": stockData["symbol"],
						"price": stockData["price"],
						"orderType": "CURRENT PRICE",
						"quantity": ownedQuantity,
						"filledDate": new Date().toLocaleDateString()
					});
					totalPL += this.processSymbolOrders(orders);
				}
				else
					totalPL += this.processSymbolOrders(orders);
			}
			this.orderDataProfitLossMessages.push(`Total P/L: ${totalPL.toFixed(2)}`);
		},
		processSymbolOrders: function(orders)
		{
			let symbolPL = 0;

			for(let orderIndex = 0; orderIndex < orders.length; orderIndex++)
			{
				const order = orders[orderIndex];

				let orderMessage = `${order["orderType"]} ${order["symbol"]} `;
				if(order["orderType"] == "BUY" )
				{
					orderMessage += `-${order["price"]} (${order["price"]}x${order["quantity"]})`;
					symbolPL -= Number(order["price"]) * order["quantity"];
				}
				else if(order["orderType"] == "SELL" || order["orderType"] == "CURRENT PRICE")
				{
					orderMessage += `+${order["price"]} (${order["price"]}x${order["quantity"]})`;
					symbolPL += Number(order["price"]) * order["quantity"];
					if(order["orderType"] == "SELL" && symbolPL > 0)
						orderMessage += ` - Capital gains liability: ${symbolPL.toFixed(2)}`
				}
				this.orderDataProfitLossMessages.push(orderMessage);
			}
			return symbolPL;
		},
		calculateCurrentCapitalGains: function()
		{
			this.totalCapitalGainsLiability = 0;
			// loop grouped orders and for any sell orders calculate the capital gains liability
			let symbols = Object.keys(this.orderData);


			for(let symbolIndex = 0; symbolIndex < symbols.length; symbolIndex++)
			{
				let symbol = symbols[symbolIndex];
				let orders = this.orderData[symbol];
				let stockPL = 0;
				let earliestTimestampForCGT = new Date(this.earliestYearForCGT, 3, 6).getTime();
				let latestTimestampForCGT = new Date(this.latestYearForCGT, 3, 5).getTime();
				
				for(let orderIndex = 0; orderIndex < orders.length; orderIndex++)
				{
					let order = orders[orderIndex];
					if(order["orderType"] == "BUY" )
						stockPL -= Number(order["price"]) * order["quantity"];
					else if(order["orderType"] == "SELL")
					{
						let splitDate = order["filledDate"].split("/");
						let orderTimestamp = new Date(splitDate[2], Number(splitDate[1]) - 1, splitDate[0]).getTime();

						// skip any sell orders outside of the relevant tax year
						if(orderTimestamp < earliestTimestampForCGT || orderTimestamp > latestTimestampForCGT)
							continue;


						stockPL += Number(order["price"]) * order["quantity"];
						
						if(stockPL > 0)
						{
							// add the capital gains liability for this sale to the total and reset 
							this.totalCapitalGainsLiability += stockPL;
							stockPL = 0; // this assumes that when we sell, we sell everything we own of this stock
						}
					}
				}
			}
			this.totalCapitalGainsLiability = this.totalCapitalGainsLiability.toFixed(2);
		},
		getOrderData: async function()
		{
			this.orderDataProfitLossMessages = [];

			if(this.orderDataSelectedSymbol != "all")
			{
				this.createMessagesFromOrderData([this.orderDataSelectedSymbol]);
				const orders = this.orderData[this.orderDataSelectedSymbol];
				this.buildStockBuySellChart(orders);
			}
			else
			{
				this.createMessagesFromOrderData(this.symbols);
				this.buildStockBuySellChart([]);
			}
			this.calculateCurrentCapitalGains();
		},
		buildStockBuySellChart: function(orders)
		{
			// destroy the existing chart
			if(this.stockBuySellChart)
				this.stockBuySellChart.destroy();

			if(orders.length < 1)
				return;

			const stockBuySellChartContainer = document.getElementById('stockBuySellChart');
			let labels = [];
			let prices = [];

			for(let i = 0; i < orders.length; i++)
			{
				let order = orders[i];
				labels.push(order["filledDate"] + " - " + order["orderType"]);
				prices.push(order["price"]);
			}

			const graphData = {
				labels: labels,
				datasets: [{
					label: this.orderDataSelectedSymbol,
					data: prices,
					fill: false,
					borderColor: 'rgb(255, 0, 0)',
					tension: 0.1
				}]
			};

			const graphConfig = {
				type: 'line',
				data: graphData,
				options: {
					spanGaps: true
				}
			};
			console.log(graphConfig);
			
			if(this.stockBuySellChart)
				this.stockBuySellChart.destroy();

			this.stockBuySellChart = new Chart(stockBuySellChartContainer, graphConfig);
	
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
		getSymbolOrderInfo: function()
		{
			vueComponent = this;
			axios.get(`/symbolOrderInfo`).then((response) => {
				this.orderData = response.data;
				this.symbols = Object.keys(this.orderData);
				vueComponent.getOrderData();
			});
		},
		updateSymbolOrderInfo: function(event)
		{
			let years = event.target.value.split("/");
			this.earliestYearForCGT = years[0];
			this.latestYearForCGT = years[1];
			this.getSymbolOrderInfo();
		}
	},
	beforeMount() {
		vueComponent = this;
		axios.get(`/getInvestmentPerformanceData`).then((response) => {

			let data = response.data;

			if(vueComponent.dataIsMalformed(data))
				return;

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

		// calculate tax years, earliest tax year should be 23/24, latest should be the current tax year
		let earliestTaxYear = 2023;
		let currentDate = new Date();
		let thisTaxYearThreshold = new Date(currentDate.getFullYear(), 4, 5);
		let latestTaxYear = currentDate <= thisTaxYearThreshold ? currentDate.getFullYear() : currentDate.getFullYear() + 1;

		for(let currentTaxStartYear = earliestTaxYear; currentTaxStartYear < latestTaxYear; currentTaxStartYear++)
		{	
			vueComponent.availableTaxYearDates[`${currentTaxStartYear}/${currentTaxStartYear + 1}`] = {
				earliestTimestamp: new Date(currentTaxStartYear, 3, 5).getTime(),
				latestTimestamp: new Date(currentTaxStartYear + 1, 3, 6).getTime()
			};
		};
		vueComponent.availableTaxYears = Object.keys(vueComponent.availableTaxYearDates).reverse();		
		vueComponent.earliestYearForCGT = latestTaxYear - 1;
		vueComponent.latestYearForCGT = latestTaxYear;
		vueComponent.getSymbolOrderInfo();
	}
});
