//////////////////////////////////////////////////////////////////////
//
// filename: transactionPanel.js
// author: Tom Connolly
// description: Contains transactionPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////

var charts = [];

// vanilla javascript to destroy charts on page close/reload
window.addEventListener("beforeunload", function(e){
	for(let chartIndex = 0; chartIndex < charts.length; chartIndex++)
		charts[chartIndex].destroy();
	charts = [];
});



new Vue({
	el: '#transactionPanel',
	data() {
		return {
			orderData: {},
			orderDataProfitLossMessages: [],
			orderDataSelectedSymbol: "all",
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
		updateOrderDataSelectedSymbol: function()
		{
			this.processOrderData();
		},
		addCurrentPricesToOrderData: async function()
		{
			const vueComponent = this;
			this.orderDataProfitLossMessages = [];
			const symbols = Object.keys(this.orderData);
			let httpPromises = []

			for(let symbolIndex = 0; symbolIndex < symbols.length; symbolIndex++)
			{
				let symbol = symbols[symbolIndex];
				let orders = this.orderData[symbol];
				const finalOrder = orders[orders.length - 1];

				// if the final order is a BUY, get the current value of the stock
				if(finalOrder["orderType"] == "BUY")
					httpPromises.push(axios.get(`/currentPrice/${symbol}`));
			}

			await Promise.all(httpPromises).then((responses) => {
				
				responses.forEach((response) => {

					const stockData = response.data;
					let symbol = stockData["symbol"];

					if(!(symbol in vueComponent.orderData))
					{
						console.log(`ERROR: ${symbol} not found in vueComponent.orderData`);
						return;
					}

					let orders = this.orderData[symbol];
					const finalOrder = orders[orders.length - 1];
					const ownedQuantity = finalOrder["quantity"]

					vueComponent.orderData[symbol].push({
						"symbol": symbol,
						"price": stockData["price"],
						"orderType": "CURRENT PRICE",
						"quantity": ownedQuantity,
						"filledDate": new Date().toLocaleDateString()
					});
				});					
			});
		},
		getPLDataFromSymbolOrders: function(orders)
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

			this.stockBuySellChart = new Chart(stockBuySellChartContainer, graphConfig);
			charts.push(this.stockBuySellChart);	
		},
		processOrderData: function(){

			let symbols = [];

			if(this.orderDataSelectedSymbol != "all")
			{
				symbols.push(this.orderDataSelectedSymbol);
				const orders = this.orderData[this.orderDataSelectedSymbol];
				this.buildStockBuySellChart(orders);
			}
			else
				symbols = Object.keys(this.orderData);

			// now calculate totalPL generating order messages for each order
			let totalPL = 0;
			this.orderDataProfitLossMessages = []; // empty the list

			for(let symbolIndex = 0; symbolIndex < symbols.length; symbolIndex++)
			{
				let symbol = symbols[symbolIndex];
				let orders = this.orderData[symbol];
				totalPL += this.getPLDataFromSymbolOrders(orders);
			}
			this.orderDataProfitLossMessages.push(`Total P/L: ${totalPL.toFixed(2)}`);

			// finally calculate capital gains tax for the selected tax year
			this.calculateCurrentCapitalGains();
		},
		getSymbolOrderInfo: function()
		{
			const vueComponent = this;
			axios.get(`/symbolOrderInfo`).then(async (response) => {
				vueComponent.orderData = response.data;
				vueComponent.symbols = Object.keys(this.orderData);
				await vueComponent.addCurrentPricesToOrderData();
				vueComponent.processOrderData();
			});
		},
		updateSymbolOrderInfo: function(event)
		{
			let years = event.target.value.split("/");
			this.earliestYearForCGT = years[0];
			this.latestYearForCGT = years[1];
			this.processOrderData();
		}
	},
	async beforeMount() {
		const vueComponent = this;

		// calculate tax years, earliest tax year should be 2023/2024, latest should be the current tax year
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
		await vueComponent.getSymbolOrderInfo();
	}
});
