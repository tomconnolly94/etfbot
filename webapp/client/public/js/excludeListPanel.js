//////////////////////////////////////////////////////////////////////
//
// filename: excludeListPanel.js
// author: Tom Connolly
// description: Contains excludeListPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////

new Vue({
	el: '#excludeListPanel',
	data() {
		return {
			stocks: [],
			newExcludeListStockSymbol: "",
			excludeReason: "immoral"
		}
	},
	beforeMount() {
		this.reloadExcludeList();
	},
	methods: {
		reloadExcludeList(){
			this.stocks = [];
			axios.get(`/excludeList`).then((response) => {
				for(const stockRecord of response.data)
				{
					this.stocks.push({
						symbol: stockRecord["symbol"],
						companyName: stockRecord["companyName"],
						reason: stockRecord["reason"]
					})
				}
			}).catch(function(error){
				console.log(`Failed to retrieve excludeList error: ${error}`);
			});
		},
		removeExcludeListItem(stockForRemoval) {
			const stockSymbolForRemoval = stockForRemoval.stock["symbol"]
			for(let index = 0; index < this.stocks.length; index++)
			{
				const stockSymbol = this.stocks[index]["symbol"];
				if(stockSymbol == stockSymbolForRemoval)
				{
					axios.delete(`/excludeList/${stockSymbolForRemoval}`).then((response) => {
						this.stocks.splice(index, 1);
					}).catch(function(error){
						console.log(`Failed to remove item from excludeList error: ${error}`);
					});
				}
			}
		},
		addExcludeListItem(){
			
			if(!this.excludeReason)
			{
				console.log(`Please select an "excludeReason"`);
				return;
			}

			let vueComponent = this;
			// add symbol
			axios.post(`excludeList/${this.newExcludeListStockSymbol}`, null, { params: {
				reason: this.excludeReason
			}}).then((response) => {
				vueComponent.reloadExcludeList();
				console.log(`Successfully added ${vueComponent} to excludeList, and reloaded the list to the UI`);
			}).catch(function(error){
				console.log(`Failed to add to excludeList, error: ${error}`);
			});
		}
	}
});