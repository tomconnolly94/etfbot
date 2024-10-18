//////////////////////////////////////////////////////////////////////
//
// filename: transactionPanel.js
// author: Tom Connolly
// description: Contains transactionPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////

new Vue({
	el: '#transactionPanel',
	data() {
		return {
			orderData: [],
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
				if(finalOrder["orderType"] == "BUY" && false){
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
		processOrderData: async function()
		{
			console.log(this.showStockBuySellChart)
			console.log(1, this.orderDataSelectedSymbol)
			this.orderDataProfitLossMessages = [];

			if(this.orderDataSelectedSymbol != "all")
			{
				this.showStockBuySellChart = true;
				this.createMessagesFromOrderData([this.orderDataSelectedSymbol]);
				const orders = this.orderData[this.orderDataSelectedSymbol];
				this.buildStockBuySellChart(orders);
			}
			else
			{
				this.showStockBuySellChart = false;
				this.createMessagesFromOrderData(this.symbols);
			}
			console.log(2, this.orderDataSelectedSymbol)
			this.calculateCurrentCapitalGains();
			console.log(3, this.orderDataSelectedSymbol)
			console.log(this.showStockBuySellChart)
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
	
		},
		getSymbolOrderInfo: function()
		{
			const vueComponent = this;
			axios.get(`/symbolOrderInfo`).then((response) => {
				this.orderData = response.data;
				this.symbols = Object.keys(this.orderData);
				vueComponent.processOrderData();
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
		const vueComponent = this;

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
